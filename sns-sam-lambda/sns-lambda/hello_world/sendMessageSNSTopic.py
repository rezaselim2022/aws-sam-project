import json
import boto3
import os

# Initialize SNS client
sns_client = boto3.client('sns')

def lambda_handler(event, context):
    # Get the SNS Topic ARN from the environment variable
    sns_topic_arn = os.environ.get('SNS_TOPIC_ARN')

    message = {
        'default': 'Hello, this is a test message from AWS Lambda to SNS!',
        'sms': 'Test message for SMS',
        'email': 'Test message for Email',
    }

    # Send the message to the SNS topic
    response = sns_client.publish(
        TopicArn=sns_topic_arn,
        Message=json.dumps(message),
        MessageStructure='json'
    )

    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'Message sent to SNS Topic!',
            'response': response
        })
    }
