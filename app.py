from flask import Flask, request
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Twilio credentials
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_WHATSAPP_NUMBER = os.getenv('TWILIO_WHATSAPP_NUMBER')

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Store conversation state per user
conversation_states = {}

# Conversation steps
STEPS = {
    'NAME': 0,
    'PHONE': 1,
    'EMAIL': 2,
    'ISSUE': 3,
    'ADDRESS': 4,
    'TIME': 5,
    'CONFIRMATION': 6
}

TIME_OPTIONS = ['Morning (9 AM - 12 PM)', 'Afternoon (12 PM - 4 PM)', 'Evening (4 PM - 7 PM)', 'ASAP']

def initialize_user(user_id):
    if user_id not in conversation_states:
        conversation_states[user_id] = {
            'step': STEPS['NAME'],
            'customerInfo': {
                'name': '',
                'phone': '',
                'email': '',
                'address': '',
                'issue': '',
                'applianceType': 'Refrigerator',
                'preferredTime': ''
            }
        }
    return conversation_states[user_id]

def process_user_input(user_id, user_message):
    state = initialize_user(user_id)
    info = state['customerInfo']
    response = ''

    if state['step'] == STEPS['NAME']:
        info['name'] = user_message
        state['step'] = STEPS['PHONE']
        response = f"Nice to meet you, {user_message}! What's the best phone number to reach you?"

    elif state['step'] == STEPS['PHONE']:
        info['phone'] = user_message
        state['step'] = STEPS['EMAIL']
        response = "Great! And what's your email address?"

    elif state['step'] == STEPS['EMAIL']:
        info['email'] = user_message
        state['step'] = STEPS['ISSUE']
        response = "Thanks! Now, could you please describe the issue with your refrigerator?"

    elif state['step'] == STEPS['ISSUE']:
        info['issue'] = user_message
        state['step'] = STEPS['ADDRESS']
        response = "I understand. Now, please provide your full address so we can send a technician to your location."

    elif state['step'] == STEPS['ADDRESS']:
        info['address'] = user_message
        state['step'] = STEPS['TIME']
        response = "Perfect! When would be a good time for our technician to visit?\n\n"
        for idx, time in enumerate(TIME_OPTIONS, 1):
            response += f"{idx}. {time}\n"
        response += "\nReply with the number (1-4)"

    elif state['step'] == STEPS['TIME']:
        try:
            time_index = int(user_message) - 1
            if 0 <= time_index < len(TIME_OPTIONS):
                info['preferredTime'] = TIME_OPTIONS[time_index]
                state['step'] = STEPS['CONFIRMATION']
                response = "Thank you! Here's a summary of your service request:\n\n"
                response += f"Name: {info['name']}\n"
                response += f"Phone: {info['phone']}\n"
                response += f"Email: {info['email']}\n"
                response += f"Address: {info['address']}\n"
                response += f"Issue: {info['issue']}\n"
                response += f"Preferred Time: {info['preferredTime']}\n"
                response += f"Status: Service request submitted successfully!\n\n"
                response += "Our technician will contact you within 30 minutes to confirm the appointment. Thank you for choosing FridgeFix!"
            else:
                response = "Invalid option. Please reply with a number between 1-4."
        except ValueError:
            response = "Invalid option. Please reply with a number between 1-4."

    else:
        response = "Thank you for using FridgeFix! Your request has been processed."

    return response

@app.route('/whatsapp', methods=['POST'])
def whatsapp_webhook():
    incoming_msg = request.values.get('Body', '').strip()
    sender_number = request.values.get('From', '')
    user_id = sender_number.replace('whatsapp:', '')

    # Process the message
    bot_response = process_user_input(user_id, incoming_msg)

    # Create Twilio response
    resp = MessagingResponse()
    resp.message(bot_response)

    return str(resp)

@app.route('/health', methods=['GET'])
def health():
    return {'status': 'OK'}, 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)
