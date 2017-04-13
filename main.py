#!/usr/bin/python3
import requests
import sqlite3
import json

conn = sqlite3.connect('stories.sqlite3')
c = conn.cursor()

with open('prefs.json') as json_data:
    prefs = json.load(json_data)
ids = prefs["ids"]
headers = prefs["headers"]

while len(ids) > 0:
    pair = ids.popitem()
    response = requests.request("GET", "https://i.instagram.com/api/v1/feed/user/"+pair[0]+"/reel_media/", headers=headers)
    response = json.loads(response.text)
    for item in response['items']:
        id = item['id']
        try:
            url = item['video_versions'][0]['url']
        except KeyError: #if there are no videos of this item
            url = item['image_versions2']['candidates'][0]['url']
        userid = pair[0]
        username = pair[1]
        taken_at = item['taken_at']
        try:
            c.execute('INSERT INTO entries VALUES(?,?,?,?,?,?)', (str(id),str(url),str(userid),str(username),taken_at,""))
        except sqlite3.IntegrityError: #is thrown when UNIQUE doesn't match
            print('!', end='',flush=True)
        else:
            print('.', end='',flush=True)
    
conn.commit()
    #CREATE TABLE `entries` (
    #    `id`	TEXT UNIQUE,
    #    `url`	TEXT,
    #    `userid`	TEXT,
    #    `username`	TEXT
    #);
