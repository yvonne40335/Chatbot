import sys
from io import BytesIO

import telegram
from flask import Flask, request, send_file

from fsm import TocMachine


API_TOKEN = '328696297:AAHLp_wsUbAp2rkgdQRgRXPMmcyEeU4HvVg'
WEBHOOK_URL = 'https://ccb1dac2.ngrok.io/hook'

app = Flask(__name__)
bot = telegram.Bot(token=API_TOKEN)
machine = TocMachine(
    states=[
        'user',
        'state1',
        'state2',
        'state3',
        'character',
        'category',
        'final1',
        'movie',
        'description',
        'final2',
        'loveline',
        'final3',
        'garbage'
    ],
    transitions=[
        {
            'trigger': 'advance',
            'source': 'user',
            'dest': 'state1',
            'conditions': 'is_going_to_state1'
        },
        {
            'trigger': 'advance',
            'source': 'user',
            'dest': 'state2',
            'conditions': 'is_going_to_state2'
        },
        {
            'trigger': 'advance',
            'source': 'user',
            'dest': 'state3',
            'conditions': 'is_going_to_state3'
        },
        {
            'trigger': 'advance',
            'source': 'state1',
            'dest': 'category',
            'conditions': 'is_going_to_category'
        },
        {
            'trigger': 'advance',
            'source': 'category',
            'dest': 'character',
            'conditions': 'is_going_to_character'
        },
        {
            'trigger': 'advance',
            'source': 'character',
            'dest': 'final1',
            'conditions': 'is_going_to_final1'
        },
        {
            'trigger': 'advance',
            'source': 'character',
            'dest': 'character',
            'conditions': 'is_going_to_character'
        },
        {
            'trigger': 'advance',
            'source': 'state2',
            'dest': 'movie',
            'conditions': 'is_going_to_movie'
        },
        {
            'trigger': 'advance',
            'source': 'movie',
            'dest': 'description',
            'conditions': 'is_going_to_description'
        },
        {
            'trigger': 'advance',
            'source': 'description',
            'dest': 'final2',
            'conditions': 'is_going_to_final2'
        },
        {
            'trigger': 'advance',
            'source': 'description',
            'dest': 'description',
            'conditions': 'is_going_to_description'
        },
        {
            'trigger': 'advance',
            'source': 'state3',
            'dest': 'loveline',
            'conditions': 'is_going_to_loveline'
        },
        {
            'trigger': 'advance',
            'source': 'loveline',
            'dest': 'final3',
            'conditions': 'is_going_to_final3'
        },
        {
            'trigger': 'advance',
            'source': 'loveline',
            'dest': 'loveline',
            'conditions': 'is_going_to_loveline'
        },
        {
            'trigger': 'advance',
            'source': 'user',
            'dest': 'garbage',
            'conditions': 'is_going_to_garbage'
        },
        {
            'trigger': 'go_back',
            'source': [
                'final1',
                'final2',
                'final3',
                'garbage'
            ],
            'dest': 'user'
        },
        {
            'trigger': 'go_back',
            'source': 'category',
            'dest': 'garbage'
        },
        {
            'trigger': 'go_back',
            'source': 'character',
            'dest': 'state1'
        },
        {
            'trigger': 'go_back',
            'source': 'movie',
            'dest': 'garbage'
        },
        {
            'trigger': 'go_back',
            'source': 'description',
            'dest': 'state2'
        },
        {
            'trigger': 'go_back',
            'source': 'loveline',
            'dest': 'garbage'
        }
    ],
    initial='user',
    auto_transitions=False,
    show_conditions=True,
)


def _set_webhook():
    status = bot.set_webhook(WEBHOOK_URL)
    if not status:
        print('Webhook setup failed')
        sys.exit(1)
    else:
        print('Your webhook URL has been set to "{}"'.format(WEBHOOK_URL))


@app.route('/hook', methods=['POST'])
def webhook_handler():
    update = telegram.Update.de_json(request.get_json(force=True), bot)
    machine.advance(update)
    return 'ok'


@app.route('/show-fsm', methods=['GET'])
def show_fsm():
    byte_io = BytesIO()
    machine.graph.draw(byte_io, prog='dot', format='png')
    byte_io.seek(0)
    return send_file(byte_io, attachment_filename='fsm.png', mimetype='image/png')


if __name__ == "__main__":
    _set_webhook()
    app.run()
