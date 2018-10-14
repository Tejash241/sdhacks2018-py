from flask import Flask, render_template, flash, redirect, session, url_for, request, g, jsonify
from app import app
import os.path
from flask.ext.autoindex import AutoIndex
import py_010_webhook_lib

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title='Home - Webhook--Python')

@app.route('/sent')
def sent():
    r = py_010_webhook_lib.send()
    return render_template('sent.html', title='Sent - Webhook--Python', data=r)

@app.route('/webhook', methods=['POST'])
def webhook():
    r = py_010_webhook_lib.webhook_listener()
    return render_template('webhook.html')

# Custom indexing of /files
files_index = AutoIndex(app, os.path.curdir + '/app/files/', add_url_rules=False)
# The request must provide the directory name one down from /files
@app.route('/files/<path:path>')
def autoindex(path):
    return files_index.render_autoindex(path)


@app.route('/receive')
def received():
	py_010_webhook_lib.webhook_listener()
	return render_template('sent.html', title='Received - Webhook--Python', data={"html":"nothing here"})

################################################################################
################################################################################

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

