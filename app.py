from flask import Flask, request
import openai
import requests
import API_KEYS


app = Flask(__name__)

# Set your ChatGPT API key
OPENAI_API_KEY = API_KEYS.OPENAI_API_KEY

# Set your Africa's Talking API key
AFRICASTALKING_API_KEY = API_KEYS.AFRICASTALKING_API_KEY

# Bot's name
bot_name = "KISHERIA BOT"

# Language for the bot
bot_language = "sw"  # Swahili

# Topic for the conversation
conversation_topic = "Sheria"  # Agriculture in Swahili

# Greeting message in Swahili
greeting = f"{bot_name}: Karibu! Mimi ni {bot_name}. {conversation_topic}\nLanguage: {bot_language}"


# Function to interact with the bot
def chat_with_bot(bot_name, language, topic, user_message, conversation_history=None):
    # Create system and user messages
    system_message = f"{bot_name}: Karibu! Mimi ni {bot_name}. {topic}\nLugha: {language}"
    user_message = f"User: {user_message}"

    # Combine system and user messages with existing conversation history
    messages = [{"role": "system", "content": system_message}]

    if conversation_history:
        messages += conversation_history

    messages.append({"role": "user", "content": user_message})

    # Make the API call for chat completion
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=150,
        api_key=API_KEYS.OPENAI_API_KEY
    )

    # Extract and return the assistant's reply
    assistant_reply = response['choices'][0]['message']['content']

    # Extract the updated conversation history for future interactions
    updated_history = messages + [{"role": "assistant", "content": assistant_reply}]

    return assistant_reply, updated_history


@app.route('/')
def smart_shamba():
    return 'Lima Kijanja'


@app.route('/sms_callback', methods=['POST'])
def sms_callback():
    user_message = request.form["text"]
    sender = request.form["from"]

    # Check for common greetings and respond with the greeting message
    if user_message.lower() in ["habari", "hello", "mambo"]:
        bot_response = greeting
    else:
        # Use the user's SMS message with the bot's name, language, and topic as the prompt
        bot_response = chat_with_bot(
            bot_name, bot_language, conversation_topic, user_message)

    # Send the bot response to the user via Africa's Talking SMS API
    response_to_sms(sender, bot_response)

    return "Success", 201


def response_to_sms(recipient_phone_number, message):
    url = "https://api.sandbox.africastalking.com/version1/messaging"
    data = {
        "username": "sandbox",
        "to": recipient_phone_number,
        "message": message,
        "from": "3607"
    }
    headers = {
        "apikey": AFRICASTALKING_API_KEY,
        "Accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    try:
        response = requests.post(url, data=data, headers=headers)
        print(f"API Request: {data}")
        print(f"API Response: {response.text}")

        # Check if the SMS was sent successfully
        if response.status_code != 201:
            raise Exception(f"Failed to send SMS. Status code: {response.status_code}")

    except Exception as e:
        print(f"Failed to send SMS: {str(e)}")
        raise Exception(f"Failed to send SMS: {str(e)}")


if __name__ == '__main__':
    app.run(debug=True)

