import json

def lambda_handler(event, context):
    for record in event['Records']:
        sqs_message_body = record['body']
        print(f"Received SQS message:{sqs_message_body}")
    return {
        'statusCode': 200,
        'body': json.dumps('Message logged successfully')
    }