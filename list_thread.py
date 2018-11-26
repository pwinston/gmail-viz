#!/usr/local/bin/python3
"""
Get a list of Threads from the user's mailbox.
"""
import argparse
import base64
import json
import os

from apiclient import errors
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools

def pretty_json(data):
  return json.dumps(data, indent=4)

def write_messages(response):
    thread_path = response['id']
    os.makedirs(thread_path, exist_ok=True)
    for m in response['messages']:
      message_path = os.path.join(thread_path, m['id'])
      with open(message_path + '.json', "w") as f:
        f.write(pretty_json(m))
      data = m['payload']['parts'][0]['body']['data']
      print(data)
      txt = base64.urlsafe_b64decode(data).decode("utf-8") 
      with open(message_path + '.txt', "w") as f:
        f.write(txt)


def list_thread(service, user_id, thread_id):
  try:
    response = service.users().threads().get(userId=user_id, id=thread_id).execute()
    write_messages(response)
  except errors.HttpError as error:
    print('An error occurred: %s' % error)

def create_service():
    store = file.Storage('token.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
        creds = tools.run_flow(flow, store)
    return build('gmail', 'v1', http=creds.authorize(Http()))

def main():
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    parser = argparse.ArgumentParser(description='List threads.')
    parser.add_argument('thread_id', help='Thread id')
    args = parser.parse_args()

    service = create_service()
    threads = list_thread(service, 'me', args.thread_id)

    print(json.dumps(threads, indent=4))


if __name__ == '__main__':
    main()