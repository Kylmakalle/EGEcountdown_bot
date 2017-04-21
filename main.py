import datetime
import json
import logging
import sys
import urllib

import urllib2

reload(sys)
sys.setdefaultencoding('utf-8')
# standard app engine imports
from google.appengine.api import urlfetch
from google.appengine.ext import ndb
import webapp2

TOKEN = '******'

BASE_URL = 'https://api.telegram.org/bot' + TOKEN + '/'


# ================================

class EnableStatus(ndb.Model):
    # key name: str(chat_id)
    enabled = ndb.BooleanProperty(indexed=False, default=False)


# ================================

def setEnabled(chat_id, yes):
    es = EnableStatus.get_or_insert(str(chat_id))
    es.enabled = yes
    es.put()


def getEnabled(chat_id):
    es = EnableStatus.get_by_id(str(chat_id))
    if es:
        return es.enabled
    return False


# ================================

class MeHandler(webapp2.RequestHandler):
    def get(self):
        urlfetch.set_default_fetch_deadline(60)
        self.response.write(json.dumps(json.load(urllib2.urlopen(BASE_URL + 'getMe'))))


class GetUpdatesHandler(webapp2.RequestHandler):
    def get(self):
        urlfetch.set_default_fetch_deadline(60)
        self.response.write(json.dumps(json.load(urllib2.urlopen(BASE_URL + 'getUpdates'))))


class SetWebhookHandler(webapp2.RequestHandler):
    def get(self):
        urlfetch.set_default_fetch_deadline(60)
        url = self.request.get('url')
        if url:
            self.response.write(
                json.dumps(json.load(urllib2.urlopen(BASE_URL + 'setWebhook', urllib.urlencode({'url': url})))))


FMT = "%d.%m.%Y %H:%M"
rus = datetime.datetime.strptime("09.06.2017 10:00", FMT)
math = datetime.datetime.strptime("02.06.2017 10:00", FMT)
phys = datetime.datetime.strptime("07.06.2017 10:00", FMT)
it = datetime.datetime.strptime("29.05.2017 10:00", FMT)


class WebhookHandler(webapp2.RequestHandler):
    def post(self):
        urlfetch.set_default_fetch_deadline(60)
        body = json.loads(self.request.body)
        logging.info('request body:')
        logging.info(body)
        self.response.write(json.dumps(body))

        update_id = body['update_id']
        try:
            message = body['message']
        except:
            message = body['edited_message']
        message_id = message.get('message_id')
        date = message.get('date')
        text = message.get('text')
        fr = message.get('from')
        chat = message['chat']
        chat_id = chat['id']

        if not text:
            logging.info('no text')
            return

        def reply(msg=None, img=None):
            if msg:
                resp = urllib2.urlopen(BASE_URL + 'sendMessage', urllib.urlencode({
                    'chat_id': str(chat_id),
                    'text': msg.encode('utf-8'),
                    'disable_web_page_preview': 'true',
                    'reply_to_message_id': str(message_id),
                })).read()
            elif img:
                resp = multipart.post_multipart(BASE_URL + 'sendPhoto', [
                    ('chat_id', str(chat_id)),
                    ('reply_to_message_id', str(message_id)),
                ], [
                                                    ('photo', 'image.jpg', img),
                                                ])
            else:
                logging.error('no msg or img specified')
                resp = None

            logging.info('send response:')
            logging.info(resp)

        if text.startswith('/'):
            if text == '/start':
                reply('Bot enabled')
                #setEnabled(chat_id, True)
            elif text == '/stop':
                reply('Bot disabled')
                #setEnabled(chat_id, False)
            elif '/rus' in text:
                now = datetime.datetime.now()
                drus = rus - now
                reply("До Русича осталось {} дней, {} часов {} минут {} секунд.".format(drus.days,
                                                                                        drus.seconds // 3600,
                                                                                        drus.seconds % 3600 // 60,
                                                                                        drus.seconds % 60))
            elif '/math' in text:
                now = datetime.datetime.now()
                dmath = math - now
                reply("До Матеши осталось {} дней, {} часов {} минут {} секунд.".format(dmath.days,
                                                                                        dmath.seconds // 3600,
                                                                                        dmath.seconds % 3600 // 60,
                                                                                        dmath.seconds % 60))
            elif '/phys' in text:
                now = datetime.datetime.now()
                dphys = phys - now
                reply("До Физеки осталось {} дней, {} часов {} минут {} секунд.".format(dphys.days,
                                                                                        dphys.seconds // 3600,
                                                                                        dphys.seconds % 3600 // 60,
                                                                                        dphys.seconds % 60))
            elif '/ikt' in text:
                now = datetime.datetime.now()
                dit = it - now
                reply("До ИКТ осталось {} дней, {} часов {} минут {} секунд.".format(dit.days,
                                                                                     dit.seconds // 3600,
                                                                                     dit.seconds % 3600 // 60,
                                                                                     dit.seconds % 60))

        # CUSTOMIZE FROM HERE

        elif 'who are you' in text:
            reply('@EGEcountdown_bot, created by Kylmakalle: https://github.com/Kylmakalle/EGEcountdown_bot')
        else:
            if getEnabled(chat_id):
                reply('I got your message! (but I do not know how to answer)')
            else:
                logging.info('not enabled for chat_id {}'.format(chat_id))


app = webapp2.WSGIApplication([
    ('/me', MeHandler),
    ('/updates', GetUpdatesHandler),
    ('/set_webhook', SetWebhookHandler),
    ('/webhook', WebhookHandler),
], debug=True)
