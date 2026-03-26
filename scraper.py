from playwright.sync_api import sync_playwright
import json

BASE_URL = "https://ekantipur.com"

def scrape_entertainment(page):
    page.goto(f"{BASE_URL}/entertainment")
    page.wait_for_selector(".category-inner-wrapper")  # Wait for the article container

    news_data = []

    # Get the first 5 article blocks
    articles = page.query_selector_all(".category-inner-wrapper")[:5]

    for article in articles:
        # Title
        title_el = article.query_selector(".category-description h2 a")
        title = title_el.text_content().strip() if title_el else None

        # Image (sibling container)
        img_el = article.query_selector(".category-image img") or article.query_selector(".category-image img")
        image_url = img_el.get_attribute("data-src") or img_el.get_attribute("src") if img_el else None

        # Category is fixed
        category = "मनो रञ्जन"

        # Author
        author_el = article.query_selector(".author-name a")
        author = author_el.text_content().strip() if author_el else None

        news_data.append({
            "title": title,
            "image_url": image_url,
            "category": category,
            "author": author
        })

    return news_data

def scrape_cartoon(page):
    page.goto(f"{BASE_URL}/cartoon")
    page.wait_for_selector(".cartoon-wrapper")

    card = page.query_selector(".cartoon-wrapper")
    desc = card.query_selector(".cartoon-description p").text_content().strip()

    if "-" in desc:
        parts = desc.split("-")
        title = parts[0].strip()
        author = parts[1].strip()
    else:
        title = desc
        author = None

    img = card.query_selector("img")
    image_url = img.get_attribute("data-src") or img.get_attribute("src")

    return {
        "title": title,
        "image_url": image_url,
        "author": author
    }

def main():
    print("Scraping started...")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        entertainment = scrape_entertainment(page)
        cartoon = scrape_cartoon(page)

        output = {
            "entertainment_news": entertainment,
            "cartoon_of_the_day": cartoon
        }

        with open("output.json", "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)

        browser.close()
        print("Scraping finished!")

if __name__ == "__main__":
    main()