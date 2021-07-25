import json
import boto3
import datetime
import dateutil.parser
import os
import time


def elicit_slot(session_attributes, intent_name, slots, slot_to_elicit, message):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'ElicitSlot',
            'intentName': intent_name,
            'slots': slots,
            'slotToElicit': slot_to_elicit,
            'message': message
        }
    }
    
def close(session_attributes, fulfillment_state, message):
    response = {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Close',
            'fulfillmentState': fulfillment_state,
            'message': message
        }
    }

    return response
    
def delegate(session_attributes, slots):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Delegate',
            'slots': slots
        }
    }

def is_invalid_date(date):
    try:
        parsed_date = dateutil.parser.parse(date).date()
        return parsed_date < datetime.date.today()
    except ValueError:
        return False

def is_invalid_time(time, date):
    try:
        parsed_time = dateutil.parser.parse(time).timestamp()
        parsed_date = dateutil.parser.parse(date).date()
        return parsed_date == datetime.date.today() and parsed_time < datetime.datetime.now().timestamp()
    except ValueError:
        return False;
        

def greet_user(intent_request):
    session_attributes = intent_request['sessionAttributes'] if intent_request['sessionAttributes'] is not None else {}
    
    return close(
        session_attributes,
        'Fulfilled',
        {
            'contentType': 'PlainText',
            'content': 'Hi there, how can I help?'
        }
    )
    
def respond_to_thanks(intent_request):
    session_attributes = intent_request['sessionAttributes'] if intent_request['sessionAttributes'] is not None else {}
    
    return close(
        session_attributes,
        'Fulfilled',
        {
            'contentType': 'PlainText',
            'content': 'You\'re welcome!'
        }
    )


def suggest_restaurant(intent_request):
    slots = intent_request['currentIntent']['slots']
    location = slots.get('location')
    cuisine = slots.get('cuisine')
    party = slots.get('party')
    date = slots.get('date')
    time = slots.get('time')
    phone = slots.get('phone')
    email = slots.get('email')
    
    session_attributes = intent_request['sessionAttributes'] if intent_request['sessionAttributes'] is not None else {}
    
    party_int = int(party) if party is not None else None
        
    if intent_request['invocationSource'] == 'DialogCodeHook':
        invalidSlot = None
        invalidMessage = None
        
        cuisines = ["chinese", "mexican", "korean", "thai", "japanese", 
        "indian","italian"]
        
        cities = ['new york', 'nyc', 'ny', 'manhattan', 'queens', 'brooklyn', 'staten island', 'bronx']
        
        if party_int is not None and (party_int < 1 or party_int > 20):
            invalidSlot = 'party'
            invalidMessage ='Party size can be from one to twenty people. How many people are in your party?'
        elif location and location.lower() not in cities:
            invalidSlot = 'location'
            invalidMessage = 'I\'m sorry, that location is not supported. Please try anyone of these: {}'.format(", ".join(cities))
        elif cuisine and cuisine.lower() not in cuisines:
            invalidSlot = 'cuisine'
            invalidMessage = 'I\'m sorry we don\'t support that cuisine. Please choose anyone of these: {}'.format(", ".join(cuisines))
        elif date and is_invalid_date(date):
            invalidSlot = 'date'
            invalidMessage = 'The date can be any date from today onwards. What date would you like to dine on?'
        elif time and is_invalid_time(time, date):
            invalidSlot = 'time'
            invalidMessage = 'The time can be any time after now. What time would you like to dine?'
        elif phone is not None and (len(phone) < 10 or len(phone) > 12 or (len(phone) == 11 and phone[0] != '1') or (len(phone) == 12 and (phone[0] != '+' or phone[1] != '1'))):
            invalidSlot = 'phone'
            invalidMessage = 'The phone number must be a valid US phone number. What phone number would you like to put down?'
        elif email is not None and '@' not in email:
            invalidSlot = 'email'
            invalidMessage = 'The email id must contain @ symbol. What email id would you like to put down?'
            
        if invalidSlot:
            slots[invalidSlot] = None
            return elicit_slot(
                session_attributes,
                intent_request['currentIntent']['name'],
                slots,
                invalidSlot,
                {'contentType': 'PlainText', 'content': invalidMessage}
            )
        return delegate(session_attributes, slots)
        
    phone = ('+1' if len(phone) == 10 else '+' if len(phone) == 11 and phone[0] == 1 else '') + phone
    
    preferences = json.dumps({
        'location': location,
        'cuisine': cuisine,
        'party': party,
        'date': date,
        'time': time,
        'phone': phone,
        'email': email
    })
    print('preferences')
    print(preferences)
    client = boto3.client('sqs')
    client.send_message(
        QueueUrl='https://sqs.us-east-1.amazonaws.com/524462994473/restaurants', 
        MessageBody=preferences,
        MessageAttributes={
            'MessageType': {
                'StringValue': 'GetSuggestionsForDining',
                'DataType': 'String'
            }
        },
    )

    return close(
        session_attributes,
        'Fulfilled',
        {
            'contentType': 'PlainText',
            'content': 'You\'re all set. Expect my suggestions shortly at {} and {}! Have a good day.'.format(phone, email)
        }
    )
    
def dispatch(intent_request):

    intent_name = intent_request['currentIntent']['name']
    if intent_name == 'Greeting':
        return greet_user(intent_request)
    elif intent_name == 'DiningSuggestions':
        return suggest_restaurant(intent_request)
    elif intent_name == 'ThankYou':
        return respond_to_thanks(intent_request)

    raise Exception('Intent with name ' + intent_name + ' not supported')


# --- Main handler ---


def lambda_handler(event, context):
    os.environ["TZ"] = 'America/New_York'
    time.tzset()

    return dispatch(event)
