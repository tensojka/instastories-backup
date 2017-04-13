#!/usr/bin/python3
import requests
import sqlite3

conn = sqlite3.connect('stories.sqlite3')
c = conn.cursor()
todelete = []
toupdate = []


for row in c.execute('SELECT * FROM entries'):
    r = requests.get(row[1])
    if r.status_code == 404:
        todelete.append(row[0])
    elif r.status_code%200 < 100:
        if r.headers["Content-Type"] == "video/mp4":
            filename = str(row[3])+":"+str(row[4])+".mp4"
        elif r.headers["Content-Type"] == "image/jpeg":
            filename = str(row[3])+":"+str(row[4])+".jpg"
        else:
            filename = str(row[3])+":"+str(row[4])+".unknown"
            print("WARNING: couldn't identify MIME type for URL "+row[1])
        with open("files/"+filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk: # filter out keep-alive new chunks
                    f.write(chunk)
        toupdate.append((filename,row[0]))

for item in todelete:
    c.execute('DELETE FROM entries WHERE id = ?',(item,))
for item in toupdate:
    c.execute('UPDATE entries SET filename = ? WHERE id = ?',item)
conn.commit()