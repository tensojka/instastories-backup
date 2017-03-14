import requests
import sqlite3

conn = sqlite3.connect('stories.sqlite3')

ids_tobackup = {
    '325362233': 'cestujurada',
    '655295824': 'hoschicz',
    '4197576288': 'malejbuk',
    '270679163': 'nejskvelejsi',
    '2031881575': 'jakub.sustr2',
    '503530161': 'chcukiwi',
    '551854863': 'chceskiwi',
    '392366908': 'petahrdina_',
    '1231421545': 'sara_smejkalova',
    '3250038853': 'tobiaskosir',
    '1693587948': 'vopelkova.desi',
    '1470027527': 'nikcakikca007',
    '1245472971': 'filipvalicek'
}

while len(ids_tobackup) > 0:
    pair = ids_tobackup.popitem()
    headers = {
        'cookie': "ds_user_id=655295824; sessionid=IGSC4d666e5ff7db9db3e4262f1fd75c20fb0379f358711eaa86603b7af68ce5c0ea%3AW2miaupIRUAT1m3OBlAC1xs5hniIFhGL%3A%7B%22asns%22%3A%7B%22time%22%3A1489478310%2C%2278.102.117.227%22%3A6830%7D%2C%22last_refreshed%22%3A1489478310.2239192%2C%22_token_ver%22%3A2%2C%22_platform%22%3A4%2C%22_auth_user_backend%22%3A%22accounts.backends.CaseInsensitiveModelBackend%22%2C%22_token%22%3A%22655295824%3Azi6WHai8n0mRXjj3dYonEslwAXxXYOh8%3A170836c056f67eb80949b6bbd4e4cd48a96fee6d947108d0f23224d8045c95b4%22%2C%22_auth_user_id%22%3A655295824%2C%22_auth_user_hash%22%3A%22%22%7D",
        'user-agent': "Instagram 10.3.2 (iPhone7,2; iPhone OS 9_3_3; en_US; en-US; scale=2.00; 750x1334) AppleWebKit/420+",
        'cache-control': "no-cache"
        }
    response = requests.request("GET", "https://i.instagram.com/api/v1/feed/user/655295824/reel_media/", headers=headers)
    print(response.text)
    #CREATE TABLE `entries` (
    #    `id`	TEXT UNIQUE,
    #    `url`	TEXT,
    #    `userid`	TEXT,
    #    `username`	TEXT
    #);