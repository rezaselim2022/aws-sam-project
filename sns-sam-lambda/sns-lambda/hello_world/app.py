import json

def lambda_handler(event, context):
    print("Event received:", event)
    for record in event['Records']:
        sns_message = record['Sns']['Message']
        print("SNS Message:", sns_message)
    return {
        'statusCode': 200,
        'body': json.dumps('Processed SNS message successfully!')
    }
