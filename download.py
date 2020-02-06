import urllib.request
from selenium import webdriver

url = 'https://d.mp3-send.com/RvWBZB:WrV3rB'

DOWNLOAD_PATH = '/Users/felixsimard/Downloads'

driver = webdriver.Chrome(executable_path=r"/Users/felixsimard/Sites/trackcrawler/chromedriver")
driver.get(url)
