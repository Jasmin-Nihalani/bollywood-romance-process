import pandas as pd
import requests
from urllib.parse import quote
from tqdm import tqdm
from time import sleep

# Load your Excel file
df = pd.read_excel("/Users/Jasmin.Nihalani/Desktop/lede_proj/imdb_records.xlsx")

# Define the query function with improved error handling
def get_wikipedia_url(title, year):
    query = f"{title} {year}"
    encoded_query = quote(query)
    api_url = f"https://en.wikipedia.org/w/api.php?action=query&format=json&list=search&formatversion=2&srsearch={encoded_query}"

    headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
}

    try:
        response = requests.get(api_url, headers=headers)

        # Check for HTTP error before attempting .json()
        if response.status_code != 200:
            print(f"HTTP error {response.status_code} for '{title}' ({year})")
            sleep(1)
            return None

        try:
            data = response.json()
        except ValueError:
            print(f"Invalid JSON for '{title}' ({year}) — raw response: {response.text[:100]}")
            sleep(1)
            return None

        results = data.get("query", {}).get("search", [])

        for result in results:
            page_title = result.get("title", "")
            snippet = result.get("snippet", "").lower()

            # Skip irrelevant list pages
            if page_title.lower().startswith("list of"):
                continue

            # Check if it's a film with keywords in the snippet
            if "film" in snippet and any(kw in snippet for kw in ["hindi", "indian", "bollywood"]):
                sleep(0.5)  # polite delay before returning
                return f"https://en.wikipedia.org/wiki/{page_title.replace(' ', '_')}"

        sleep(0.5)
        return None

    except Exception as e:
        print(f"Error processing '{title}' ({year}): {e}")
        sleep(1)
        return None

# Apply the function with a progress bar
tqdm.pandas()
df["wikipedia_url"] = df.progress_apply(lambda row: get_wikipedia_url(row["title"], row["year"]), axis=1)

# Save the final result
output_path = "/Users/Jasmin.Nihalani/Desktop/lede_proj/imdb_with_wiki_urls.csv"
df.to_csv(output_path, index=False)

print(f"✅ Done! Wikipedia URLs saved to: {output_path}")
