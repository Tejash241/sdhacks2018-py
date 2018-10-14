from flask import Flask, render_template, flash, redirect, session, url_for, request, g, jsonify
from app import app
import os.path
import requests
import json
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

@app.route('/list_all_unread')
def list_all_unread():
	api_response = requests.get("https://demo.docusign.net/restapi/v2/accounts/6807342/search_folders/awaiting_my_signature?order=desc")
	print json.loads(api_response.text)
	pending_envelops = api_response.folderItems
	pending_envelop_subjects = [x["subject"] for x in pending_envelopes]
	pending_envelop_senders = [x["senderName"] for x in pending_envelopes]
	response = {"num_envelops":len(pending_envelopes), "pending_envelops_subjects":pending_envelops_subjects, "pending_envelop_sender":pending_envelop_senders}

	return response


# @app.route('/read_document')
# def read_document(envelope_name):
# 	api_response = ...
# 	pass

################################################################################
################################################################################

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

