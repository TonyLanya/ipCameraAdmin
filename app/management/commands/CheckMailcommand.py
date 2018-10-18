from django.core.management.base import BaseCommand
import poplib
from email import parser
import string, random
from io import StringIO
import rfc822py3.rfc822py3 as rfc822
from datetime import date, timedelta
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools

def List_to_String(lis, separator=''):
    return str.encode(separator).join(lis)

# If modifying these scopes, delete the file token.json.
SCOPES = 'https://www.googleapis.com/auth/gmail.readonly'

class Command(BaseCommand):
    help = 'check gmail alerts'

    def handle(self, *args, **options):
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

        print(response)


        # pop_conn = poplib.POP3_SSL('pop.gmail.com')
        # pop_conn.user('tomasfans1985@gmail.com')
        # pop_conn.pass_('qwer1234QWER!@#$')
        # #while true:
        
        # print("listing emails")
        # resp, items, octets = pop_conn.list()

        # id, size = str.split(items[len(items)-1].decode("utf-8"))
        # resp, text, octets = pop_conn.retr(id)

        # print(type(text))
        # text = List_to_String(text, "\n")
        # file = StringIO(text.decode("utf-8"))
        # message = rfc822.Message(file)

        # print(message)
        # print(message['From'])
        # print(message['Subject'])
        # print(message['Date'])
        # pop_conn.quit()