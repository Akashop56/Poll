import google.generativeai as genai
import json
import os
import time
from playwright.sync_api import sync_playwright

# AI Setup
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

def generate_poll():
    prompt = """
You are an expert Indian Cricket content creator for YouTube.
Generate a highly engaging, short YouTube community text poll about currently trending cricket (IPL, Indian Team, T20, Virat Kohli, MS Dhoni, Rohit Sharma, etc.).

Rules:
1. Title must be very short, catchy, and easy to read.
2. Provide EXACTLY 4 options.
3. Options must be aesthetic, short, and use emojis (e.g., 💛 MS Dhoni (Captain Cool), 💙 Rohit Sharma (Hitman)).
4. The 4th option should usually be an interaction bait like "🏏 Other (Comment your pick!)" or "State Rivalries (Comment yours!)".
5. OUTPUT STRICTLY IN JSON FORMAT like this:
{
  "title": "Which IPL match is the El Clásico for you?",
  "options": ["RCB ♥️ vs KKR 💜", "CSK 💛 vs MI 💙", "SRH 🧡 vs RR 💗", "Other (Comment yours!) 🏏"]
}
"""
    response = model.generate_content(prompt)
    clean_json = response.text.strip().replace('```json', '').replace('```', '')
    return json.loads(clean_json)

def post_to_youtube():
    try:
        poll = generate_poll()
        cookies = json.loads(os.environ["YOUTUBE_COOKIES"])

        with sync_playwright() as p:
            # Browser thoda slow chalayenge taaki YouTube bot na samjhe
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
            context.add_cookies(cookies)
            page = context.new_page()

            print("Opening YouTube Community...")
            page.goto("https://www.youtube.com/community", wait_until="networkidle")
            time.sleep(5)

            # Poll button dhundna (YouTube naya interface)
            print("Clicking Poll Button...")
            page.get_by_label("Create a text poll").click()
            time.sleep(2)

            # Question bharna
            page.get_by_placeholder("Ask a question").fill(poll['title'])
            
            # Options bharna
            options_inputs = page.query_selector_all('input[placeholder="Add option"]')
            for i, opt in enumerate(poll['options'][:4]):
                options_inputs[i].fill(opt)

            # Post Button
            print("Posting...")
            page.get_by_label("Post").click()
            time.sleep(3)
            print("Successfully Posted!")
            browser.close()
    except Exception as e:
        print(f"Galti hui bhai: {e}")

if __name__ == "__main__":
    post_to_youtube()
