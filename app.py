# Installing Dependences
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from openai import OpenAI
import openai
import os
import re
from dotenv import load_dotenv
from openai import OpenAI
from flask_basicauth import BasicAuth
import random
#loading environment
load_dotenv()
import time

load_dotenv()
#creating basic auth
app = Flask(__name__)
# app.config['BASIC_AUTH_USERNAME'] = os.getenv("PASSWORD")
# app.config['BASIC_AUTH_PASSWORD'] = os.getenv("USERNAME")
app.config['BASIC_AUTH_USERNAME'] = 'Esteem'
app.config['BASIC_AUTH_PASSWORD'] = '29~DE6gjNJ&J'
basic_auth = BasicAuth(app)

openai.api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI()
assistant_id = "asst_wKTvrc2keK7keUy5LYy18XkZ"

@app.route('/', methods=['GET','POST'])
@basic_auth.required
def ask_question():
    try:
        user_question = request.json.get('user_question')
        user_location = request.json.get('location')
        user_doj = request.json.get('yearOfJoining')

        user_question = user_question + ", My location is " + str(user_location) + " , My date of joining" + str(user_doj)

        # Create a new thread for each question
        thread = client.beta.threads.create()
        print(thread.id)

        message = client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=user_question
        )

        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=assistant_id
        )

        while True:
            run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
            if run.status == "completed":
                break

        messages = client.beta.threads.messages.list(thread_id=thread.id)
        latest_message = messages.data[0]
        text = latest_message.content[0].text.value
        text = re.sub(r'[\[\]\(\)\{\}]', '', text)
        text = text.replace('\n', ' ')

        # Check if the response starts with "https"
        if text.strip().startswith("https"):
            # List of random texts to choose from
            random_texts = ["Sure!, Here's the Url you can refer to:", "To answer your query, you can refer to below mentioned URL that will provide more information on this", "Check this URL below for more info"]

            # Choose a random text from the list
            random_text = random.choice(random_texts)

            # Concatenate the random text with the GPT-3 response
            text = f"{random_text} {text.strip()}"

        return jsonify({'response': text, 'thread_id': thread.id})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
