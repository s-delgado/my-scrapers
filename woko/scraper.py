from selenium import webdriver
import pandas as pd
from webdriver_manager.chrome import ChromeDriverManager
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import os
from selenium.webdriver.chrome.options import Options

options = Options()
options.headless = True
driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)

driver.get("http://www.woko.ch/en/nachmieter-gesucht")

# create a list with elements
datePosted = []
heading = []
availableDate = []
address = []
links = []
price = []

content = driver.find_element_by_id("GruppeID_98")

for i in content.find_elements_by_class_name('inserat'):
    titel = i.find_element_by_class_name('titel')
    datePosted.append(titel.find_element_by_css_selector('span').get_attribute("innerHTML"))
    heading.append(titel.find_element_by_css_selector('h3').get_attribute("innerHTML"))

    table = i.find_element_by_css_selector('table').get_attribute("innerHTML").splitlines()
    availableDate.append(table[5].split(">")[1].split('<')[0].strip().split(' ')[2])
    address.append(table[9].split('>')[1].split('<')[0])

    price.append(i.find_element_by_class_name('preis').get_attribute('innerHTML'))
    links.append(i.find_element_by_css_selector('a').get_attribute('href'))

df = pd.DataFrame([datePosted, heading, availableDate, address, links, price]).T
df.columns = ['datePosted', 'title', 'moveIn', 'address', 'link', 'price']
df['datePosted'] = pd.to_datetime(df.datePosted,  format="%d.%m.%Y %H:%M")
df['moveIn'] = pd.to_datetime(df.moveIn, format="%d.%m.%Y")
df = df.sort_values('moveIn', ascending=False)

target = df[(df.moveIn >= "2021-09-01")]

if len(target) > 0:
    message = Mail(
        from_email='properties@woko.com',
        to_emails=os.environ['EMAIL'],
        subject='WOKO Properties!',
        html_content=target.to_html())
    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception:
        print('Email not sent')
