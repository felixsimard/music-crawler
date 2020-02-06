from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

import difflib

import time
from os import listdir
import os
from os.path import isfile, join
import glob

import csv

# some constants
TRACKS_DB_SOURCE = 'https://myfreemp3cc.com/'
SEARCH_INPUT_XPATH = '//*[@id="query"]'
SEARCH_BTN_XPATH = '/html/body/div[2]/div[1]/div/span/button'
SEARCH_RESULT_CLASS = 'list-group-item'
DOWNLOAD_PATH = '/Users/felixsimard/Downloads/'

def searchTrack(query):
    search = driver.find_element(By.XPATH, SEARCH_INPUT_XPATH)
    search_btn = driver.find_element(By.XPATH, SEARCH_BTN_XPATH)
    search.send_keys(query)
    search_btn.click()
    try:
        element = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, SEARCH_RESULT_CLASS))
        )
    except Exception as e:
        #print("Error retrieving search results.")
        print(u'\2717', query)
        exit(1)

    output = driver.find_elements_by_class_name(SEARCH_RESULT_CLASS)
    try:
        driver.find_element(By.XPATH, '//*[@id="result"]/div[2]/li[1]/div/a[3]').click() # small download button
    except Exception as e:
        #print("Error:", e)
        print(u'\2717', query)
        exit(1)

    main_download_btn = '//*[@id="footer"]/div[1]/div[1]/button'

    WebDriverWait(driver, 5)

    driver.switch_to.window(driver.window_handles[1])

    try:
        element = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, main_download_btn))
        )
    except Exception as e:
        print(u'\2717', query)
        #print("Error finding the main download button.")
        exit(1)

    try:
        driver.find_element(By.XPATH, '//*[@id="footer"]/div[1]/div[1]/button').click() # main download button

    except Exception as e:
        #print("Error:", e)
        exit(1)

    # song downloaded :)
    print(u'\u2713', query)


# record list of all current songs in directory
library = []
def updateLibrary():
    for f in listdir(DOWNLOAD_PATH):
        unwanted_str = " my-free-mp3s.com "
        if (f.endswith('.mp3') or f.endswith('.wav')):
            f = f.replace(unwanted_str, '')
            f = f.replace('.mp3', '')
            library.append(f)



#--- MAIN ---#

# get CSVs in playlists directory
csv_path = "playlists/"
playlists_csv = [ f for f in listdir(csv_path) if isfile(join(csv_path, f)) ]

playlist = playlists_csv[0]

# construct arrays of tracks and artists
tracks = []
artists = []
with open(csv_path+playlist) as csvfile:
    readCSV = csv.reader(csvfile, delimiter=',')
    for row in readCSV:
        tracks.append(row[0])
        artists.append(row[1])
tracks.pop(0) # remove the "track"
artists.pop(0) # remove the "artist"


updateLibrary()

for t in range(len(tracks)):

    # track search query
    query = artists[t]+" - "+tracks[t]

    # check if song has not been already downloaded
    #print("Checking if", query, "is in", library, "\n")
    hasBeenDownloaded = difflib.get_close_matches(query, library, 1, 0.75)
    if(len(hasBeenDownloaded) <= 0):
        # Initiate Chrome driver
        chrome_options = Options()
        #chrome_options.add_argument("--headless")
        driver = webdriver.Chrome(executable_path=r"/Users/felixsimard/Sites/trackcrawler/chromedriver", options=chrome_options)
        driver.get(TRACKS_DB_SOURCE)

        searchTrack(query)
        driver.close()

        updateLibrary()
    else:
        print(u'\u2713', query)

# Clean file names
for f in listdir(DOWNLOAD_PATH):
    unwanted_str = " my-free-mp3s.com "
    if (f.endswith('.mp3') or f.endswith('.wav')) and unwanted_str in f:
        new_file_name = f.replace(unwanted_str, '')
        os.rename(DOWNLOAD_PATH+f, DOWNLOAD_PATH+new_file_name)
