from selenium import webdriver

browser = webdriver.Firefox()
browser.get('http://peter14f.pythonanywhere.com')

assert 'Django' in browser.title
