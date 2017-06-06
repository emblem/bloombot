from flask import Flask, request, redirect
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
from tinydb import TinyDB, Query
import re
import traceback
import json

with open('auth.json') as auth_file:
    auth_data = json.load(auth_file)

# Your Account SID from twilio.com/console
account_sid = auth_data["account_sid"]
# Your Auth Token from twilio.com/console
auth_token = auth_data["auth_token"]

client = Client(account_sid, auth_token)
app = Flask(__name__)
db = TinyDB('data/plates.json')

@app.route("/", methods=['GET', 'POST'])
def sms_handler():
    """Respond to incoming calls with a simple text message."""
    body = request.values.get('Body', None)
    
    if not body: return str("No 'Body' field in message")
    
    (msg_type, params) = process_body(body)

    if msg_type == 'REGISTER':
        return register_plate(request, params)
    elif msg_type == 'UNREGISTER':
        return stop_messages(request)
    elif unknown_number(request):
        return new_user_msg()
    #These commands require a registered source number    
    elif msg_type == 'OPEN':
        return open_door(request, params)
    elif msg_type == 'PLATE':
        return msg_plate(request, params)
    else:
        return help_msg()


#get the canonical form for a plate string
def std_plate(plate_str):
    return re.sub(r'\W+', '', plate_str.upper())

def register_plate(request, params):
    """associate the sender's number with the named plate"""
    try:
        plate = std_plate(params)
        phone = request.values.get('From', None)
            
        assert(plate)
        assert(phone)
        
        q = Query()
        if not db.update({'phone':phone}, q.plate == plate):
            db.insert({'phone':phone, 'plate':plate})

        return msg("Registered '" + plate + ". To send a message send the word 'plate' followed by the plate number and the message.")
    except AssertionError:
        return msg("Failed to register plate")

def msg(message):
    """convert string to TwiML response"""
    return str(MessagingResponse().message(message))

def stop_messages(request):
    """remove a phone number from the database"""
    phone = request.values.get('From', None)
    assert(phone)
    
    q = Query()

    db.remove(q.phone == phone)
    return msg("Messages Stopped")

def open_door(request, params):
    return msg("Door Requests Not Implemented")

def help_msg():
    return msg("Try\n"
               "- register ABC123\n"
               "- unregister\n"
               "- plate XYZ567 your lights are on")

def unknown_number(request):
    phone = request.values.get('From', None)
    assert(phone)

    q = Query()
    return (len(db.search(q.phone == phone)) == 0)

def new_user_msg():
    return msg("Hi! This is Bloombot.  You need to register.  Send the word 'register' followed by your license plate number")
                         
def msg_plate(request, params):
    """send a message to the number(s) associated with the given plate"""
    (plate, params) = process_body(params)
    
    plate = std_plate(plate)
    q = Query()
    records = db.search(q.plate == plate)
    if records:
        for record in records:
            try:
                send_message(record['phone'], plate + ": " + params)
            except KeyError:
                traceback.print_exc()
        return msg("OK! Your message was sent.")

    return msg("Sorry, I don't know who has the plate: '" + plate + "'.")
    
def send_message(phone, message):
    client.api.account.messages.create(
                to=phone, 
                from_="+14123019315",
                body= message)            

def process_body(body):
    body = body.strip()
    result = re.split(r'\s+', body, 1)
    result[0] = re.sub(r'[^\w]+', '', result[0].upper())

    params = ''
    try:
        params = result[1]
    except IndexError:
        pass
        
    return (result[0], params)

if __name__ == "__main__":
    app.run(debug=True)
