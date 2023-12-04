"""
Lambda function for sending emails via Amazon Simple Email Service.
Triggered on file update (new/existing) in S3 bucket.
Had to verify the email address in Amazon SES before usage.
"""
from os import getenv
import boto3


def send_mail(
        recipient: str,
        sender: str,
        subject: str,
        html_body: str,
        encoding: str = "UTF-8",
):
    session = boto3.session.Session()
    client = session.client('ses')

    message = {
        'Body': {
            'Html': {
                'Charset': encoding,
                'Data': html_body,
            }
        },
        'Subject': {
            'Charset': encoding,
            'Data': subject,
        },
    }
    response = client.send_email(
        Destination={'ToAddresses': [recipient]},
        Message=message,
        Source=sender,
    )
    return response


def main(event=None, context=None):
    send_mail(
        recipient=getenv("RECEIVER_EMAIL"),
        sender=getenv("SENDER_EMAIL"),
        subject="S3 Event Notification",
        html_body='Bucket file updated!',
    )
