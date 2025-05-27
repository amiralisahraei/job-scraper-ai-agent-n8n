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
import time

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


def expand_all_multiple_locations(driver):
    """Expand all multiple location containers."""
    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-test='default-offer']"))
        )
        containers = driver.find_elements(By.CSS_SELECTOR, "div[data-test-location='multiple']")
        expanded = 0
        for container in containers:
            try:
                clickable_elements = container.find_elements(By.CSS_SELECTOR, 
                    "button, a, *[role='button'], *[onclick], *[cursor='pointer']")
                target_element = None
                for elem in clickable_elements:
                    elem_text = elem.text.strip().lower()
                    elem_class = elem.get_attribute('class') or ''
                    if any(keyword in elem_text for keyword in ['lokalizacj', 'więcej', 'rozwiń', 'pokaż']):
                        target_element = elem
                        break
                    elif any(keyword in elem_class for keyword in ['expand', 'toggle', 'show-more']):
                        target_element = elem
                        break
                if not target_element:
                    target_element = clickable_elements[0] if clickable_elements else container
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", target_element)
                time.sleep(0.5)
                driver.execute_script("arguments[0].click();", target_element)
                time.sleep(1)
                expanded += 1
            except Exception:
                continue
        if expanded > 0:
            time.sleep(2)
        return expanded
    except Exception:
        return 0

def parse_offer(offer):
    """Extract job offer details from HTML."""
    try:
        if (offer.find("button", attrs={"data-test": "add-to-favourites", "data-test-checkboxstate": "true"}) or
            offer.find("div", attrs={"data-test": "applied-text"})):
            return None

        details = {
            "title": _get_text(offer, "h2", "offer-title"),
            "company": _get_text(offer, "h3", "text-company-name"),
            "technologies": [
                tag.get_text(strip=True) 
                for tag in offer.find_all("span", attrs={"data-test": "technologies-item"})
            ]
        }

        location_links = offer.find_all("a", attrs={"data-test": "link-offer"})
        if len(location_links) > 1:
            if offer.find("button", attrs={"data-test-checkboxstate": "true"}):
                return None
            results = []
            links_array = []
            for link in location_links:
                text_location = link.get_text(strip=True)
                links_array.append({
                    text_location: link["href"]
                })
            details.update({
                "links": links_array
            })
            results.append(details)
            return results if results else None

        location_text = _get_text(offer, "h4", "text-region")
        link_href = _get_href(offer, "a", "link-offer")
        details.update({
            "location": location_text,
            "link": link_href
        })
        return details

    except Exception:
        return None


def _get_text(element, tag, data_test):
    """Helper function to get text from element safely."""
    found = element.find(tag, attrs={"data-test": data_test})
    return found.get_text(strip=True) if found else None


def _get_href(element, tag, data_test):
    """Helper function to get href from element safely."""
    found = element.find(tag, attrs={"data-test": data_test})
    return found["href"] if found and "href" in found.attrs else None


def scrape_jobs():
    """Main scraping logic with expand-all-first approach."""
    driver = webdriver.Chrome(service=ChromeService(), options=options)
    results = []

    try:
        login(driver, EMAIL, PASSWORD)
        search_url = "https://it.pracuj.pl/praca/python%20engineer;kw/ostatnich%2024h;p,1/polska;ct,1"
        driver.get(search_url)

        page_count = 0
        while True:
            page_count += 1

            expanded_count = expand_all_multiple_locations(driver)

            soup = BeautifulSoup(driver.page_source, "html.parser")
            offers_section = soup.find("div", attrs={"data-test": "section-offers"})
            job_offers = offers_section.find_all("div", attrs={"data-test": "default-offer"}) if offers_section else []

            for offer in job_offers:
                parsed = parse_offer(offer)
                if parsed:
                    if isinstance(parsed, list):
                        results.extend(parsed)
                    else:
                        results.append(parsed)

            try:
                next_button = driver.find_element(By.CSS_SELECTOR, "button[data-test='bottom-pagination-button-next']")
                if not next_button.is_enabled():
                    break
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_button)
                time.sleep(1)
                driver.execute_script("arguments[0].click();", next_button)
                WebDriverWait(driver, 10).until(EC.staleness_of(next_button))
                time.sleep(2)
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
    print(f"Saved {len(results)} results to {output_path}")


if __name__ == "__main__":
    try:
        results = scrape_jobs()
        save_results(results)
        print(f"\nScraping completed! Found {len(results)} total job offers.")
    except Exception as e:
        print(f"An error occurred: {e}")
