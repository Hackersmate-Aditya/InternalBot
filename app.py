import time
from flask import Flask, request, jsonify
from openai import OpenAI
from flask_basicauth import BasicAuth
import os
import re
import random
import openai
import asyncio
from dotenv import load_dotenv
import gc
import asyncio

# Loading environment variables
load_dotenv()

# Creating basic auth
app = Flask(__name__)
app.config['BASIC_AUTH_USERNAME'] = 'Esteem'
app.config['BASIC_AUTH_PASSWORD'] = '29~DE6gjNJ&J'
basic_auth = BasicAuth(app)

# OpenAI setup
OpenAI.api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI()
assistant_id = "asst_PQhmvRHRqlllXtysPdf1vQV3"
# assistant_id = "asst_N6auFrBmUxrqSFwUHZYQ0xnq"

# thread = None

async def process_question(user_question, user_location, user_doj):
    try:
        # time.sleep(3.5)
        print("Inside process_question")
        thread = client.beta.threads.create(timeout=2)
        print("After thread create")
        user_question = user_question.lower()

        # a_thread = None

        def create_new_thread():
            new_thread = client.beta.threads.create(timeout=2)
            new_message = client.beta.threads.messages.create(
                timeout=2,
                thread_id=new_thread.id, content=user_question, role="user"
            )
            return new_thread

        # if not a_thread:
        #     if not thread:
        #         thread = client.beta.threads.create()
        #         print(thread.id)
        #         print(thread)
        # else:
        #     if not thread:
        #         thread = client.beta.threads.create()
        #     thread.id = a_thread
        #     print(thread.id)
        #     print(thread)

        message = client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=user_question,timeout=2
        )
        print("After message")

        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=assistant_id,timeout=2
            # print("Inside run ")
        )
        print("After run")


        while True:
            try:
                run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id, timeout=3)
                if run.status == "completed":
                    break
            except openai.error.OpenAIError as e:
                # Handle the case where the run is not found (404 error)
                if 'No run found' in str(e):
                    print(f"Run not found. Creating a new thread.")
                    client.beta.threads.delete(thread.id)
                    thread = create_new_thread()
                    message = client.beta.threads.messages.create(
                        thread_id=thread.id, content=user_question, role="user"
                    )
                    run = client.beta.threads.runs.create(
                        thread_id=thread.id,
                        assistant_id=assistant_id
                    )
                else:
                    raise


        messages = client.beta.threads.messages.list(thread_id=thread.id,timeout=3)
        latest_message = messages.data[0]
        text = latest_message.content[0].text.value
        text = re.sub(r'[\[\]\(\)\{\}]', '', text)
        text = text.replace('\n', ' ')

        if text.strip().startswith("https"):
            random_texts = ["Sure!, Here's the URL you can refer to:", "To answer your query, you can refer to below mentioned URL that will provide more information on this", "Check this URL below for more info"]
            random_text = random.choice(random_texts)
            text = f"{random_text} {text.strip()}"
            print(text)

        if text.count("https") > 1:
            text = f"Here are several URLs pertinent to your inquiry. Please select the one that best matches your needs. To ensure greater accuracy in the results, please furnish additional details in your queries {text}"

        opinion_text = ['We value your feedback! Share your thoughts with us at:', 'To share your opinion, please visit the following link:','Have something to say? Your opinion matters! Click here:','Express yourself and share your opinions here:','Opinions welcome! Let us know what you think at:']
        feedback_link = "https://feedback.creatingwow.in/"
        if user_question == 'opinion':
            text = text.replace(text,'')
            random_text_opinion = random.choice(opinion_text) + feedback_link
            text = f"{random_text_opinion}"

        report_text = ['To submit a report, please use the following link:','Report any issues or concerns using this link:','Help us by submitting a report through the following link:','If you need to file a report, click on the following link:','Use the following link to submit feedback or report any issues:']
        if user_question == 'report':
            text = text.replace(text,'')
            random_text_report = random.choice(report_text) + feedback_link
            text = f"{random_text_report}"

        ananymous_text = ['Provide anonymous feedback by visiting the following link:','For anonymous reporting, please visit this link:','Your privacy is assured. Submit feedback anonymously:','Make suggestions anonymously by clicking on this link:']
        if user_question == 'anonymous':
            text = text.replace(text,'')
            random_text_anonymous = random.choice(ananymous_text) + feedback_link
            text = f"{random_text_anonymous}"

        response_text = ['Share your response with us by visiting the following link:','Submit your response easily through this link:','Share your thoughts and responses by clicking here:','Give your feedback and response using this link:','We value your response! Respond to us by visiting:','Open the response gateway and submit your thoughts at:']
        if user_question == 'response':
            text = text.replace(text,'')
            random_text_response = random.choice(response_text) + feedback_link
            text = f"{random_text_response}"

        if "https://itsupport.infobeans.com/support/solutions/folders/22222222" in text:
            text = text.replace("https://itsupport.infobeans.com/support/solutions/folders/22222222","https://itsupport.infobeans.com/support/solutions/folders/27000104399?page=2&per_page=10")

        if "https://itsupport.infobeans.com/support/solutions/folders/44444444" in text:
            text = text.replace("https://itsupport.infobeans.com/support/solutions/folders/44444444","https://itsupport.infobeans.com/support/solutions/folders/27000104399")

        if "https://itsupport.infobeans.com/support/solutions/folders/33333333" in text:
            text = text.replace("https://itsupport.infobeans.com/support/solutions/folders/33333333","https://itsupport.infobeans.com/support/solutions/folders/27000104399?page=3&per_page=10")

        if "https://infobeans_admin_committee" in text:
            if user_location == "Pune":
                text = text.replace("https://infobeans_admin_committee","https://docs.google.com/forms/d/e/1FAIpQLSemXT1GOuBftcj9w2-0W3NZRXGL0eCSWZ9dDsj9uy7Dv5PDcw/viewform")
            elif user_location in ["Indore","Chennai","Vadodara", "Bangalore"]:
                text = text.replace("https://infobeans_admin_committee","https://docs.google.com/forms/d/e/1FAIpQLSfsR415c0QuF5F9bEXi6RSrP1pSzkGX2Z8To3SkqGuqkbXUxg/viewform?pli=1")

        if "https://payroll.creatingwow.in/" in text:
            if user_location == "Chennai":
                text = text.replace("https://payroll.creatingwow.in/","https://payroll.creatingwow.in/chennai")
            elif user_location == "Pune":
                text = text.replace("https://payroll.creatingwow.in/","https://payroll.creatingwow.in/sezpune")
            elif user_location == "Vadodara":
                text = text.replace("https://payroll.creatingwow.in/","https://payroll.creatingwow.in/unit_3")
            elif user_location == "Bangalore":
                text = text.replace("https://payroll.creatingwow.in/","https://payroll.creatingwow.in/unit_3")
            elif user_location == "Indore":
                if user_doj >= 2011:
                    text = text.replace("https://payroll.creatingwow.in/", "https://payroll.creatingwow.in/unit_3")
                elif user_doj < 2011:
                    text = text.replace("https://payroll.creatingwow.in/", "https://payroll.creatingwow.in/SEZINDORE")

        text = text.replace("https://payroll.creatingwow.in/unit_3#/", "https://payroll.creatingwow.in/unit_3")

        gc.collect()
        return {'response': text, 'thread_id': thread.id}

    except Exception as e:
        return {'error': str(e)}

# Route for handling questions asynchronously
@app.route('/', methods=['POST','GET'])
@basic_auth.required
def ask_question():
    try:
        start_time = time.time()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        user_question = request.json.get('user_question')
        user_location = request.json.get('location')
        user_doj = request.json.get('yearOfJoining')
        user_doj = int(user_doj)
        user_question = user_question.lower()

        # text, new_thread_id = asyncio.run(process_question(user_question, user_location, user_doj, thread))

        # Run the asynchronous function within the event loop
        result = loop.run_until_complete(
            process_question(user_question, user_location, user_doj)
        )
        print("--- %s seconds ---" % (time.time() - start_time))

        # loop.close()
        # return jsonify({'response': text, 'thread_id': new_thread_id})
        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
