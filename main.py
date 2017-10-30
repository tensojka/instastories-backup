#!/usr/bin/python3
import requests
import sqlite3
import json
import os

try:
    with open('prefs.json') as json_data:
        prefs = json.load(json_data)
except FileNotFoundError:
    print("prefs.json file not found in current directory. Exiting.")
    exit()

conn = sqlite3.connect(prefs["dbfilename"])
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS `entries` (`id`	TEXT UNIQUE, `url`	TEXT, `userid`	TEXT, `username` TEXT, `taken_at` INTEGER, `filename` TEXT);")
if not prefs["quiet"]: print("Loading new entries to DB")

while len(prefs["ids"]) > 0:
    pair = prefs["ids"].popitem()
    response = requests.request("GET", "https://i.instagram.com/api/v1/feed/user/"+pair[0]+"/reel_media/", headers=prefs["headers"])
    if response.status_code != 200:
        print("ERROR: got "+str(response.status_code)+" when fetching stories entries!")
        exit
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
            if not prefs["quiet"]: print('!', end='',flush=True)
        else:
            if not prefs["quiet"]: print('.', end='',flush=True)

conn.commit()

if not prefs["quiet"]:
    print()
    print("Downloading new videos and photos, printing names of new files:")

todelete = []
toupdate = []
if not os.path.exists(prefs["filesdir"]):
    os.makedirs(prefs["filesdir"])

for row in c.execute('SELECT * FROM entries WHERE filename = ""'):
    r = requests.get(row[1])
    if r.status_code == 404:
        todelete.append(row[0])
    elif r.status_code%200 < 100:
        if r.headers["Content-Type"] == "video/mp4" or r.headers["Content-Type"] == "text/plain":
            filename = str(row[3])+"/"+str(row[4])+".mp4"
        elif r.headers["Content-Type"] == "image/jpeg":
            filename = str(row[3])+"/"+str(row[4])+".jpg"
        else:
            filename = str(row[3])+"/"+str(row[4])+".unknown"
            print("WARNING: couldn't identify MIME type for URL "+row[1])
        if not os.path.exists(prefs["filesdir"]+"/"+str(row[3])):
            os.makedirs(prefs["filesdir"]+"/"+str(row[3]))
        with open(prefs["filesdir"]+"/"+filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk: # filter out keep-alive new chunks
                    f.write(chunk)
        toupdate.append((filename,row[0]))
        if not prefs["quiet"]: print(filename)

for item in todelete:
    c.execute('DELETE FROM entries WHERE id = ?',(item,))
for item in toupdate:
    c.execute('UPDATE entries SET filename = ? WHERE id = ?',item)
conn.commit()