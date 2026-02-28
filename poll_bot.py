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
    Generate a very short, catchy YouTube cricket poll about IPL or Indian Cricket Team.
    Format: JSON only. 
    Title: Max 60 chars. 
    Options: Exactly 4 short options with emojis. 
    The 4th option must be 'Other (Comment!) 🏏'.
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
