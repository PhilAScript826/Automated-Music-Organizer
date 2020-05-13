from bs4 import BeautifulSoup as bs
import requests
import json
import lyricsgenius
import re
import os
import shutil
import datetime
import time

# Instantiate genius api with your token
token = input("Please provide Genius API Token:")
try:
    genius = lyricsgenius.Genius(token)
except:
    print("Not a valid token. Please try again.")

directory = input("Provide directory:")
# Iterate through the files in your directory
try:
    for file in os.listdir(directory)[1:]:
        
        name = False
        if '-' not in file:
            song = file
        else:
            # Split the file by name and song
            name, song = file.split('-',1)

        # Remove unwanted characters from name
        song = re.sub('(\(.*?\).mp3|\[.*?\].mp3|.mp3)', '', song)

        # Search for the artist in Genius API
        if name:
            artist = genius.search_song(song, name)
        else:
            artist = genius.search_song(song)
        
        #Instantiate the datetime so you can update later
        year, month, day = artist.year.split('-')
        date = datetime.datetime(year=int(year), month=int(month), day=int(day), hour=0, minute=0, second=0)
        modTime = time.mktime(date.timetuple())
        
        # enter the Genius site to scrape the genre of the artist 
        response = requests.get(str(artist.url))
        soup = bs(response.text, 'html.parser')
        data = re.findall("var CURRENT_TAG =(.+?);\n", soup.find_all('script')[2].text, re.S)
        ls = []
        if data:
            ls = json.loads(data[0])
            if ls['tag']['slug'] == 'r-b':
                ls['tag']['slug'] = 'r&b'

        # Create a directory of it doesnt exist by genre and move the file into the created directory. Otherwise, move file into existing directory
        if os.path.exists(os.path.join(directory, ls['tag']['slug'].upper())):
            source = os.path.join(directory, file)
            destination = os.path.join(directory, ls['tag']['slug'].upper())
            dest = shutil.move(source, destination)

            # This updates the created and modified time of file
            os.utime(dest, (modTime, modTime))

        else:
            os.mkdir(os.path.join(directory, ls['tag']['slug'].upper()))
            source = os.path.join(directory, file)
            destination = os.path.join(directory, ls['tag']['slug'].upper())
            dest = shutil.move(source, destination)
            
            # This updates the created and modified time of file
            os.utime(dest, (modTime, modTime))
except:
    print("Not a valid directory. Please try again.")

print("Finished!")