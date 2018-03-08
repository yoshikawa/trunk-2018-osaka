'use strict';

const express = require('express');
const line = require('@line/bot-sdk');
const PORT = process.env.PORT || 3000;

const config = {
    channelAccessToken: 'pZPhNgEf9MgXfbl0tEHjgijZzflOGWLe9Wlf7yZaF0e6OQobs/E+BKptwbWqO7qW7Q+8k0QxaUcQOSeCFCpcW3tpid9AKXW5E4sNgQSN1vgcnxQfRrDQSdD+521xqhWwSCiInnOrA28hu2iRxEPmaAdB04t89/1O/w1cDnyilFU=',
    channelSecret: '2391b5a9f6617b874dac8df9518690ac'
};

const app = express();

app.post('/webhook', line.middleware(config), (req, res) => {
    console.log(req.body.events);
    Promise
      .all(req.body.events.map(handleEvent))
      .then((result) => res.json(result));
});

const client = new line.Client(config);

function handleEvent(event) {
  if (event.type !== 'message' || event.message.type !== 'text') {
    return Promise.resolve(null);
  }

  return client.replyMessage(event.replyToken, {
    type: 'text',
    text: event.message.text
  });
}

app.listen(PORT);
console.log(`Server running at ${PORT}`);
