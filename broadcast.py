from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
import json

with open('../auth.json') as auth_file:
    auth_data = json.load(auth_file)

# Your Account SID from twilio.com/console
account_sid = auth_data["account_sid"]
# Your Auth Token from twilio.com/console
auth_token = auth_data["auth_token"]

client = Client(account_sid, auth_token)

def send_message(phone, message):
    client.api.account.messages.create(
                to=phone, 
                from_="+14123019315",
                body= message)            

message = "Hi Phip!  This is the Bloomcraft parking lot message service, Bloombot.  I can help deliver messages to people based on their license plates.  To use this service, reply with the word register followed by your plate number."

send_message("+14125899292", message)
