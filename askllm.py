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
        raise ValueError(f"{key} not found. Please set it in a .env file.")

# Clients
client = OpenAI()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
anthropic_client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

app = Flask(__name__)

def query_llm_1(question):
    """Query Gemini 2.5 Pro and return the text response."""
    try:
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(question)
        return response.text
    except Exception as e:
        logger.exception("Error querying Gemini")
        return f"Error with Gemini (LLM 1): {str(e)}"

def query_llm_2(question):
    """Query ChatGPT 3.5-turbo and return the text response."""
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
        return f"Error with ChatGPT (LLM 2): {str(e)}"

def query_llm_3(question):
    """Query DeepSeek v3 and return the text response."""
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
        return f"Error with DeepSeek (LLM 3): {str(e)}"

def analyze_differences_with_llm_4(responses, analyzer="claude"):
    """Use Claude 3 or ChatGPT to analyze the differences between responses."""
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
        return f"Error during analysis (LLM 4 - {analyzer}): {str(e)}"


def _analysis_worker(futures, mapping, analyzer):
    """Wait for LLM futures, gather results in order, and run analysis."""
    responses = [None] * len(futures)
    for future in futures:
        idx = mapping[future]
        responses[idx] = future.result()
    return analyze_differences_with_llm_4(responses, analyzer=analyzer)

@app.route("/", methods=["GET", "POST"])
def home():
    """Render the main page and handle question submission."""
    result_1 = result_2 = result_3 = analysis = ""
    times = {}
    analyzer_choice = "claude"

    if request.method == "POST":
        question = request.form.get("question")
        analyzer_choice = request.form.get("analyzer", "claude")
        functions = [query_llm_1, query_llm_2, query_llm_3]
        results = [None, None, None]
        start_times = {}

        with ThreadPoolExecutor(max_workers=4) as executor:
            future_to_index = {}
            for idx, func in enumerate(functions):
                start_times[idx] = time.time()
                future = executor.submit(func, question)
                future_to_index[future] = idx

            analysis_future = executor.submit(
                _analysis_worker,
                list(future_to_index.keys()),
                future_to_index,
                analyzer_choice,
            )

            for future in as_completed(future_to_index):
                idx = future_to_index[future]
                try:
                    result = future.result()
                except Exception as e:
                    logger.exception("Error executing LLM %s", idx + 1)
                    result = f"Error running LLM {idx + 1}: {str(e)}"
                finally:
                    elapsed = round(time.time() - start_times[idx], 2)
                    times[f"LLM {idx + 1}"] = elapsed
                    results[idx] = result

            analysis = analysis_future.result()
            result_1, result_2, result_3 = results


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
