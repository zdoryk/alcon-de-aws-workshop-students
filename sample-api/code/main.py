import json


def lambda_handler(event, context):
    # Extract query parameters
    query_params = event.__getitem__('queryStringParameters')
    headers = event.__getitem__('headers')

    date = ''
    start_time = ''
    end_time = ''
    auth_token = ''

    if query_params:
        date = event['queryStringParameters'].get('date', '')
        start_time = event['queryStringParameters'].get('start_time', '')
        end_time = event['queryStringParameters'].get('end_time', '')

    if headers:
        # Extract Bearer token from headers
        auth_token = event['headers'].get('Authorization', '').split('Bearer ')[-1]

    # Your existing Lambda logic goes here

    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'Lambda function executed successfully',
            'date': date,
            'start_time': start_time,
            'end_time': end_time,
            'auth_token': auth_token
        })
    }
