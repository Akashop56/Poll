from google import genai
import json, os, time, re
from playwright.sync_api import sync_playwright

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

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
    response = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
    json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
    return json.loads(json_match.group())

def post_to_youtube():
    try:
        poll = generate_poll()
        cookies = json.loads(os.environ["YOUTUBE_COOKIES"])
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
            context.add_cookies(cookies)
            page = context.new_page()
            page.goto("https://www.youtube.com/community", wait_until="networkidle")
            time.sleep(10)
            page.get_by_label("Create a text poll").click()
            time.sleep(3)
            page.get_by_placeholder("Ask a question").fill(poll['title'])
            inputs = page.query_selector_all('input[placeholder="Add option"]')
            for i, opt in enumerate(poll['options'][:4]): inputs[i].fill(opt)
            page.get_by_label("Post").click()
            time.sleep(5)
            print("Successfully Posted!")
            browser.close()
    except Exception as e: print(f"Error: {e}")

if __name__ == "__main__": post_to_youtube()
