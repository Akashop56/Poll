from google import genai
import json
import os
import time
import re
from playwright.sync_api import sync_playwright

# Naya AI Setup (2026 Update)
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

def generate_poll():
    # Aapka Favorite Custom Prompt
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
    
    # Naye model 'gemini-2.0-flash' ka use
    response = client.models.generate_content(
        model="gemini-2.0-flash", 
        contents=prompt
    )
    
    # JSON nikalne ke liye safety regex
    json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
    if json_match:
        return json.loads(json_match.group())
    else:
        raise ValueError("AI ne sahi JSON format nahi diya.")

def post_to_youtube():
    try:
        poll = generate_poll()
        print(f"Poll Ready: {poll['title']}")
        
        cookies_json = os.environ["YOUTUBE_COOKIES"]
        cookies = json.loads(cookies_json)

        with sync_playwright() as p:
            # Headless mode mein browser chalana
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
            context.add_cookies(cookies)
            page = context.new_page()

            print("Opening YouTube Community Tab...")
            page.goto("https://www.youtube.com/community", wait_until="networkidle")
            time.sleep(10) # 10 seconds ka wait taaki bada channel aaram se load ho

            # Poll button par click karna
            print("Clicking Poll Button...")
            page.get_by_label("Create a text poll").click()
            time.sleep(3)

            # Question bharna
            print("Entering Question and Options...")
            page.get_by_placeholder("Ask a question").fill(poll['title'])
            
            # Options bharna
            inputs = page.query_selector_all('input[placeholder="Add option"]')
            for i, opt in enumerate(poll['options'][:4]):
                inputs[i].fill(opt)

            # Post karna
            print("Clicking Post...")
            page.get_by_label("Post").click()
            time.sleep(5)
            
            print("Success! Aapka poll YouTube par post ho gaya hai.")
            browser.close()
            
    except Exception as e:
        print(f"Galti hui: {e}")

if __name__ == "__main__":
    post_to_youtube()
