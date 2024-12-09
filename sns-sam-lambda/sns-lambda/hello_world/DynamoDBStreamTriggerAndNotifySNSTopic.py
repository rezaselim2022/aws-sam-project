import json
import os
import boto3

# Initialize SNS client
sns_client = boto3.client('sns')
sns_topic_arn = os.environ['SNS_TOPIC_ARN']  # Environment variable set in SAM template

def lambda_handler(event, context):
    # Fetch the SNS topic ARN from the environment variable
    
    
    processed_ids = set()

    for record in event['Records']:
        event_name = record['eventName']
        print(f"Event Name: {event_name}")

        new_data = record['dynamodb'].get('NewImage', {})
        old_data = record['dynamodb'].get('OldImage', {})

        if event_name == 'INSERT' and new_data:
            print(f"New Data (INSERT): {json.dumps(new_data)}")

        if old_data:
            print(f"Old Data: {json.dumps(old_data)}")

        record_id = new_data.get("Id", {}).get("S") or old_data.get("Id", {}).get("S")

        if record_id in processed_ids:
            continue
        processed_ids.add(record_id)

        message = {
            'EventType': event_name,
            'NewData': new_data,
            'OldData': old_data
        }

        # Publish to SNS
        try:
            response = sns_client.publish(
                TopicArn=sns_topic_arn,
                Message=json.dumps(message),
                Subject=f'DynamoDB {event_name} Event Notification'
            )
            print(f"Message sent to SNS: {response['MessageId']}")
        except Exception as e:
            print(f"Error publishing to SNS: {str(e)}")

    return {
        'statusCode': 200,
        'body': json.dumps('Successfully processed DynamoDB Stream and sent to SNS')
    }
