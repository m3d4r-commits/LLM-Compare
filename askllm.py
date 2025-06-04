from flask import Flask, request, render_template
import time
import os
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed
from openai import OpenAI
import google.generativeai as genai
import requests
import anthropic
import logging

# Configure logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
required_keys = ["OPENAI_API_KEY", "GOOGLE_API_KEY", "DEEPSEEK_API_KEY", "ANTHROPIC_API_KEY"]
for key in required_keys:
    if not os.getenv(key):
        raise ValueError(f"{key} is niet gevonden. Zet deze in een .env bestand.")

# Clients
client = OpenAI()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
anthropic_client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

app = Flask(__name__)

def query_llm_1(question):
    try:
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(question)
        return response.text
    except Exception as e:
        logger.exception("Error querying Gemini")
        return f"Fout bij Gemini (LLM 1): {str(e)}"

def query_llm_2(question):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Je bent een behulpzame AI."},
                {"role": "user", "content": question}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.exception("Error querying ChatGPT")
        return f"Fout bij ChatGPT (LLM 2): {str(e)}"

def query_llm_3(question):
    try:
        headers = {
            "Authorization": f"Bearer {os.getenv('DEEPSEEK_API_KEY')}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": "Je bent een behulpzame AI."},
                {"role": "user", "content": question}
            ]
        }
        response = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            json=payload,
            headers=headers,
            timeout=30,
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        logger.exception("Error querying DeepSeek")
        return f"Fout bij DeepSeek (LLM 3): {str(e)}"

def analyze_differences_with_llm_4(responses, analyzer="claude"):
    try:
        combined = "\n".join([f"LLM {i+1}: {r}" for i, r in enumerate(responses)])
        prompt = f"Analyseer deze drie antwoorden:\n\n{combined}"

        if analyzer == "claude":
            message = anthropic_client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=1024,
                temperature=0.7,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return "".join([c.text for c in message.content])
        else:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Je bent een taalmodel dat analyseert."},
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message.content

    except Exception as e:
        logger.exception("Error during analysis")
        return f"Fout bij analyse (LLM 4 - {analyzer}): {str(e)}"

@app.route("/", methods=["GET", "POST"])
def home():
    result_1 = result_2 = result_3 = analysis = ""
    times = {}
    analyzer_choice = "claude"

    if request.method == "POST":
        question = request.form.get("question")
        analyzer_choice = request.form.get("analyzer", "claude")
        functions = [query_llm_1, query_llm_2, query_llm_3]
        results = [None, None, None]
        start_times = {}

        with ThreadPoolExecutor(max_workers=3) as executor:
            future_to_index = {}
            for idx, func in enumerate(functions):
                start_times[idx] = time.time()
                future = executor.submit(func, question)
                future_to_index[future] = idx

            for future in as_completed(future_to_index):
                idx = future_to_index[future]
                try:
                    result = future.result()
                except Exception as e:
                    logger.exception("Error executing LLM %s", idx + 1)
                    result = f"Fout bij LLM {idx + 1}: {str(e)}"
                finally:
                    elapsed = round(time.time() - start_times[idx], 2)
                    times[f"LLM {idx + 1}"] = elapsed
                    results[idx] = result

        result_1, result_2, result_3 = results
        analysis = analyze_differences_with_llm_4(results, analyzer=analyzer_choice)

    return render_template("index.html",
                           result_1=result_1,
                           result_2=result_2,
                           result_3=result_3,
                           analysis=analysis,
                           times=times,
                           analyzer_choice=analyzer_choice)

if __name__ == "__main__":
    debug = os.getenv("FLASK_DEBUG", "False").lower() == "true"
    app.run(debug=debug)
