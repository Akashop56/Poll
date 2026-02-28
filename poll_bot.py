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
    return json.loads(response.text.replace('```json', '').replace('```', '').strip())

def post_to_youtube():
    poll = generate_poll()
    cookies = json.loads(os.environ["YOUTUBE_COOKIES"])

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        context.add_cookies(cookies)
        page = context.new_page()

        # YouTube Community Page par jana
        page.goto("https://www.youtube.com/community")
        time.sleep(5)

        # Poll Button par click (Selectors may vary, but these are standard)
        page.click("text=Poll") # Ya fir 'Text poll' selector
        time.sleep(2)

        # Title aur Options bharna
        page.fill('placeholder="Ask a question..."', poll['title'])
        inputs = page.query_selector_all('input[placeholder="Add option"]')
        for i, opt in enumerate(poll['options']):
            inputs[i].fill(opt)

        # Post Button dabana
        page.click("text=Post")
        print(f"Successfully posted: {poll['title']}")
        time.sleep(2)
        browser.close()

if __name__ == "__main__":
    post_to_youtube()
