![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Flask](https://img.shields.io/badge/Flask-Web_App-orange)
![License](https://img.shields.io/github/license/m3d4r-commits/LLM-Compare)
# LLM Comparison Web App

This project is a Flask-based web application that allows users to compare responses from multiple Large Language Models (LLMs) and analyze their differences. It supports models like Gemini 2.5 Pro, ChatGPT 3.5-turbo, and DeepSeek v3, with analysis powered by either Claude 3 or ChatGPT.

## Features

- Query multiple LLMs simultaneously and compare their responses.
- Analyze differences between LLM responses using Claude 3 or ChatGPT.
- Toggle between themes, including a "Matrix Mode" for a retro aesthetic.
- Responsive design with a retro MS-DOS-inspired theme.

## Project Structure

```plaintext
.env                # Environment variables (API keys)
.gitignore          # Git ignore file
askllm.py           # Main Flask application
static/
    styles.css      # Custom CSS for the web app
templates/
    index.html      # HTML template for the web app
```

## Prerequisites

- Python 3.8 or higher
- Flask
- API keys for OpenAI, Google Generative AI, DeepSeek, and Anthropic

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/m3d4r-commits/LLM-Compare
   cd llm-webapp
   ```

2. Create a virtual environment and activate it:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the root directory and add your API keys:
   ```plaintext
   OPENAI_API_KEY=your_openai_api_key
   GOOGLE_API_KEY=your_google_api_key
   DEEPSEEK_API_KEY=your_deepseek_api_key
   ANTHROPIC_API_KEY=your_anthropic_api_key
   ```

## Usage

1. Start the Flask server:
   ```bash
   python askllm.py
   ```

2. Open your browser and navigate to:
   ```
   http://127.0.0.1:5000/
   ```

3. Enter a question, select an analysis model, and compare the responses.

## Customization

- **Themes**: Modify the `static/styles.css` file to customize the appearance.
- **Matrix Mode**: The "Matrix Mode" can be toggled using the button in the UI.

## API Integration

- **Gemini 2.5 Pro**: Uses Google Generative AI API.
- **ChatGPT 3.5-turbo**: Uses OpenAI API.
- **DeepSeek3**: Uses DeepSeek API.
- **Claude 3**: Uses Anthropic API for analysis.

## Security

- Ensure your `.env` file is listed in `.gitignore` to prevent accidental exposure of API keys.
- Do not share your API keys publicly.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

## Acknowledgments

- [Flask](https://flask.palletsprojects.com/) for the web framework.
- [OpenAI](https://openai.com/), [Google Generative AI](https://ai.google/), [DeepSeek](https://deepseek.com/), and [Anthropic](https://www.anthropic.com/) for their APIs.