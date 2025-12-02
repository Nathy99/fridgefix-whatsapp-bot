from flask import Flask, request
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
import os
import re
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
    'PHONE_CHECK': -1,
    'NAME': 0,
    'PHONE': 1,
    'EMAIL': 2,
    'ISSUE_SELECT': 3,
    'ISSUE_DETAIL': 3.5,
    'ADDRESS': 4,
    'TIME': 5,
    'CONFIRMATION': 6,
    'COMPLETED': 7
}

TIME_OPTIONS = ['Morning (9 AM - 12 PM)', 'Afternoon (12 PM - 4 PM)', 'Evening (4 PM - 7 PM)', 'ASAP']

# Fridge issue options
FRIDGE_ISSUES = [
    'Not cooling properly',
    'Freezer not working',
    'Leaking water',
    'Strange noises',
    'Ice buildup',
    'Door seal damaged',
    'Compressor issues',
    'Thermostat problems',
    'Electrical issues',
    'Other issue'
]

# South African provinces for location validation
SA_PROVINCES = [
    'Eastern Cape', 'Free State', 'Gauteng', 'KwaZulu-Natal',
    'Limpopo', 'Mpumalanga', 'Northern Cape', 'North West', 'Western Cape'
]

def validate_sa_phone(phone):
    """Validate South African phone number - accepts multiple formats"""
    # Remove spaces, dashes, parentheses and other special characters
    phone_clean = re.sub(r'[\s\-\(\)\.]+', '', phone)
    
    # Accept formats:
    # +27XXXXXXXXXX, 27XXXXXXXXXX, 0XXXXXXXXXX (10 digits after 0)
    
    # If starts with +27
    if phone_clean.startswith('+27'):
        phone_clean = phone_clean[1:]  # Remove +
    
    # If starts with 0, replace with 27
    if phone_clean.startswith('0'):
        phone_clean = '27' + phone_clean[1:]
    
    # Check if it's valid SA number (27 + 9 digits = 11 total)
    return phone_clean.startswith('27') and len(phone_clean) == 11 and phone_clean.isdigit()

def validate_gmail(email):
    """Validate Gmail email address"""
    gmail_pattern = r'^[a-zA-Z0-9._%+-]+@gmail\.com$'
    return re.match(gmail_pattern, email) is not None

def validate_sa_location(address):
    """Check if address contains South African province or city"""
    address_upper = address.upper()
    
    # Check for all 9 SA provinces (case-insensitive)
    for province in SA_PROVINCES:
        if province.upper() in address_upper:
            return True
    
    # Also check for common SA cities
    sa_cities = [
        'johannesburg', 'cape town', 'durban', 'pretoria', 'bloemfontein', 
        'port elizabeth', 'east london', 'pietermaritzburg', 'polokwane', 'nelspruit',
        'sandton', 'midrand', 'centurion', 'stellenbosch', 'paarl', 'bellville',
        'soweto', 'randburg', 'roodepoort', 'boksburg', 'benoni', 'springs',
        'witbank', 'secunda', 'rustenburg', 'potchefstroom', 'klerksdorp'
    ]
    
    for city in sa_cities:
        if city in address_upper:
            return True
    
    return False

def initialize_user(user_id):
    if user_id not in conversation_states:
        conversation_states[user_id] = {
            'step': STEPS['PHONE_CHECK'],
            'customerInfo': {
                'name': '',
                'phone': '',
                'email': '',
                'address': '',
                'issue_category': '',
                'issue_detail': '',
                'applianceType': 'Refrigerator',
                'preferredTime': ''
            },
            'phone_attempts': 0,
            'email_attempts': 0,
            'location_attempts': 0
        }
    return conversation_states[user_id]

