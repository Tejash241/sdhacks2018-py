from flask import Flask, render_template, flash, redirect, session, url_for, request, g, jsonify
from app import app
import os.path
import requests
import json
from flask.ext.autoindex import AutoIndex
from lib_master_python import ds_recipe_lib
import py_010_webhook_lib


ds_user_email = "tvdesai@eng.ucsd.edu"
ds_user_pw = "abcd@12345"
ds_integration_id = "2b6cd4f1-36d6-4f1a-b188-420c1c76d9d0"
ds_account_id = False
webhook_path = "/webhook"

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

@app.route('/list_all_unread', methods=['POST'])
def list_all_unread():
	request_json = request.json
	print request_json
	global ds_account_id
	msg = ds_recipe_lib.init(ds_user_email, ds_user_pw, ds_integration_id, ds_account_id)
	if (msg != None):
		return {'ok': False, 'msg': msg}

	r = ds_recipe_lib.login()
	if (not r["ok"]):
		return r
	else:
		print 'login successful'

	ds_account_id = ds_recipe_lib.ds_account_id
	action_conditions = request_json['queryResult']['action']
	if action_conditions == 'email.ask': 
		api_response = requests.get("https://demo.docusign.net/restapi/v2/accounts/"+ds_account_id+"/search_folders/completed?order=desc", headers=ds_recipe_lib.ds_headers)
		# print api_response.text
		response_text = json.loads(api_response.text)
		print response_text
		pending_envelops = response_text[u'folderItems']
		pending_envelop_senders = [x["senderName"] for x in pending_envelops]
		fulfillmentText = ""
		for i, sender in enumerate(pending_envelop_senders):
			if i == 0:
				fulfillmentText += "You have one email from " + sender.split()[0]
			else:
				fulfillmentText += "one email from " + sender.split()[0]

		response = {"fulfillmentText":fulfillmentText}


	elif action_conditions == 'email.from': #read document of a particular person
		person_name = request_json['queryResult']['parameters']['name'] #some name to be inputted from Nitesh
		api_response = requests.get("https://demo.docusign.net/restapi/v2/accounts/"+ds_account_id+"/search_folders/completed?order=desc", headers=ds_recipe_lib.ds_headers)
		# print api_response.text
		response_text = json.loads(api_response.text)
		print response_text, 'ddddddddddddddddddddddddd'
		pending_envelops = response_text[u'folderItems']
		pending_envelop_senders = [x["senderName"] for x in pending_envelops]
		envelop_ids = [x["envelopeId"] for x in pending_envelops]
		fulfillmentText = ""
		for i, sender in enumerate(pending_envelop_senders):
			if person_name in sender.split():
				new_api_response = json.loads(requests.get("https://demo.docusign.net/restapi/v2/accounts/"+ds_account_id+"/envelopes/"+envelop_ids[i]+"/documents", headers=ds_recipe_lib.ds_headers).text)
				print new_api_response
				documents = new_api_response['envelopeDocuments']
				final_documents = []
				for d in documents:
					if d['documentId'] != 'certificate':
						final_documents.append(d)

				response = {"fulfillment": "There are " + str(len(final_documents)) + " documents to read"}
				break

	print response, 'sdsddddddddddddddddddddddddddd'
	response = app.response_class(
        response=json.dumps(response),
        status=200,
        mimetype='application/json'
    )
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

