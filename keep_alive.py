from flask import Flask, request, abort
import os

server = Flask(__name__)

@server.route('/')
def home():
    return "Bot is running! ✅"

def init_webhook(bot_instance, webhook_url):
    token = bot_instance.token

    @server.route('/' + token, methods=['POST'])
    def webhook():
        import telebot
        if request.headers.get('content-type') == 'application/json':
            json_str = request.get_data(as_text=True)
            update = telebot.types.Update.de_json(json_str)
            bot_instance.process_new_updates([update])
            return ''
        else:
            abort(403)

    bot_instance.remove_webhook()
    bot_instance.set_webhook(url=webhook_url + '/' + token)

def run_server():
    port = int(os.environ.get('PORT', 8080))
    server.run(host='0.0.0.0', port=port)

def keep_alive():
    from threading import Thread
    t = Thread(target=run_server)
    t.daemon = True
    t.start()
