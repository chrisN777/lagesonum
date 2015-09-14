# coding: utf-8

# Der WSGI-Server auf PythonAnywhere verwendet diese Datei

import sqlite3
import os
import time

import bottle
from bottle import default_app, route, view
from bottle import request
from bottle_utils.i18n import I18NPlugin
from bottle_utils.i18n import lazy_gettext as _

import input_number as ip
from dbhelper import initialize_database
import hashlib

MOD_PATH = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.abspath(os.path.join(MOD_PATH, '..', '..', "lagesonr.db"))

if not os.path.exists(DB_PATH):
    initialize_database(DB_PATH)

lagesonrdb = sqlite3.connect(DB_PATH)

LANGS = [
    ('de_DE', 'Deutsch'),
    ('en_US', 'English'),
]
# ('ar_AR', 'Arab'),
DEFAULT_LOCALE = 'en_US'


@route('/user-agent')
def user_agent():
    """
    returns an identification hash based on information from the user's browser
    :return: string
    """
    usr_agent = str(request.environ.get('HTTP_USER_AGENT'))
    usr_lang = str(request.environ.get('HTTP_ACCEPT_LANGUAGE'))
    usr_ip = str(request.remote_addr)

    usr_fingerprint = usr_agent + usr_lang + usr_ip
    usr_hash = hashlib.md5(usr_fingerprint.encode("utf-8"))

    # no return
    return ()

@route('/')
@view('start_page')
def index():
    """1.Seite: Helfer steht am LaGeSo und gibt Nummern ein [_____] """
    return {'entered': []}

@route('/', method='POST')
@view('start_page')
def do_enter():
    import pdb
    #pdb.set_trace()
    numbers = request.forms.get('numbers')
    timestamp = time.asctime()
    numbers = [num.strip() for num in numbers.split('\n')]
    result_num = []
    with lagesonrdb as con:
        cur = con.cursor()
        for num in set(numbers):
            if ip.is_valid_number(num) and ip.is_ok_with_db(
                    num) and ip.is_valid_user():
                insert = 'INSERT INTO NUMBERS(NUMBER, TIME, PLACE, USER) VALUES ("%s", "%s", "-", "-")' % (
                    num, timestamp)
                cur.execute(insert)
                result_num.append(num)
            else:
                result_num.append("INVALID INPUT: %s" % num)

    return {'entered': result_num, 'timestamp': timestamp}


@route('/query')
@view('query_page')
def query_number():
    """
    2. Seite: Flüchtling fragt ab: Wurde meine Nummer gezogen? [_____]
    => Antwort: X mal am LaGeSo eingetragen von (Erste Eintragung)
    DD.MM.YY hh bis DD.MM.YY hh (LetzteEintragung)
    application = default_app()
    """
    return {'result': '-', 'timestamp_first': '-', 'timestamp_last': '-',
            'n': '0'}


@route('/query', method='POST')
@view('query_page')
def do_query():
    number = request.forms.get('number')

    if ip.is_valid_number(number) and ip.is_ok_with_db(
            number) and ip.is_valid_user():

        with lagesonrdb as con:
            cur = con.cursor()
            query = 'SELECT TIME FROM NUMBERS WHERE NUMBER="%s" ORDER BY TIME' % number
            result = list(cur.execute(query))
            n = len(result)
            if n > 0:
                timestamp_first, timestamp_last = result[0][0], result[-1][0]
                return {'result': number, 'timestamp_first': timestamp_first,
                        'timestamp_last': timestamp_last, 'n': n}
        return {'result': 'number', 'timestamp_first': 'NOT FOUND',
                'timestamp_last': '-', 'n': '0'}

    else:
        return {"INVALID INPUT": number}


# findet templates im gleichen Verzeichnis
bottle.TEMPLATE_PATH.append(MOD_PATH)
app = default_app()
application = I18NPlugin(app, langs=LANGS, default_locale=DEFAULT_LOCALE,
                         domain='messages',
                         locale_dir=os.path.join(MOD_PATH, 'locales'))
