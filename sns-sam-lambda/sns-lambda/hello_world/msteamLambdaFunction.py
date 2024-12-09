import os
import json
import boto3
import urllib3
# Retrieve the webhook URL from environment variables
teams_webhook_url = os.environ.get('TEAMS_WEBHOOK_URL')

def lambda_handler(event, context):
   
    if not teams_webhook_url:
        raise ValueError("TEAMS_WEBHOOK_URL environment variable is not set")

    http = urllib3.PoolManager()
    headers = {'Content-Type': 'application/json'}

    for record in event['Records']:
        sns_message = record['Sns']['Message']
        print("SNS Message:", sns_message)

        try:
            message_data = json.loads(sns_message)
        except json.JSONDecodeError as e:
            print("JSON decode error:", e)
            continue

        event_type = message_data.get('EventType')
        new_data = message_data.get('NewData', {})
        old_data = message_data.get('OldData', {})

        if event_type == 'INSERT':
            message = f"New item added: {new_data}"
        elif event_type == 'MODIFY':
            message = f"Item updated. New values: {new_data} Old values: {old_data}"
        elif event_type == 'REMOVE':
            message = f"Item deleted: {old_data}"
        else:
            message = "Unknown event type"

        adaptive_card_payload = {
            "type": "message",
            "attachments": [
                {
                    "contentType": "application/vnd.microsoft.card.adaptive",
                    "content": {
                        "type": "AdaptiveCard",
                        "version": "1.3",
                        "body": [
                            {"type": "TextBlock", "text": "DynamoDB Change Notification", "weight": "Bolder", "size": "Large"},
                            {"type": "TextBlock", "text": message, "wrap": True},
                            {"type": "TextBlock", "text": f"Event Type: {event_type}", "wrap": True}
                        ]
                    }
                }
            ]
        }

        response = http.request(
            "POST",
            teams_webhook_url,
            body=json.dumps(adaptive_card_payload),
            headers=headers
        )

        print({"statusCode": response.status, "response": response.data})

    return {
        "statusCode": 200,
        "body": json.dumps('Notifications sent to MS Teams')
    }
