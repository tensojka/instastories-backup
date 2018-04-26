#!/usr/bin/python3
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

def get_db(prefs):
    conn = sqlite3.connect(prefs["dbfilename"])
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS `entries` (`id`	TEXT UNIQUE, `url`	TEXT, `userid`	TEXT, `username` TEXT, `taken_at` INTEGER, `filename` TEXT);")
    if not prefs["quiet"]: print("Loading new entries to DB")
    return conn

def fetch_user_id(username):
    r = requests.get("https://www.instagram.com/" + username)
    return (json.loads(re.findall(
        r'(?<=window._sharedData = ).+(?=;</script>)',
        r.text)[0])['entry_data']['ProfilePage'][0]['graphql']['user']['id'])

def fetch_stories(prefs, session, conn):
    for userid,username in prefs["ids"].items():
        response = session.get("https://i.instagram.com/api/v1/feed/user/"+ userid +"/reel_media/")
        responseobj = json.loads(response.text)
        if response.status_code != 200:
            if responseobj['message'] == "Invalid target user.":
                print("User "+username+" with id "+userid+" does not exist. Skipping.")
                continue
            raise SystemExit("ERROR: got "+str(response.status_code)+" when fetching stories entries! Response: "+response.text)
        for item in responseobj['items']:
            id = item['id']
            try:
                url = item['video_versions'][0]['url']
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
    session.headers['user-agent'] = "Instagram 10.3.2 (iPhone7,2; iPhone OS 9_3_3; en_US; en-US; scale=2.00; 750x1334) AppleWebKit/420+"
    if ('username' in prefs) and ('password' in prefs):
        session.headers.update({'Referer': 'https://www.instagram.com/'})
        req = session.get('https://www.instagram.com/')
        session.headers.update({'X-CSRFToken': req.cookies['csrftoken']})
        login_data = {'username': prefs['username'], 'password': prefs['password']}
        session.post('https://www.instagram.com/accounts/login/ajax/', data=login_data, allow_redirects=True)
    elif 'headers' in prefs:
        session.headers = prefs["headers"]
    elif 'cookie' in prefs:
        session.headers.update({'cookie': prefs['cookie']})
        session.headers["x-ig-capabilities"] = "36oD"
        session.headers["cache-control"] = "no-cache"

    else:
        raise AssertionError("prefs.json contains neither headers nor username. Cannot authenticate to IG.")
    return session

#Ensure that the prefs are in correct format. If not, reformat them.
def ensure_prefs(prefs):
    if ('usernames' in prefs) and not ('ids' in prefs):
        print("Reformatting prefs.json, fetching user ids...")
        prefs['ids'] = {}
        for user in prefs['usernames']:
            prefs['ids'][fetch_user_id(user)] = user

        del prefs['usernames']

        with open('prefs.json','w') as prefsfile:
            json.dump(prefs,prefsfile,indent=4)
        main()
        raise SystemExit


def main():
    prefs = get_prefs()
    ensure_prefs(prefs)
    session = get_login_session(prefs)
    conn = get_db(prefs)
    fetch_stories(prefs, session, conn)
    download_stories(prefs, session, conn)

if __name__ == '__main__':
    main()
