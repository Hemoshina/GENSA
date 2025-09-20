import os
from flask import Flask, request, jsonify, send_from_directory
from dotenv import load_dotenv
import wikipediaapi
from openai import OpenAI
import google.generativeai as genai

# Load environment variables
load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "../frontend")

app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path="/")

# ✅ Wikipedia setup
wiki_wiki = wikipediaapi.Wikipedia(
    language="en",
    user_agent="GenAI-App/1.0 (https://example.com; contact@example.com)"
)

# ✅ OpenAI setup
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ✅ Gemini setup (updated for latest SDK)
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

@app.route("/api/query", methods=["POST"])
def api_query():
    body = request.get_json(force=True)
    query = body.get("query", "").strip()

    if not query:
        return jsonify({"error": "Query is required"}), 400

    # Step 1: Wikipedia
    page = wiki_wiki.page(query)
    wiki_summary = page.summary[0:500] if page.exists() else "No results found on Wikipedia."

    # Step 2: OpenAI
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful AI assistant for career and course guidance."},
                {"role": "user", "content": f"Provide detailed guidance about: {query}"}
            ]
        )
        ai_summary = response.choices[0].message.content.strip()
    except Exception as e:
        ai_summary = f"OpenAI error: {str(e)}"

    # Step 3: Gemini / Google Generative AI
    try:
        gemini_response = genai.chat.create(
            model="models/chat-bison-001",
            messages=[{"author": "user", "content": f"Provide detailed guidance about: {query}"}]
        )
        gemini_summary = gemini_response.last.strip() if gemini_response and gemini_response.last else "No response from Gemini."
    except Exception as e:
        gemini_summary = f"Gemini error: {str(e)}"

    # Step 4: Merge all results
    return jsonify({
        "wikipedia": wiki_summary,
        "openai": ai_summary,
        "gemini": gemini_summary,
        "final_answer": (
            f"📘 Wikipedia:\n{wiki_summary}\n\n"
            f"🤖 OpenAI:\n{ai_summary}\n\n"
            f"✨ Gemini:\n{gemini_summary}"
        )
    })


# ✅ Serve frontend
@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def frontend(path):
    if path and os.path.exists(os.path.join(FRONTEND_DIR, path)):
        return send_from_directory(FRONTEND_DIR, path)
    return send_from_directory(FRONTEND_DIR, "index.html")


if __name__ == "__main__":
    app.run(debug=True, port=5000)
