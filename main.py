import time
import httpx
import pandas as pd
import random

GEMINI_API_KEY = ("ENTER_YOUR_GEMINI_KEY")
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"


def analyze_finance_question(text, retries=3):
    if not text or text.isspace():
        return "Unknown", "Unknown", "No summary available"

    prompt = f"""
    Classify the following personal finance question into:
    Layer 1: What finance domain does the question belong to? Examples: spending, saving, budgeting, tax, loan, retirement, investment, etc.
    Layer 2: What is the nature of the question? Examples: definition request, plan construction, calculation request, seeking advice, etc.
    Additionally, generate a concise summary of the post in 2-3 sentences.

    Return the response in the format:
    Layer 1: <finance domain>
    Layer 2: <nature of question>
    Summary: <summary>

    Question: {text}
    """

    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    headers = {"Content-Type": "application/json"}
    params = {'key': GEMINI_API_KEY}

    for attempt in range(retries):
        try:
            response = httpx.post(GEMINI_API_URL, json=payload, headers=headers, params=params, timeout=30.0)
            response.raise_for_status()

            json_response = response.json()
            text_response = json_response.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get(
                "text", "Unknown\nUnknown\nNo summary available")
            lines = text_response.split("\n")

            layer_1 = lines[0].replace("Layer 1: ", "").strip() if len(lines) > 0 else "Unknown"
            layer_2 = lines[1].replace("Layer 2: ", "").strip() if len(lines) > 1 else "Unknown"
            summary = lines[2].replace("Summary: ", "").strip() if len(lines) > 2 else "No summary available"

            return layer_1, layer_2, summary

        except httpx.TimeoutException:
            print(f"Timeout error. Retrying {attempt + 1}/{retries}...")
            time.sleep(5)
        except Exception as e:
            print(f"Error in classification: {e}")
            return "Unknown", "Unknown", "No summary available"

    return "Unknown", "Unknown", "No summary available"


def scrape_reddit(subreddit, max_posts=5000):
    base_url = "https://www.reddit.com"
    endpoint = f"/r/{subreddit}.json"
    dataset = []
    headers = {"User-Agent": "Mozilla/5.0 (compatible; MyRedditScraper/1.0)"}

    post_counter = 0
    after = None
    retry_attempts = 100

    while post_counter < max_posts:
        params = {"limit": 100}
        if after:
            params["after"] = after

        for attempt in range(retry_attempts):
            try:
                response = httpx.get(base_url + endpoint, params=params, headers=headers, timeout=10.0)

                if response.status_code != 200:
                    raise Exception(f"Error {response.status_code}: {response.text}")

                json_data = response.json()
                posts = json_data.get("data", {}).get("children", [])
                after = json_data.get("data", {}).get("after")

                for post in posts:
                    if post_counter >= max_posts:
                        break

                    data = post["data"]
                    post_content = f"{data.get('title', '')}\n\n{data.get('selftext', '')}"

                    layer_1, layer_2, summary = analyze_finance_question(post_content)

                    dataset.append({
                        "id": data.get("id"),
                        "title": data.get("title"),
                        "selftext": data.get("selftext"),
                        "finance_domain": layer_1,
                        "question_nature": layer_2,
                        "summary": summary,
                        "url": data.get("url"),
                        "permalink": data.get("permalink"),
                        "created_utc": data.get("created_utc"),
                        "author": data.get("author"),
                        "num_comments": data.get("num_comments"),
                        "score": data.get("score"),
                        "upvote_ratio": data.get("upvote_ratio"),
                        "subreddit": data.get("subreddit"),
                    })

                    post_counter += 1
                    time.sleep(random.uniform(1.5, 3.5))

                break

            except Exception as e:
                wait_time = 2 ** attempt + random.uniform(0.5, 2.0)
                print(f"Error fetching data: {e}. Retrying in {wait_time:.2f} seconds...")
                time.sleep(wait_time)

        if not after:
            break

    df = pd.DataFrame(dataset)
    df.to_csv(f"reddit_{subreddit}_classified.csv", index=False)

    print(f"Data saved successfully! {len(dataset)} posts collected.")


subreddit = input("Enter the subreddit name: ")
scrape_reddit(subreddit)
