import json
import boto3
import os
import uuid
from datetime import datetime

# Initialize DynamoDB resource
dynamodb = boto3.resource('dynamodb')
 # Get the DynamoDB table name from environment variables
table_name = os.environ.get('TABLE_NAME')
table = dynamodb.Table(table_name)

def lambda_handler(event, context):
    # Iterate over each record in the event
    for record in event['Records']:
        id = str(uuid.uuid4())  # Unique identifier
        created_on = datetime.now().strftime('%m/%d/%y')  # Creation timestamp
        modified_on = created_on  # Initially the same as created_on
        
        # Check if the event is an SNS message or an S3 event
        if 'Sns' in record:
            # Handle SNS event (Lambda-triggered)
            sns_message = record['Sns']['Message']
            sns_subject = record['Sns'].get('Subject', 'No Subject')
            sns_region = record['Sns']['TopicArn'].split(':')[3]
            
            # Log the SNS message for debugging
            print(f"SNS Message: {sns_message}")
            
            try:
                # Try to parse the message as JSON
                message_body = json.loads(sns_message)
            except json.JSONDecodeError:
                # If not JSON, treat it as plain text
                message_body = sns_message
            
            # Check if message_body is a dictionary and contains specific Java fields
            if isinstance(message_body, dict) and 'application_name' in message_body:
                # Handle Java Spring event
                application_name = message_body.get('application_name', 'Java Spring Boot')
                message_content = message_body.get('message', 'No message content provided')

                # Prepare the item for Java Spring event
                item = {
                    'Id': id,
                    'Application': 'Java',  # Set Application as 'Java'
                    'ApplicationName': application_name,
                    'BucketName': None,  # Not applicable for Java Spring events
                    'FileName': None,    # Not applicable for Java Spring events
                    'Region': sns_region,      # Not applicable for Java Spring events
                    'Message': message_content,
                    'CreatedOn': created_on,
                    'ModifiedOn': modified_on
                }
                
            elif isinstance(message_body, dict) and 'ApplicationName' in message_body:
                # Handle Python SNS event
                application_name = message_body.get('ApplicationName', 'unknown_application')
                message_content = message_body.get('Message', 'No message content')

                # Prepare the item for Python SNS event
                item = {
                    'Id': id,
                    'Application': 'Python',
                    'ApplicationName': application_name,
                    'BucketName': None,  # Not applicable for Python events
                    'FileName': None,    # Not applicable for Python events
                    'Region': sns_region,
                    'Message': message_content,
                    'CreatedOn': created_on,
                    'ModifiedOn': modified_on
                }

            elif isinstance(message_body, dict) and 'Records' in message_body and 's3' in message_body['Records'][0]:
                # Extract S3 details for S3 event
                s3_info = message_body
                bucket_name = s3_info['Records'][0]['s3']['bucket']['name']
                file_name = s3_info['Records'][0]['s3']['object']['key']
                region = s3_info['Records'][0]['awsRegion']
                
                # Prepare the item for S3 event
                item = {
                    'Id': id,
                    'Application': 'S3',
                    'ApplicationName': None,  # Not applicable for S3 events
                    'BucketName': bucket_name,
                    'FileName': file_name,
                    'Region': region,
                    'Message': None,  # Not applicable for S3 events
                    'CreatedOn': created_on,
                    'ModifiedOn': modified_on
                }

            else:
                # Handle regular SNS event
                item = {
                    'Id': id,
                    'Application': 'Lambda',  # Set Application as 'Lambda' for other SNS events
                    'ApplicationName': context.function_name,
                    'BucketName': None,  # Not applicable for SNS events
                    'FileName': None,    # Not applicable for SNS events
                    'Region': sns_region,
                    'Message': message_body if isinstance(message_body, str) else message_body.get('default', sns_message),
                    'CreatedOn': created_on,
                    'ModifiedOn': modified_on
                }

        else:
            print("Unknown event type, skipping record.")
            continue
        
        # Insert the item into DynamoDB
        try:
            table.put_item(Item=item)
            print(f"Successfully stored item: {item}")
        except Exception as e:
            print(f"Error storing item: {e}")

    return {
        'statusCode': 200,
        'body': json.dumps('Processed records successfully!')
    }
