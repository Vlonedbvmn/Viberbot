from flask import Flask, request, Response
from viberbot import Api
from viberbot.api.bot_configuration import BotConfiguration
from viberbot.api.messages.text_message import TextMessage
from viberbot.api.viber_requests import ViberConversationStartedRequest
from viberbot.api.viber_requests import ViberFailedRequest
from viberbot.api.viber_requests import ViberMessageRequest
from viberbot.api.viber_requests import ViberSubscribedRequest
from viberbot.api.viber_requests.viber_request import ViberRequest


import time
import logging
import sched
import threading

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

app = Flask(__name__)


viber = Api(BotConfiguration(
  name='LaravelBot', #optional can be left empty
  #avatar='http://link-to-your/avatar.png', #optional can be left empty
  avatar='https://www.viber.com/app/uploads/Legcat.1517733927.gif', #optional can be left empty
  auth_token='47f988adc4a7d2e98098u09-6190b85cad5a2bec-2236ac21c07b5e74' #this is your token
))

@app.route('/', methods=['POST'])
def incoming():
    logger.debug("received request. post data: {0}".format(request.get_data()))
    if not viber.verify_signature(request.get_data(), request.headers.get('X-Viber-Content-Signature')):
        return Response(status=403)

    # this library supplies a simple way to receive a request object
    # эта библиотека предоставляет простой способ получения объекта запроса
    viber_request = viber.parse_request(request.get_data())


    #If comeone sents a message
    # Если кто-то отправляет сообщение
    if isinstance(viber_request, ViberMessageRequest):
        message = viber_request.message
        if message.text=="Ping":
            viber.send_messages(viber_request.sender.id, [TextMessage(text="Pong")])

    #if some one subscribes to you
    # если кто-то подписывается на вас
    elif isinstance(viber_request, ViberSubscribedRequest):
        viber.send_messages(viber_request.get_user.id, [
            TextMessage(text="thanks for subscribing stranger")
        ])

    elif isinstance(viber_request, ViberFailedRequest):
        logger.warn("client failed receiving message. failure: {0}".format(viber_request))

    return Response(status=200)


def set_webhook(viber):
    viber.set_webhook('https://b8c56eba.ngrok.io')


if __name__ == "__main__":
    scheduler = sched.scheduler(time.time, time.sleep)
    scheduler.enter(5, 1, set_webhook, (viber,))
    t = threading.Thread(target=scheduler.run)
    t.start()
    app.run(host='127.0.0.1', port=8080 , debug=True)
