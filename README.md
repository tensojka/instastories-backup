# Instagram Stories Backup
This script lets you download stories of select users.

# Install

First, clone this repo.

This requires Python 3 and pip to be installed. You can download Python 3 at python.org/downloads. pip should be installed automatically with Python.

Next, run this in terminal in the directory where you cloned this to.

```
# pip3 install -r requirements.txt
```

## Setup authentication with Instagram

Instagram allows only authenticated users to watch (and download) stories if you are not logged in. If you do not use 2FA on your IG account, it's preferred that you enter your username and password in the `prefs.json` file. If you do use 2FA or for some reason do not want to store your credentials in a file, you can login into Instagram from a browser and copy your session cookie to `prefs.json`.

### Username and password

Open the `prefs.json` file in a text editor and replace `insert username` and `insert password` with credentials for an Instagram account.

### Provide the cookies

You will need to get the cookie: header to be sent to Instagram to authenticate it's you.To obtain the cookie, login into http://instagram.com.

In Chrome: Open Developer Tools, change to the Network tab, reload `instagram.com`, scroll up in the request list, click instagram.com, find __cookie:__ under Request headers in the Headers pane. Copy the contents of __cookie:__. 

Then open `prefs.json` in a text editor. Add a `cookie` field like this:

```
...
"cookie": "PASTE HERE",
...
```

Note: older syntax with a `headers` field is still valid.

## Select users to backup

Edit the `"usernames:"` section of `prefs.json`, replacing the examples with usernames of users whose Stories you want to backup.

Usernames of Instagram users change pretty frequently. What doesn't change is their IDs.

After the first run of the script, the `usernames` field of `prefs.json` will get changed to `ids`, so don't be surprised.

# Usage
To run the program:
```
$ python3 main.py
```
You will have to run it every 24 hours in order to catch all Stories by the people you follow before they disappear.

You can set `quiet` in `prefs.json` to suppress all program output except errors. Useful for running via cron.

## Where do I find the downloaded media?

Media is saved in the directory specified in prefs.json as `filesdir`. By default, that is `./files`.

There is a folder for every user, named after their first encountered username. If a user changes their username, even their new Stories will get backed up to the folder with the users first encountered name.

## Navigating program output
Exclamation marks (!) mean that a Stories entry we tried to crawl is already in the database and dots (.) mean that an entry has been successfully added to the database.

# Issues?

If the script doesn't work for you, please check closed issues on Github. If you encounter a new error or the proposed solution doesn't work for you, open a new issue.

# Contributing

If you are thinking about adding a new feature to this script, please open an issue first to discuss if the new feature would be a good fit.