from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
import json
import database
import time

db = database.UserDatabase()

with open('../auth.json') as auth_file:
    auth_data = json.load(auth_file)

# Your Account SID from twilio.com/console
account_sid = auth_data["account_sid"]
# Your Auth Token from twilio.com/console
auth_token = auth_data["auth_token"]

client = Client(account_sid, auth_token)

def send_message(phone, message):
    print(phone)
    print(message)
    client.api.account.messages.create(
                to=phone, 
                from_="+14123019315",
                body= message)

def main():
    records = db.sheet.get_all_records()
    
    pre_registered_message = "Hi %(name)s!  This is the new Bloomcraft message service, BloomBot.  I can help you contact the owners of cars in the Bloomcraft lot based on their license plates.\n\nI already have a license plate, %(plate)s, registered to your name.  To send a message you can type 'plate ABC123 Your lights are on!', and I'll send the owner of the plate 'ABC123' your message.  Stuart's license plate is JXV3875 - give it a try if you like"

    unregistered_message = "Hi %(name)s!  This is the new Bloomcraft message service, BloomBot.  I can help you contact the owners of cars in the Bloomcraft lot based on their license plates.\n\nI don't have your license plate on file yet.  Please register by sending the word 'register' followed by your license plate.  To send a message to someone else you can type 'plate ABC123 Your lights are on!', and I'll send the owner of the plate 'ABC123' your message.  Stuart's license plate is JXV3875 - once you register you can give it a try if you like"
    
    for r in records:
        if r['send_invite'] == "TRUE":
            
            if r['Plate']:
                send_message(r['Phone'], pre_registered_message % {'name':r['informal_name'], 'plate':json.loads(r['Plate'])[0]})
            else:
                send_message(r['Phone'], unregistered_message % {'name':r['informal_name']})

            time.sleep(1)
            
    print('Done')

main()
