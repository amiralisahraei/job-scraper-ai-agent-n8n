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
# Set up Chrome WebDriver

options = Options()
options.add_argument("--headless")  # Add this line to disable GUI
options.add_argument("--start-maximized")

def scrape_jobs():
    driver = webdriver.Chrome(service=ChromeService(), options=options)
    try:
        # Step 1: Go to login page
        driver.get("https://login.pracuj.pl/")

        # Step 2: Accept cookies (if popup appears)
        try:
            cookie_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Akceptuj wszystkie')]"))
            )
            cookie_button.click()
        except:
            pass  # No cookie popup

        # Step 3: Enter email
        email_input = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email']"))
        )
        email_input.send_keys(EMAIL)
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        # Step 4: Enter password
        password_input = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='password']"))
        )
        password_input.send_keys(PASSWORD)
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        # Step 5: Skip welcome screen if it appears
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//h1[contains(text(), 'Nowe konto już jest')]"))
            )
        except:
            pass

        # Step 6: Go to job search page
        search_url = "https://it.pracuj.pl/praca/python%20engineer;kw/ostatnich%2024h;p,1/polska;ct,1?itth=37%2C213"
        driver.get(search_url)

        # Step 7: Wait for job offers to load
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-test='default-offer']"))
        )

        # Step 8: Parse page with BeautifulSoup
        soup = BeautifulSoup(driver.page_source, "html.parser")
        offers_section = soup.find("div", attrs={"data-test": "section-offers"})
        job_offers = offers_section.find_all("div", attrs={"data-test": "default-offer"})

        # Step 9: Extract only non-starred offers
        results = []

        for offer in job_offers:
            star_button = offer.find("button", attrs={"data-test": "add-to-favourites"})
            if star_button:
                is_saved = star_button.get("data-test-checkboxstate") == "true"
                if is_saved:
                    continue  # Skip starred offers

            title_tag = offer.find("h2", attrs={"data-test": "offer-title"})
            title = title_tag.get_text(strip=True) if title_tag else None

            company_tag = offer.find("h3", attrs={"data-test": "text-company-name"})
            company = company_tag.get_text(strip=True) if company_tag else None

            location_tag = offer.find("h4", attrs={"data-test": "text-region"})
            location = location_tag.get_text(strip=True) if location_tag else None

            link_tag = offer.find("a", attrs={"data-test": "link-offer"})
            link = link_tag["href"] if link_tag and "href" in link_tag.attrs else None

            tech_tags = offer.find_all("span", attrs={"data-test": "technologies-item"})
            technologies = [tech.get_text(strip=True) for tech in tech_tags]

            results.append({
                "title": title,
                "company": company,
                "location": location,
                "link": link,
                "technologies": technologies,
            })

    finally:
        driver.quit()
    
    return results

if __name__ == "__main__":
    result = scrape_jobs()
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=4)

   