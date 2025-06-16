from flask import Flask, render_template, request, jsonify
import openai
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from dotenv import load_dotenv
import os
from datetime import datetime

# Load environment variables
load_dotenv()

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")

def save_to_sheets(user_input, gpt_response):
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(creds)
    sheet = client.open("BIZZ-Task-Logs").sheet1
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sheet.append_row([now, user_input, gpt_response])

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    try:
        data = request.get_json()
        user_input = data.get('question', '')

        if not user_input.strip():
            return jsonify({'answer': "Please type something to ask BIZZ!"})

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content":
                 "You are BIZZ, a smart and helpful AI agent that gives actionable business advice. "
                 "After each response, ask: 'Do you want to save this or continue brainstorming?'" },
                {"role": "user", "content": user_input}
            ]
        )

        output = response["choices"][0]["message"]["content"]
        save_to_sheets(user_input, output)
        return jsonify({'answer': output})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
