# coding: utf-8

import sys

import os
import uuid
import json
from PIL import Image
import io
import requests
from flask import Flask, request, abort, send_file

from linebot import (
    LineBotApi, WebhookHandler,
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, ImageMessage, VideoMessage, TextSendMessage, AudioMessage, StickerSendMessage, AudioSendMessage
)

from pydub import AudioSegment
import ffmpeg

import argparse
import io

from google.cloud import storage

app = Flask(__name__, static_folder='namari')
port = int(3000)


CHANNEL_SECRET = '2391b5a9f6617b874dac8df9518690ac'

CHANNEL_ACCESS_TOKEN = 'SyR0KJcIbZivQpl0XvPTtsnC+P+XSYP/1dQH2AywHbbAg2pTeApw8KEMSjOz7/oT7Q+8k0QxaUcQOSeCFCpcW3tpid9AKXW5E4sNgQSN1vjfiZX5uU+BQHFb3IS060vy440Ge3ooOGN3ALm7W7if0AdB04t89/1O/w1cDnyilFU='

line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

@app.route("/", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']

    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    text = event.message.text

    print('event.message.text =', event.message.text)

    #------------------------
    #textReplace!
    with open("geek.json", 'r') as outfile:
        data = json.load(outfile)

    s = text

    keys = data.keys()
    values = data.values()

    for key,value in zip(keys,values):
        if key in s:
            s = s.replace(key, value)

    with open("gobi.json", 'r') as outfile:
        data = json.load(outfile)

    keys = data.keys()
    values = data.values()

    for key,value in zip(keys,values):
        if key in s:
            s = s.replace(key, value)
    print(s)

    text = s

    #------------------------

    #------------------------
    #voiceroid!
    #あかねちゃん
    speaker = 'akane_west'

#    speak_text = text
#    text = "<voice name=\"" + speaker + "\">" + speak_text + "</voice>"

    data = {
        "username": 'MA2017',
        "password": 'MnYrnxhH',
        "ext": 'aac',
        "text": text,
        "speaker_name": speaker,
        "range": 1.8
        }

    r = requests.post('http://webapi.aitalk.jp/webapi/v2/ttsget.php', params=data)

    if not os.path.exists('namari'):
        os.makedirs('namari')

    dataPath = 'namari/{}.m4a'.format('message')
    print(dataPath)
    f = open(dataPath, 'wb')
    f.write(r.content)
    f.close()

    #------------------------
    storage_client = storage.Client()


    audio_Kansai = AudioSegment.from_file(dataPath, format='m4a')
    duration = int(audio_Kansai.duration_seconds * 1000)

    print(type(dataPath))
    print(duration,(type(duration)))

    audioURL = 'https://d9489ca9.ngrok.io/' + dataPath

    response = line_bot_api.reply_message(
        event.reply_token, [
            TextSendMessage(text=text),
            AudioSendMessage(original_content_url=audioURL, duration=duration)
            ]
    )

@handler.add(MessageEvent, message=AudioMessage)
def handle_content_message(event):
    if isinstance(event.message, ImageMessage):
        ext = 'jpg'
    elif isinstance(event.message, VideoMessage):
        ext = 'mp4'
    elif isinstance(event.message, AudioMessage):
        ext = 'm4a'
    else:
        return

    message_content = line_bot_api.get_message_content(event.message.id)
    dirname = 'tmp'
    fileName = uuid.uuid4().hex
    if not os.path.exists(dirname):
        os.makedirs(dirname)
    with open("tmp/{}.m4a".format(fileName), 'wb') as audio:
        audio.write(message_content.content)

    AudioSegment.converter = "/usr/bin/ffmpeg"
    flac_audio = AudioSegment.from_file("tmp/{}.m4a".format(fileName), format='m4a')
    flac_audio.export("tmp/{}.flac".format(fileName), format="flac")
    text = transcribe_file("tmp/{}.flac".format(fileName))

    #------------------------
    #textReplace!
    with open("geek.json", 'r') as outfile:
        data = json.load(outfile)
    baseText = text
    s = text

    keys = data.keys()
    values = data.values()

    for key,value in zip(keys,values):
        if key in s:
            s = s.replace(key, value)

    with open("gobi.json", 'r') as outfile:
        data = json.load(outfile)

    keys = data.keys()
    values = data.values()

    for key,value in zip(keys,values):
        if key in s:
            s = s.replace(key, value)
    print(s)

    text = s

    #------------------------

    #------------------------
    #voiceroid!
    #あかねちゃん
    speaker = 'akane_west'

#    speak_text = text
#    text = "<voice name=\"" + speaker + "\">" + speak_text + "</voice>"

    data = {
        "username": 'MA2017',
        "password": 'MnYrnxhH',
        "ext": 'aac',
        "text": text,
        "speaker_name": speaker,
        "range": 1.8
        }

    r = requests.post('http://webapi.aitalk.jp/webapi/v2/ttsget.php', params=data)

    if not os.path.exists('namari'):
        os.makedirs('namari')

    dataPath = 'namari/{}.m4a'.format(fileName)
    print(dataPath)
    f = open(dataPath, 'wb')
    f.write(r.content)
    f.close()

    #------------------------
    storage_client = storage.Client()


    audio_Kansai = AudioSegment.from_file(dataPath, format='m4a')
    duration = int(audio_Kansai.duration_seconds * 1000)

    print(type(dataPath))
    print(duration,(type(duration)))

    audioURL = 'https://d9489ca9.ngrok.io/' + dataPath

    response = line_bot_api.reply_message(
        event.reply_token, [
            TextSendMessage(text=baseText),
            TextSendMessage(text=text),
            AudioSendMessage(original_content_url=audioURL, duration=duration)
        ]
    )

def transcribe_file(speech_file):
    """Transcribe the given audio file."""
    from google.cloud import speech
    from google.cloud.speech import enums
    from google.cloud.speech import types
    client = speech.SpeechClient()

    # [START migration_sync_request]
    # [START migration_audio_config_file]
    with io.open(speech_file, 'rb') as audio_file:
        content = audio_file.read()

    audio = types.RecognitionAudio(content=content)
    config = types.RecognitionConfig(
        #encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
        encoding=enums.RecognitionConfig.AudioEncoding.FLAC,
        #sample_rate_hertz=16000,
        #language_code='en-US')
        language_code='ja-JP')
    # [END migration_audio_config_file]

    # [START migration_sync_response]
    response = client.recognize(config, audio)
    # [END migration_sync_request]
    # Each result is for a consecutive portion of the audio. Iterate through
    # them to get the transcripts for the entire audio file.
    for result in response.results:
        # The first alternative is the most likely one for this portion.
        # print('聞き取った単語：'.decode('utf-8'), result.alternatives[0].decode('utf-8'))

        word = response.results[0].alternatives[0].transcript
        word = word.encode('utf-8')

        print('Transcript:', word)
        return response.results[0].alternatives[0].transcript

    return '聞き取れませんでした'


if __name__ == "__main__":
    app.debug = True
    app.run(host='localhost', port = port)
