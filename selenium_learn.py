from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

def baidu():
    browser = webdriver.Chrome()
    browser.get('https://www.baidu.com')
    input = browser.find_element_by_id('kw')
    input.send_keys('Python')
    input.send_keys(Keys.ENTER)
    wait = WebDriverWait(browser, 10)
    wait.until(EC.presence_of_element_located((By.ID, 'content_left')))
    print(browser.current_url)
    print(browser.get_cookies())
    print(browser.page_source)
    browser.close()

def taobao():
    browser = webdriver.Chrome()
    browser.get('https://www.taobao.com')
    input_first = browser.find_element_by_id('q')
    input_second = browser.find_element_by_css_selector('#q')
    input_third = browser.find_element_by_xpath('//*[@id="q"]')
    print(input_first, input_second, input_third)
    browser.close()

if __name__ == '__main__':
    taobao()