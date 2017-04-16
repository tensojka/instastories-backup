# Instagram Stories Backup
Crawl stories of select Instagram users and backup them.
# Setup and install
First, clone this repo.

## Obtain cookies

You will need to get the cookie: header to be sent to Instagram to authenticate it's you. Instagram allows only authenticated users to watch Stories. To obtain the cookie, login into (http://instagram.com)[instagram.com].

Chrome: Open Developer Tools, change to the Network tab, reload `instagram.com`, scroll up in the request list, click instagram.com, find __cookie:__ under Request headers in the Headers pane. Copy the contents of __cookie:__, and paste them into your `prefs.json` in place of whatever was in `cookie:` field now.

## Setup users to backup
You will need to obtain the IDs of IG users whose Stories you want to backup. You can use [this service](https://smashballoon.com/instagram-feed/find-instagram-user-id/) to find them.

Edit the `"ids:"` section of `prefs.json`, replacing the examples with IDs and usernames of users whose Stories you want to backup.

## Install Python and dependencies
This requires Python 3 and pip3 to be installed. You can download Python 3 at [python.org/downloads](https://www.python.org/downloads/). pip3 will be installed automatically with Python.

Next, run this in terminal in the directory where you cloned this to.
```
# pip3 install requests
```

# Running
To run the program:
```
$ python3 main.py
```
You will have to run it every 24 hours in order to catch all Stories by the people you follow before they disappear

## Navigating program output
Exclamation marks (!) mean that a Stories entry we tried to crawl is already in the database and dots (.) mean that an entry has been successfully added to the database.

# Working with collected data
The script saves all metadata into the SQLite3 database `stories.sqlite3` and by default downloads media into files/