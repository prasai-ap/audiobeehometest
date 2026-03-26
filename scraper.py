from playwright.sync_api import sync_playwright
import json

BASE_URL = "https://ekantipur.com"


# -----------------------------
# Scrape Entertainment News
# -----------------------------
def scrape_entertainment(page):
    page.goto(f"{BASE_URL}/entertainment")

    # wait for full page load (important for dynamic content)
    page.wait_for_load_state("networkidle")

    news_data = []

    # correct selector (articles contain news cards)
    cards = page.query_selector_all("article")[:5]

    for card in cards:
        try:
            # title
            title_el = card.query_selector("h2 a, h3 a")
            title = title_el.text_content().strip() if title_el else None

            # image
            image_el = card.query_selector("img")
            image_url = image_el.get_attribute("src") if image_el else None

            # category
            category_el = card.query_selector(".category")
            category = category_el.text_content().strip() if category_el else "मनो रञ्जन"

            # author (may not exist)
            author_el = card.query_selector(".author")
            author = author_el.text_content().strip() if author_el else None

            news_data.append({
                "title": title,
                "image_url": image_url,
                "category": category,
                "author": author
            })

        except Exception as e:
            print("Error scraping news:", e)

    return news_data


# -----------------------------
# Scrape Cartoon of the Day
# -----------------------------
def scrape_cartoon(page):
    page.goto(f"{BASE_URL}/cartoon")

    # wait for cartoon section
    page.wait_for_selector(".cartoon-wrapper")

    try:
        card = page.query_selector(".cartoon-wrapper")

        # title + author combined
        desc = card.query_selector(".cartoon-description p").text_content().strip()

        # split title and author
        if "-" in desc:
            parts = desc.split("-")
            title = parts[0].strip()
            author = parts[1].strip()
        else:
            title = desc
            author = None

        # image (lazy loaded)
        img = card.query_selector("img")
        image_url = img.get_attribute("data-src") or img.get_attribute("src")

        return {
            "title": title,
            "image_url": image_url,
            "author": author
        }

    except Exception as e:
        print("Error scraping cartoon:", e)
        return {
            "title": None,
            "image_url": None,
            "author": None
        }


# -----------------------------
# Main Function
# -----------------------------
def main():
    print("Scraping started...")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        # increase timeout (important)
        page.set_default_timeout(60000)

        # scrape both sections
        entertainment = scrape_entertainment(page)
        cartoon = scrape_cartoon(page)

        # final output
        output = {
            "entertainment_news": entertainment,
            "cartoon_of_the_day": cartoon
        }

        # save JSON (Nepali text support)
        with open("output.json", "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)

        browser.close()

    print("Scraping completed. Data saved to output.json")


# -----------------------------
# Run Script
# -----------------------------
if __name__ == "__main__":
    main()