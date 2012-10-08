#!/usr/bin/python

import sys
from os import system, listdir
from os.path import exists, expanduser
from BeautifulSoup import BeautifulSoup
from mechanize import Browser
from datetime import datetime
from urllib2 import HTTPError

from config import user, password
from to_mobi import to_mobi

URL = "http://www.instapaper.com"

PATH = expanduser("~/.config/instapaper/")

def copy_n_backend_files():
    if not exists("/media/Kindle/documents/"):
        return
    for file in filter(lambda x: x.startswith("instapaper-"), listdir(PATH)):
        if not exists("/media/Kindle/documents/%s" % file):
            print "Copying %s on Kindle..." % file
            system("cp '%s' /media/Kindle/documents/" % (PATH + file))
        print "Backup file %s" % file
        system("mv '%s' %sarchives/" % (PATH + file, PATH))

if __name__ == '__main__':
    file_name = "instapaper-%s.mobi" % datetime.now().strftime("%F")
    #if exists(PATH + file_name) or exists(PATH + "archives/%s" % file_name):
        #copy_n_backend_files()
        #print ".mobi file already downloaded today, end"
        #sys.exit(0)

    copy_n_backend_files()
    b = Browser()
    b.set_handle_robots(False)
    print "Login..."
    b.open(URL + "/user/login")
    b.select_form(nr=0)
    b["username"] = user
    b["password"] = password
    soup = BeautifulSoup(b.submit().read())
    #print "Get .mobi file..."
    #open(PATH + file_name, "w").write(b.open(URL + "/mobi").read())
    #print "Archive urls..."
    #for i in soup('a', title="Move to Archive")[:20]:
        #print i["href"]
        #b.open(URL + i["href"])
    print "Generating mobis.."
    bookmarks = soup.find("div", id="bookmark_list")("div", **{"class": lambda x: x and x.startswith("tableViewCell")})
    if bookmarks[0].text == u"No articles saved.":
        bookmarks = None
    while bookmarks:
        for i in bookmarks:
            print 'Handling "%s"' % i.find("a", "tableViewCellTitleLink").text
            try:
                to_mobi(b.open(URL + i.a["href"]).read(), i.find('span', 'host').text)
            except HTTPError:
                continue
            print "Archiving..."
            b.open(URL + i.a["href"].replace("read", "skip"))

        soup = BeautifulSoup(b.open("https://www.instapaper.com/u").read())
        bookmarks = soup.find("div", id="bookmark_list")("div", **{"class": lambda x: x and x.startswith("tableViewCell")})
        if bookmarks[0].text == u"No articles saved.":
            bookmarks = None

    copy_n_backend_files()
    print "end"