def process_user_input(user_id, user_message):
    state = initialize_user(user_id)
    info = state['customerInfo']
    response = ''
    
    # Check for greeting messages
    greetings = ['hi', 'hello', 'hey', 'hiya', 'greetings', 'good morning', 'good afternoon', 'good evening']
    if user_message.lower().strip() in greetings:
        response = "👋 Hello! I'm happy to help!\n\n"
        response += "Please provide your South African phone number to get started:\n\n"
        response += "Example: +27 82 123 4567\n"
        response += "Or: 0821234567"
        return response

    # Step -1: Phone validation (South African number check)
    if state['step'] == STEPS['PHONE_CHECK']:
        if validate_sa_phone(user_message):
            info['phone'] = user_message
            state['step'] = STEPS['NAME']
            response = "✅ Great! Your South African number is verified.\n\nNow, could you please tell me your name?"
        else:
            state['phone_attempts'] += 1
            if state['phone_attempts'] >= 3:
                response = "❌ SERVICE NOT AVAILABLE\n\n"
                response += "FridgeFix currently operates only in South Africa.\n\n"
                response += "📍 We don't have technicians in your location.\n\n"
                response += "🌐 Please visit our website for service availability:\n"
                response += "www.fridgefix.co.za\n\n"
                response += "Or contact us:\n"
                response += "📧 support@fridgefix.co.za\n"
                response += "📞 +27 (0)11 123 4567\n\n"
                response += "We apologize for the inconvenience!"
                # Reset conversation on max attempts
                conversation_states[user_id] = {
                    'step': STEPS['PHONE_CHECK'],
                    'customerInfo': {
                        'name': '',
                        'phone': '',
                        'email': '',
                        'address': '',
                        'issue_category': '',
                        'issue_detail': '',
                        'applianceType': 'Refrigerator',
                        'preferredTime': ''
                    },
                    'phone_attempts': 0,
                    'email_attempts': 0,
                    'location_attempts': 0
                }
            else:
                response = f"❌ Invalid phone number. Please provide a valid South African number.\n\n"
                response += f"Attempts remaining: {3 - state['phone_attempts']}\n\n"
                response += "Accepted formats:\n"
                response += "• +27 82 123 4567\n"
                response += "• 27821234567\n"
                response += "• 0821234567"

    # Step 0: Name
    elif state['step'] == STEPS['NAME']:
        info['name'] = user_message
        state['step'] = STEPS['EMAIL']
        response = f"Nice to meet you, {user_message}! 👋\n\nPlease provide your Gmail email address (required for confirmation):"

    # Step 2: Email validation (Gmail only)
    elif state['step'] == STEPS['EMAIL']:
        if validate_gmail(user_message):
            info['email'] = user_message
            state['step'] = STEPS['ISSUE_SELECT']
            response = "✅ Email verified!\n\n"
            response += "🔧 What issue are you experiencing with your refrigerator?\n\n"
            for idx, issue in enumerate(FRIDGE_ISSUES, 1):
                response += f"{idx}. {issue}\n"
            response += "\nReply with the number (1-10)"
        else:
            state['email_attempts'] += 1
            if state['email_attempts'] >= 3:
                response = "❌ We only accept Gmail addresses for service confirmation.\n\n"
                response += "Please create a free Gmail account at:\n"
                response += "www.gmail.com\n\n"
                response += "Then restart the conversation with your Gmail address."
                # Reset conversation on max attempts
                conversation_states[user_id] = {
                    'step': STEPS['PHONE_CHECK'],
                    'customerInfo': {
                        'name': '',
                        'phone': '',
                        'email': '',
                        'address': '',
                        'issue_category': '',
                        'issue_detail': '',
                        'applianceType': 'Refrigerator',
                        'preferredTime': ''
                    },
                    'phone_attempts': 0,
                    'email_attempts': 0,
                    'location_attempts': 0
                }
            else:
                response = f"❌ Invalid email. Please use a Gmail address (example@gmail.com).\n\n"
                response += f"Attempts remaining: {3 - state['email_attempts']}"

    # Step 3: Issue selection (after email)
    elif state['step'] == STEPS['ISSUE_SELECT']:
        try:
            issue_index = int(user_message) - 1
            if 0 <= issue_index < len(FRIDGE_ISSUES):
                info['issue_category'] = FRIDGE_ISSUES[issue_index]
                state['step'] = STEPS['ISSUE_DETAIL']
                response = f"✅ Got it! You selected: {FRIDGE_ISSUES[issue_index]}\n\n📝 Please provide any additional details about the issue (or type 'none' if no additional details):"
            else:
                response = "❌ Invalid option. Please reply with a number between 1-10."
        except ValueError:
            response = "❌ Invalid option. Please reply with a number between 1-10."

    # Step 3.5: Issue detail (additional details)
    elif state['step'] == STEPS['ISSUE_DETAIL']:
        if user_message.lower() != 'none':
            info['issue_detail'] = user_message
        state['step'] = STEPS['ADDRESS']
        response = "Thank you! 📝\n\nNow, please provide your full address including the province (e.g., 'Johannesburg, Gauteng' or 'Cape Town, Western Cape'):"

    # Step 4: Address validation (South Africa location check)
    elif state['step'] == STEPS['ADDRESS']:
        if validate_sa_location(user_message):
            info['address'] = user_message
            state['step'] = STEPS['TIME']
            response = "✅ Location verified in South Africa!\n\n⏰ When would be a good time for our technician to visit?\n\n"
            for idx, time in enumerate(TIME_OPTIONS, 1):
                response += f"{idx}. {time}\n"
            response += "\nReply with the number (1-4)"
        else:
            state['location_attempts'] += 1
            if state['location_attempts'] >= 3:
                response = "❌ SERVICE NOT AVAILABLE IN YOUR LOCATION\n\n"
                response += "FridgeFix currently operates only within South Africa.\n\n"
                response += "📍 We don't have technicians in your area.\n\n"
                response += "🌐 For service availability, please visit:\n"
                response += "www.fridgefix.co.za\n\n"
                response += "📧 Email: support@fridgefix.co.za\n"
                response += "📞 Phone: +27 (0)11 123 4567\n\n"
                response += "We apologize for the inconvenience!"
                # Reset conversation on max attempts
                conversation_states[user_id] = {
                    'step': STEPS['PHONE_CHECK'],
                    'customerInfo': {
                        'name': '',
                        'phone': '',
                        'email': '',
                        'address': '',
                        'issue_category': '',
                        'issue_detail': '',
                        'applianceType': 'Refrigerator',
                        'preferredTime': ''
                    },
                    'phone_attempts': 0,
                    'email_attempts': 0,
                    'location_attempts': 0
                }
            else:
                response = f"❌ Location not recognized. Please provide your full address with a South African province or city.\n\n"
                response += "📍 Provinces: Gauteng, Western Cape, KwaZulu-Natal, Eastern Cape, Free State, Limpopo, Mpumalanga, Northern Cape, North West\n\n"
                response += "Example: 'Johannesburg, Gauteng' or 'Cape Town, Western Cape'\n\n"
                response += f"Attempts remaining: {3 - state['location_attempts']}"

    # Step 5: Time selection
    elif state['step'] == STEPS['TIME']:
        try:
            time_index = int(user_message) - 1
            if 0 <= time_index < len(TIME_OPTIONS):
                info['preferredTime'] = TIME_OPTIONS[time_index]
                state['step'] = STEPS['CONFIRMATION']
                response = "✅ Thank you! Here's a summary of your service request:\n\n"
                response += f"👤 Name: {info['name']}\n"
                response += f"📱 Phone: {info['phone']}\n"
                response += f"📧 Email: {info['email']}\n"
                response += f"📍 Address: {info['address']}\n"
                response += f"🔧 Issue Category: {info['issue_category']}\n"
                if info['issue_detail']:
                    response += f"📝 Issue Details: {info['issue_detail']}\n"
                response += f"⏰ Preferred Time: {info['preferredTime']}\n\n"
                response += "✅ Status: Service request submitted successfully!\n\n"
                response += "Our technician will contact you within 30 minutes to confirm the appointment.\n\n"
                response += "Thank you for choosing FridgeFix! 🙏"
            else:
                response = "❌ Invalid option. Please reply with a number between 1-4."
        except ValueError:
            response = "❌ Invalid option. Please reply with a number between 1-4."

    # Step 6: Completion - offer to start new request or exit
    elif state['step'] == STEPS['CONFIRMATION']:
        if user_message.lower() in ['yes', 'y', 'new', 'another']:
            # Reset conversation
            conversation_states[user_id] = {
                'step': STEPS['PHONE_CHECK'],
                'customerInfo': {
                    'name': '',
                    'phone': '',
                    'email': '',
                    'address': '',
                    'issue_category': '',
                    'issue_detail': '',
                    'applianceType': 'Refrigerator',
                    'preferredTime': ''
                },
                'phone_attempts': 0,
                'email_attempts': 0,
                'location_attempts': 0
            }
            response = "🔧 Welcome back to FridgeFix!\n\nPlease provide your phone number to get started:"
        else:
            state['step'] = STEPS['COMPLETED']
            response = "🙏 Thank you for contacting FridgeFix!\n\n"
            response += "We will follow up with you shortly.\n\n"
            response += "📧 Check your email for confirmation details.\n"
            response += "📱 Our technician will call you to confirm the appointment.\n\n"
            response += "If you need to submit another request, just type 'new' or 'yes'.\n\n"
            response += "Thank you for choosing FridgeFix! 🙏"

    elif state['step'] == STEPS['COMPLETED']:
        if user_message.lower() in ['yes', 'y', 'new', 'another']:
            # Reset conversation
            conversation_states[user_id] = {
                'step': STEPS['PHONE_CHECK'],
                'customerInfo': {
                    'name': '',
                    'phone': '',
                    'email': '',
                    'address': '',
                    'issue_category': '',
                    'issue_detail': '',
                    'applianceType': 'Refrigerator',
                    'preferredTime': ''
                },
                'phone_attempts': 0,
                'email_attempts': 0,
                'location_attempts': 0
            }
            response = "🔧 Welcome back to FridgeFix!\n\nPlease provide your phone number to get started:"
        else:
            response = "🙏 Thank you for using FridgeFix!\n\nWe will be in touch soon. Goodbye! 👋"

    else:
        response = "Thank you for using FridgeFix! Your request has been processed."

    return response

@app.route('/whatsapp', methods=['POST'])
def whatsapp_webhook():
    incoming_msg = request.values.get('Body', '').strip()
    sender_number = request.values.get('From', '')
    user_id = sender_number.replace('whatsapp:', '')

    # Initialize user if first message
    if user_id not in conversation_states:
        initialize_user(user_id)
        bot_response = "🔧 Welcome to FridgeFix!\n\n"
        bot_response += "Please provide your phone number to get started:"
    else:
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
