from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import json
from dotenv import load_dotenv
import os

load_dotenv()

EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")

options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")



def accept_cookies(driver):
    """Accept cookie consent if present."""
    try:
        cookie_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Akceptuj wszystkie')]"))
        )
        cookie_button.click()
    except Exception:
        pass


def enter_credentials(driver, email, password):
    """Enter login credentials and submit."""
    email_input = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email']"))
    )
    email_input.send_keys(email)
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

    password_input = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='password']"))
    )
    password_input.send_keys(password)
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()


def login(driver, email, password):
    """Perform login sequence."""
    driver.get("https://login.pracuj.pl/")
    accept_cookies(driver)
    enter_credentials(driver, email, password)
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//h1[contains(text(), 'Nowe konto już jest')]"))
        )
    except Exception:
        pass


def parse_offer(offer):
    """Extract job offer details from HTML."""
    star_button = offer.find("button", attrs={"data-test": "add-to-favourites"})
    if star_button and star_button.get("data-test-checkboxstate") == "true":
        return None

    if offer.find("div", attrs={"data-test": "applied-text"}):
        return None

    title = offer.find("h2", attrs={"data-test": "offer-title"})
    company = offer.find("h3", attrs={"data-test": "text-company-name"})
    location = offer.find("h4", attrs={"data-test": "text-region"})
    link_tag = offer.find("a", attrs={"data-test": "link-offer"})
    tech_tags = offer.find_all("span", attrs={"data-test": "technologies-item"})

    return {
        "title": title.get_text(strip=True) if title else None,
        "company": company.get_text(strip=True) if company else None,
        "location": location.get_text(strip=True) if location else None,
        "link": link_tag["href"] if link_tag and "href" in link_tag.attrs else None,
        "technologies": [tech.get_text(strip=True) for tech in tech_tags],
    }


def scrape_jobs():
    """Main scraping logic."""
    driver = webdriver.Chrome(service=ChromeService(), options=options)
    results = []

    try:
        login(driver, EMAIL, PASSWORD)
        search_url = "https://it.pracuj.pl/praca/python%20engineer;kw/ostatnich%2024h;p,1/polska;ct,1"
        driver.get(search_url)

        while True:
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-test='default-offer']"))
            )

            soup = BeautifulSoup(driver.page_source, "html.parser")
            offers_section = soup.find("div", attrs={"data-test": "section-offers"})
            job_offers = offers_section.find_all("div", attrs={"data-test": "default-offer"}) if offers_section else []

            for offer in job_offers:
                parsed = parse_offer(offer)
                if parsed:
                    results.append(parsed)

            try:
                next_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-test='bottom-pagination-button-next']"))
                )
                driver.execute_script("arguments[0].click();", next_button)
                WebDriverWait(driver, 10).until(EC.staleness_of(next_button))
            except Exception:
                break

    finally:
        driver.quit()

    return results


def save_results(results, output_path="../output/output.json"):
    """Save results to a JSON file."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    try:
        results = scrape_jobs()
        save_results(results)
    except Exception as e:
        print(f"An error occurred: {e}")