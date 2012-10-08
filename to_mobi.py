#!/usr/bin/env python
# encoding: utf-8

import re
import unidecode
from os import system
from os.path import exists, expanduser
from urllib import urlretrieve
from BeautifulSoup import BeautifulSoup
from datetime import datetime

template = """
<html>
<head>
    <title>%s</title>
</head>
<body>
%s
</body>
</html>
"""

def slugify(str):
    str = unidecode.unidecode(str).lower()
    return re.sub(r'\W+','-',str)

def to_html(content, host):
    soup = BeautifulSoup(content, convertEntities=BeautifulSoup.HTML_ENTITIES)
    title = soup.find("div", id="titlebar").h1.text
    title += " [%s]" % host
    soup.find("div", id="titlebar").a.img.extract()
    body = soup.find("div", id="story")

    images = {}

    for i, img in enumerate(filter(lambda x: x.get("src", "").startswith("http"), body("img"))):
        if images.get(img["src"]):
            img["src"] = images[img["src"]]
            continue
        extension = img["src"].split("/")[-1].split(".")[-1]

        print "Downloading %s ..." % img["src"]
        try:
            urlretrieve(img["src"], "build/img/%s.%s" % (i, extension))
        except (IOError, UnicodeError):
            try:
                urlretrieve(img["src"], "build/img/%s.%s" % (i, extension))
            except (IOError, UnicodeError):
                images[img["src"]] = img["src"]
                continue

        images[img["src"]] = "img/%s.%s" % (i, extension)
        img["src"] = "img/%s.%s" % (i, extension)

    return template % (title.encode("Utf-8"), "%s\n%s" % (soup.find("div", id="titlebar"), body)), title

def to_mobi(content, host):
    print "Parse html..."
    html, title = to_html(content, host)
    title = slugify(title)
    file_name = "instapaper-%s-%s.html" % (title[:80], datetime.now().strftime("%F"))
    file_name_mobi = ".".join(file_name.split(".")[:-1]) + ".mobi"
    path =  "/home/psycojoker/code/python/insta/build/"
    save_dir = expanduser("~/.config/instapaper/")
    if not exists(save_dir + file_name_mobi):
        open(path + file_name, "w").write(html)
        print "Generating .mobi..."
        system("cd %s && ebook-convert %s %s > %s/.log" % (path, file_name, file_name_mobi, path))
        system("mv %s%s %s"% (path, file_name_mobi, save_dir))
        print "done"
    else:
        print "Already downloaded, skip"

if __name__ == '__main__':
    print to_html(open("test.html").read())
