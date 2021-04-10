import time
from selenium import webdriver
import os
from datetime import datetime
'''
data = []

def checkforinput():
    if driver.getPageSource().contains("Please verify you are a human"):
        print("logic")

def readpage(name, url, return_page=None):
    fullname = name

    driver.get(url)
    time.sleep(10)
    checkforinput()
    elements = driver.find_elements_by_xpath("//div[@id='navigation']/ul/li/a")
    regions = [(rg.text, rg.get_attribute('href')) for rg in elements]
    if len(elements) == 0:
        data.append(name)
        print(name)
        #driver.get(return_page)
    else:
        for name,url in regions:
            fullname += f'{name}"||"'
            time.sleep(10) # Let the user actually see something!
            from_page = driver.current_url
            readpage(name=fullname, url=url, return_page=from_page)
'''

def executesearch():
    elements = driver.find_elements_by_xpath("//a[@data-modal='vaccineinfo-DE']")
    if len(elements) > 0:
        elements[0].click()
        time.sleep(5)
        covidstatus_div = driver.find_elements_by_xpath("//div[contains(@class,'covid-status')]/table/tbody/tr")
        active_modal = driver.find_elements_by_xpath("//div[@class='modal__box modal--active']")
        timestamp = active_modal[0].find_elements_by_xpath(".//div[@data-id='timestamp']/p")[0].text
        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        print(f'{"*"*15} {dt_string} {"*"*15}')
        print(timestamp)
        for row in covidstatus_div:
            status = [f.text for f in row.find_elements_by_xpath(".//span")]
            status = " ".join(status)
            print(status)
            #if 'Available' in status:
            if 'Available' in status:
               os.system(f'say "{status}"')
        print("*"*15)
        time.sleep(5)
        driver.find_elements_by_xpath("//div[@class='modal__box modal--active']/div/button")[0].click()


driver = webdriver.Chrome('/Users/cjrisua/Downloads/chromedriver2')  # Optional argument, if not specified will search path.
driver.get('https://www.cvs.com/immunizations/covid-19-vaccine')
time.sleep(5) # Let the user actually see something!

flag = True
maxiter = 250
while(flag):
    executesearch()
    time.sleep(60)
    maxiter = maxiter -1
    if maxiter == 0:
        break
time.sleep(5) # Let the user actually see something!
driver.quit()
