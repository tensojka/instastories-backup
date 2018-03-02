#!/usr/bin/python3
import bs4
import json
import os
import requests
import re
import sqlite3

def get_prefs():
    try:
        with open('prefs.json') as json_data:
            prefs = json.load(json_data)
            return prefs
    except FileNotFoundError:
        print("prefs.json file not found in current directory. Exiting.")
        exit()

def create_db(prefs):
    conn = sqlite3.connect(prefs["dbfilename"])
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS `entries` (`id`	TEXT UNIQUE, `url`	TEXT, `userid`	TEXT, `username` TEXT, `taken_at` INTEGER, `filename` TEXT);")
    if not prefs["quiet"]: print("Loading new entries to DB")
    return conn

def fetch_user_id(username):
    r = requests.get("https://smashballoon.com/instagram-feed/find-instagram-user-id/?username=" + username + "&896914zje22267qjtl=4")
    soup = bs4.BeautifulSoup(r.text, "lxml")
    div = str(soup.find("div", id="show_id"))
    user_id = re.search('(?:User\ ID:<\/b>\s)(\d+)', div).groups()[0]
    return user_id

def fetch_stories(prefs, session, conn):
    for username in prefs["usernames"]:
        print(username)
        userid = fetch_user_id(username)
        response = session.get("https://i.instagram.com/api/v1/feed/user/"+ userid +"/reel_media/", headers={
            'user-agent':"Instagram 10.3.2 (iPhone7,2; iPhone OS 9_3_3; en_US; en-US; scale=2.00; 750x1334) AppleWebKit/420+",
            'cookie':'sessionid={0};'.format(session.cookies['sessionid'])
        })
        if response.status_code != 200:
            print("ERROR: got "+str(response.status_code)+" when fetching stories entries!")
            exit()
        response = json.loads(response.text)
        for item in response['items']:
            id = item['id']
            try:
                url = item['video_versions'][0]['url']
                print(url)
            except KeyError: #if there are no videos of this item
                url = item['image_versions2']['candidates'][0]['url']
            taken_at = item['taken_at']
            try:
                c = conn.cursor()
                c.execute('INSERT INTO entries VALUES(?,?,?,?,?,?)', (str(id),str(url),str(userid),str(username),taken_at,""))
            except sqlite3.IntegrityError: #is thrown when UNIQUE doesn't match
                if not prefs["quiet"]: print('!', end='',flush=True)
            else:
                if not prefs["quiet"]: print('.', end='',flush=True)

        conn.commit()

def download_stories(prefs, session, conn):
    if not prefs["quiet"]:
        print()
        print("Downloading new videos and photos, printing names of new files:")

    c = conn.cursor()
    todelete, toupdate = [], []
    if not os.path.exists(prefs["filesdir"]):
        os.makedirs(prefs["filesdir"])

    for row in c.execute('SELECT * FROM entries WHERE filename = ""'):
        r = session.get(row[1])
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

def get_login_session(prefs):
    session = requests.Session()
    session.headers.update({'Referer': 'https://www.instagram.com/'})
    req = session.get('https://www.instagram.com/')
    session.headers.update({'X-CSRFToken': req.cookies['csrftoken']})
    login_data = {'username': prefs['username'], 'password': prefs['password']}
    session.post('https://www.instagram.com/accounts/login/ajax/', data=login_data, allow_redirects=True)
    return session

def main():
    prefs = get_prefs()
    session = get_login_session(prefs)
    conn = create_db(prefs)
    fetch_stories(prefs, session, conn)
    download_stories(prefs, session, conn)

if __name__ == '__main__':
    main()
