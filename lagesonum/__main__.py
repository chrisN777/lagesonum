# coding: utf-8

# Datei zum lokalen testen, PythonAnywhere verwendet bottle_app.py direkt

from bottle import run, debug

from bottle_app import application

debug(False)
run(application, host='127.0.0.1', port=8080, reloader=True)
