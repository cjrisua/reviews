import time
from selenium import webdriver

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

driver = webdriver.Chrome()  # Optional argument, if not specified will search path.
driver.get('https://www.wine-searcher.com/regions-california');
time.sleep(5) # Let the user actually see something!
#search_box = driver.find_element_by_name('q')
elements = driver.find_elements_by_xpath("//div[@id='navigation']/ul/li/a")
regions = [(rg.text, rg.get_attribute('href')) for rg in elements]
for name,url in regions:
    readpage(url=url,name=f'{name}"||"')
    
#search_box.send_keys('ChromeDriver')
#search_box.submit()
time.sleep(5) # Let the user actually see something!
driver.quit()