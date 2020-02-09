from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

import difflib
from difflib import SequenceMatcher

import time
import sys
from os import listdir
import os
from os.path import isfile, join
import glob

import csv

# CONSTANTS
TRACKS_DB_SOURCE = 'https://myfreemp3cc.com/'
SEARCH_INPUT_XPATH = '//*[@id="query"]'
SEARCH_BTN_XPATH = '/html/body/div[2]/div[1]/div/span/button'
SEARCH_RESULT_CLASS = 'list-group-item'
DOWNLOAD_PATH = '/Users/felixsimard/OneDrive - McGill University/Personal/Music/Library/Downloaded/' #/Users/felixsimard/Downloads/
CSV_PATH = "/Users/felixsimard/OneDrive - McGill University/Personal/Music/Library/spotifyCSVs/"

SUCCESS_DOWNLOADS = []
FAILED_DOWNLOADS = []

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
        #print(u'\u2717', query)
        #FAILED_DOWNLOADS.append(query)
        #exit(1)
        pass

    output = driver.find_elements_by_class_name(SEARCH_RESULT_CLASS)
    try:
        driver.find_element(By.XPATH, '//*[@id="result"]/div[2]/li[1]/div/a[3]').click() # small download button
    except Exception as e:
        print(u'\u2717', query)
        FAILED_DOWNLOADS.append(query)
        pass

    main_download_btn = '//*[@id="footer"]/div[1]/div[1]/button'

    WebDriverWait(driver, 5)

    try:
        element = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, main_download_btn))
        )
    except Exception as e:
        pass

    try:
        driver.switch_to.window(driver.window_handles[1])
        driver.find_element(By.XPATH, '//*[@id="footer"]/div[1]/div[1]/button').click() # main download button
        # song downloaded :)
        print(u'\u2713', query)
        SUCCESS_DOWNLOADS.append(query)
    except Exception as e:
        pass




# record list of all current songs in directory
library = []
def updateLibrary():
    for f in listdir(DOWNLOAD_PATH):
        unwanted_str = " my-free-mp3s.com "
        if (f.endswith('.mp3') or f.endswith('.wav')):
            f = f.replace(unwanted_str, '')
            f = f.replace('.mp3', '')
            f = f.strip()
            library.append(f)


def checkIfDownloaded(artist, track):
    isDownloaded = False
    print("Artist:", artist, "Track:", track)
    query = artist+" - "+track
    for l in library:
        similar = SequenceMatcher(None, query, l).ratio()
        if(similar > 0.70):
            isDownloaded = True
            print("ALREADY", l)
            break

    return isDownloaded


#--- MAIN ---#

print("Starting music crawler...", "\n")

print("Location:", DOWNLOAD_PATH, "\n")

# get arguments from command line ie: name of playlist
args = sys.argv
if(len(args) > 1):
    args_lst = args[1:]
    playlist_name = ' '.join(args_lst)

# get CSVs in playlists directory
playlists_csv = [ f for f in listdir(CSV_PATH) if isfile(join(CSV_PATH, f)) ]

print("Reading:", playlist_name, "\n")

# construct arrays of tracks and artists
tracks = []
artists = []
with open(CSV_PATH+playlist_name) as csvfile:
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

    hasBeenDownloaded = difflib.get_close_matches(query, library, 1, 0.5)

    #hasBeenDownloaded = checkIfDownloaded(artists[t], tracks[t])

    if (len(hasBeenDownloaded) <= 0): # len(hasBeenDownloaded) <= 0
        # Initiate Chrome driver
        chrome_options = webdriver.ChromeOptions()
        prefs = {"download.default_directory" : DOWNLOAD_PATH}
        chrome_options.add_experimental_option("prefs",prefs)
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
        new_file_name = new_file_name.strip()
        os.rename(DOWNLOAD_PATH+f, DOWNLOAD_PATH+new_file_name)

print("\n")
print("Success:", len(SUCCESS_DOWNLOADS), "Failed:", len(FAILED_DOWNLOADS))
print("\n")
