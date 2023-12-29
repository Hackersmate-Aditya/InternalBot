from flask import Flask, request, jsonify
from dotenv import load_dotenv
from openai import OpenAI
import openai
import os
from dotenv import load_dotenv
from openai import OpenAI
from flask_basicauth import BasicAuth


load_dotenv()
import time

load_dotenv()

app = Flask(__name__)
# app.config['BASIC_AUTH_USERNAME'] = os.getenv("PASSWORD")
# app.config['BASIC_AUTH_PASSWORD'] = os.getenv("USERNAME")
app.config['BASIC_AUTH_USERNAME'] = 'aa'
app.config['BASIC_AUTH_PASSWORD'] = 'aaa'
basic_auth = BasicAuth(app)

openai.api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI()
assistant_id = "asst_jTnYZT8jOc3YUuKPUD0K9f9I"
thread = None

@app.route('/ask', methods=['POST'])
@basic_auth.required
def ask_question():
    try:
        global thread
        user_question = request.json.get('user_question')
        a_thread = request.json.get('thread_id')

        if not a_thread:
            if not thread:
                thread = client.beta.threads.create()
                print(thread.id)
                print(thread)
        else:
            if not thread:
                thread = client.beta.threads.create()
            thread.id = a_thread
            print(thread.id)
            print(thread)

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

        return jsonify({'response': text, 'thread_id': thread.id})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(port=5000)
