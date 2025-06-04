from flask import Flask, request, jsonify
import os
import json
import requests
from datetime import datetime
from app import manage_data
import logging

app = Flask(__name__)


SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN") # set this on Lamda function
HEADERS = {
    'Authorization': f'Bearer {SLACK_BOT_TOKEN}',
    'Content-Type': 'application/json',
}
logger = logging.getLogger()
logger.setLevel(logging.INFO)


# Function to track emoji reactions
@app.route('/', methods=['POST'])
def slack_event():
    data = request.json

    if 'challenge' in data:
        logger.info("Received challenge request.")
        return jsonify({'challenge': data['challenge']})
    
    response = jsonify({"status": "OK"}), 200
    
    if data.get('event', {}).get('type') == 'reaction_added':
        event = data['event']
        reaction = event['reaction']
        if reaction == 'todobee':
            logger.info("User added :todobee: reaction.")
            user = event['user']
            channel = event['item']['channel']
            ts = event['item']['ts']
            logger.info(f"Adding user data ({user, channel, ts}) to table.")

            manage_data.store_user_data(user, channel, ts)
    
    elif data.get('event', {}).get('type') == 'reaction_removed':
        event = data['event']
        reaction = event['reaction']
        if reaction == 'todobee':
            logger.info("User removed :todobee: reaction.")
            user = event['user']
            channel = event['item']['channel']
            ts = event['item']['ts']
            logger.info(f"Removing user data ({user, channel, ts}) to table.")
            # Delete the reaction removed event
            manage_data.delete_user_data(user, ts)
    
    return response


def lambda_handler(event, context):

    if event.get('source') == 'aws.scheduler':
        # Call the send_reminders function if triggered by EventBridge
        logger.info("[AWS Event] Running process for sending reminders to slack users.")
        return send_reminders()
    else:

        # Initialize the Flask app
        logger.info("[Slack Event] Running process to store the data.")
        with app.test_request_context(
            path=event.get('path', '/'),
            method=event.get('httpMethod', 'GET'),
            headers=event.get('headers', {}),
            data=event.get('body', '')
        ):
            # Call the route handler
            response = app.full_dispatch_request()
            
            # Return the response in the API Gateway format
            return {
                'statusCode': response.status_code,
                'body': response.get_data(as_text=True),
                'headers': dict(response.headers)
            }


# Function to query DynamoDB and send reminders
def send_reminders():
    
    # Group threads by users
    users_threads = {}
    
    for item in manage_data.get_user_data():
        user = item['user']
        if user not in users_threads:
            users_threads[user] = []
        users_threads[user].append(item['link'])
    
    logger.info("Number of users to send reminders to: %s", len(users_threads))
    # Send reminders to each user with the threads they marked with :todobee:
    for user, threads in users_threads.items():

        text = "Hey! Here are your slack threads to follow up on:\n\n"
        logger.info(f"Sending reminders to user {user}")
        logger.info(f"Number of threads: {len(threads)}")
        for i, thread in enumerate(threads, 1):
            text += f"• <{thread}|Thread {i}>\n"
        
        # Send the message via Slack
        response = requests.post('https://slack.com/api/chat.postMessage', headers=HEADERS, json={
            "channel": user,
            "text": text
        })
        logger.info("Reminder sent to user %s", user)
    
    logger.info("Deleting old records.")
    manage_data.delete_old_user_data()

    return {"statusCode": 200, "body": json.dumps("Reminders sent successfully")}
