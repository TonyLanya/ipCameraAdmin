from __future__ import print_function
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from datetime import date, timedelta
import base64
import email

# If modifying these scopes, delete the file token.json.
SCOPES = 'https://www.googleapis.com/auth/gmail.readonly'
def GetMessage(service, user_id, msg_id):
  """Get a Message with given ID.

  Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    msg_id: The ID of the Message required.

  Returns:
    A Message.
  """
  try:
    message = service.users().messages().get(userId=user_id, id=msg_id).execute()

    print('Message snippet: %s' % message['snippet'])

    return message
  except error:
    print( 'An error occurred: %s' % error )

def GetMimeMessage(service, user_id, msg_id):
  """Get a Message and use it to create a MIME Message.

  Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    msg_id: The ID of the Message required.

  Returns:
    A MIME Message, consisting of data from Message.
  """
  message = service.users().messages().get(userId=user_id, id=msg_id,
                                             format='raw').execute()

  print('Message snippet: %s' % message['snippet'])

  msg_str = base64.urlsafe_b64decode(message['raw'].encode('ASCII'))

  mime_msg = email.message_from_string(msg_str.decode("utf-8"))

  return mime_msg

def main():
    store = file.Storage('token.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('gmail', 'v1', http=creds.authorize(Http()))
    today = date.today()
    yesterday = today - timedelta(1)

    # do your setup...

    user_id = 'tomasfans1985@gmail.com'

    # Dates have to formatted in YYYY/MM/DD format for gmail
    query = "before: {0} after: {1}".format(today.strftime('%Y/%m/%d'),
                                            yesterday.strftime('%Y/%m/%d'))

    response = service.users().messages().list(userId=user_id,
                                            q=query).execute()
    # Process the response for messages...

    print(response['messages'][0]['id'])
    GetMimeMessage(service, 'me', response['messages'][0]['id'])

if __name__ == '__main__':
    main()