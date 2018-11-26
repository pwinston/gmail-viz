#!/usr/local/bin/python3
"""
Get a list of Threads from the user's mailbox.
"""
import argparse
from apiclient import errors
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
import json

def ListThreadsMatchingQuery(service, user_id, query=''):
  """List all Threads of the user's mailbox matching the query.

  Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    query: String used to filter messages returned.
           Eg.- 'label:UNREAD' for unread messages only.

  Returns:
    List of threads that match the criteria of the query. Note that the returned
    list contains Thread IDs, you must use get with the appropriate
    ID to get the details for a Thread.
  """
  try:
    response = service.users().threads().list(userId=user_id, q=query).execute()
    threads = []
    if 'threads' in response:
      threads.extend(response['threads'])

    while 'nextPageToken' in response:
      page_token = response['nextPageToken']
      response = service.users().threads().list(userId=user_id, q=query,
                                        pageToken=page_token).execute()
      threads.extend(response['threads'])

    return threads
  except errors.HttpError as error:
    print('An error occurred: %s' % error)


def main():
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    parser = argparse.ArgumentParser(description='List threads.')
    parser.add_argument('query', help='Query String')
    args = parser.parse_args()

    store = file.Storage('token.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('gmail', 'v1', http=creds.authorize(Http()))

    threads = ListThreadsMatchingQuery(service, 'me', args.query)

    import pprint
    #pprint.pprint(threads)
    print(json.dumps(threads, indent=4))


if __name__ == '__main__':
    main()