import re
import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

def requires_experience(description, max_years=2):
    match = re.search(r'(\d+)\s*(?:\+|plus|years?)\s*experience', description, re.IGNORECASE)
    if match:
        years = int(match.group(1))
        return years <= max_years
    return True

def truncate_description(description, length=300):
    if len(description) > length:
        return description[:length] + "..."
    return description

def get_driver(headless=True):
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')
    options.add_argument('--ignore-certificate-errors-spki-list')
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
    
    if headless:
        options.add_argument('--headless')  # Enable headless mode
        options.add_argument('--disable-gpu')  # Disable GPU usage
        options.add_argument('--window-size=1920,1080')  # Set window size for headless mode
    
    return webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

def get_indeed_jobs():
    driver = get_driver(headless=True)
    driver.get("https://ca.indeed.com/?r=us")

    search_bar = driver.find_element(By.ID, 'text-input-what')
    search_bar.send_keys("entry level software developer")
    search_bar.submit()
    time.sleep(random.uniform(10, 20))

    page_source = driver.page_source
    soup = BeautifulSoup(page_source, "html5lib")
    job_listings = soup.find_all('a', attrs={"class": "jcs-JobTitle"})

    print(f"Found {len(job_listings)} job listings on Indeed")

    with open('job_listings_indeed.txt', 'w', encoding='utf-8') as file:
        for job in job_listings:
            job_title = job.text.strip()
            job_link = 'https://ca.indeed.com' + job.get('href')

            driver.get(job_link)
            time.sleep(random.uniform(5, 15))

            job_page_source = driver.page_source
            job_soup = BeautifulSoup(job_page_source, "html5lib")
            job_description_div = job_soup.find('div', attrs={"id": "jobDescriptionText"})
            job_description = job_description_div.get_text(strip=True) if job_description_div else 'No description found'

            if not requires_experience(job_description):
                continue

            job_description = truncate_description(job_description, length=300)

            file.write("Job Title:\n")
            file.write(f"{job_title}\n\n")
            file.write("Job Link:\n")
            file.write(f"{job_link}\n\n")
            file.write("Job Description:\n")
            file.write(f"{job_description}\n")
            file.write("=" * 80 + "\n\n")

    driver.quit()

def get_monster_jobs():
    driver = get_driver(headless=False)  # Set to False to handle CAPTCHA manually
    driver.get("https://www.monster.ca/")

    # Pause for CAPTCHA
    input("Please solve the CAPTCHA manually and press Enter to continue...")

    search_bar = driver.find_element(By.ID, 'horizontal-input-one-undefined')
    search_bar.send_keys("entry level software developer")
    search_bar.submit()
    time.sleep(random.uniform(10, 20))

    page_source = driver.page_source
    soup = BeautifulSoup(page_source, "html5lib")
    job_listings = soup.find_all('a', attrs={"class": "sc-gAjuZT cUPTNR"})

    print(f"Found {len(job_listings)} job listings on Monster")

    with open('job_listings_monster.txt', 'w', encoding='utf-8') as file:
        for job in job_listings:
            job_title = job.text.strip()
            job_link = 'https://www.monster.ca/' + job.get('href')

            driver.get(job_link)
            time.sleep(random.uniform(5, 15))

            job_page_source = driver.page_source
            job_soup = BeautifulSoup(job_page_source, "html5lib")
            job_description_div = job_soup.find('div', attrs={"class": "codestyles__CodeContainer-sc-u7r2mx-0 dCWfYX code-component"})
            job_description = job_description_div.get_text(strip=True) if job_description_div else 'No description found'

            if not requires_experience(job_description):
                continue

            job_description = truncate_description(job_description, length=300)

            file.write("Job Title:\n")
            file.write(f"{job_title}\n\n")
            file.write("Job Link:\n")
            file.write(f"{job_link}\n\n")
            file.write("Job Description:\n")
            file.write(f"{job_description}\n")
            file.write("=" * 80 + "\n\n")

    driver.quit()

# Get job listings from Indeed and Monster
get_indeed_jobs()
get_monster_jobs()

print("Job listings saved to job_listings_indeed.txt and job_listings_monster.txt")
