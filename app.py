from flask import Flask, request, jsonify
import requests
import json
import re
import os
app = Flask(__name__)


JIRA_URL = os.environ.get('JIRA__URL')
JIRA_API_TOKEN = os.environ.get('JIRA__API__TOKEN')
JIRA_PROJECT_KEY = os.environ.get('JIRA__PROJECT__KEY')
JIRA_ISSUE_TYPE = 'Task'  # or any other issue type

# Set header parameters
headers = {
    "Authorization": "Bearer " + JIRA_API_TOKEN,
    'Content-type':'application/json',
    'Accept':'application/json'
}


def sanitize_input(input_string):
    """Sanitize input to prevent injection attacks."""
    return re.sub(r'[<>]', '', input_string)


@app.route('/grafana-webhook', methods=['POST'])
def grafana_webhook():
    data = request.json

    # Extract necessary information from Grafana alert
    alert_name = data.get('title')
    alert_message = data.get('message')

    # Validate parameters
    if not alert_name or not alert_message :
        return jsonify({"error": "Missing required parameters"}), 400
        
    # Sanitize input
    alert_name = sanitize_input(alert_name)
    alert_message = sanitize_input(alert_message)
    # alert_state = sanitize_input(alert_state)
    # Create Jira issue payload
    jira_payload = {
        "fields": {
            "project": {
                "key": JIRA_PROJECT_KEY
            },
            "summary": f"Grafana Alert: {alert_name}",
            "description": alert_message,
            "issuetype": {
                "name": JIRA_ISSUE_TYPE
            }
        }
    }
    # Make request to Jira API
    response = requests.post(
        JIRA_URL,
        data=json.dumps(jira_payload),
        headers=headers,
        verify=False,
    )

    if response.status_code == 201:
        return jsonify({"message": "Issue created successfully"})
    else:
        # return jsonify({"error": response.json()}), response.status_code
        return jsonify({"error": f"Issue NOT CREATED, RESPONSE={response}"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

