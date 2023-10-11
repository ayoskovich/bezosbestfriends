import requests

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

chromedriver_path = "/Users/anthonyyoskovich/Downloads/chromedriver-mac-x64/chromedriver"

options = Options()
options.add_argument("--window-size=1920x1080")
options.add_argument("--verbose")
options.add_argument("--headless")

service = Service(executable_path=chromedriver_path)
driver = webdriver.Chrome(service=service, options=options)
driver.get("https://ir.aboutamazon.com/annual-reports-proxies-and-shareholder-letters/default.aspx")
elems = driver.find_elements(By.CLASS_NAME, "module-financial_year-text")

alldata = {}
for i, elem in enumerate(elems):
    year = elem.text
    elem.click()
    wait = WebDriverWait(driver, 10)
    box = wait.until(EC.visibility_of_element_located((By.XPATH, f'//*[@id="_ctrl0_ctl54_divModuleContainer"]/div/div/div/div/div[{i+1}]')))

    list_items = box.find_elements(By.TAG_NAME, 'li')
    assert len(list_items) >= 3, 'Didnt find correct number of elements'

    for item in list_items:
        linktext = item.find_element(By.TAG_NAME, 'a').get_attribute('href')
        if 'letter' in linktext.lower():
            pass
        elif 'ltr' in linktext.lower():
            pass
        else:
            continue
        alldata[year] = linktext

for year, url in alldata.items():
    response = requests.get(url)
    print(f'Writing {year}')
    with open(f'data/Letter_{year}.pdf', 'wb') as f:
        f.write(response.content)