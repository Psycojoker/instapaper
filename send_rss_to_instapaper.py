import sys
import requests
from os.path import expanduser, exists
from json import load, dumps
from feedparser import parse

from config import user, password

RSS = expanduser("~/.config/instapaper/urls")
DB = expanduser("~/.config/instapaper/.rss.db")

if not exists(RSS) or not open(RSS, "r").read():
    print "I don't have urls to process, end"
    sys.exit(0)

if not exists(DB):
    open(DB, "w").write(dumps([]))

db = load(open(DB))

for rss in open(RSS):
    for url in map(lambda x: x.link, parse(rss).entries):
        if url in db:
            continue

        print "Adding %s..." % url
        response = requests.post("http://www.instapaper.com/api/add",
                      params={"username": user,
                              "password": password,
                              "url": url})
        if response.status_code == 201:
            db.append(url)
        else:
            print "ERROR: can't append %s: reponse code: %s" % (url, response.status_code)

open(DB, "w").write(dumps(db, indent=4))
