#!/usr/bin/python

import sys
import urllib
import re
import json

from bs4 import BeautifulSoup

import socket

socket.setdefaulttimeout(10)

cache = {}
with open("../files/tweets.txt", 'w') as handle:
    for line in open(sys.argv[1]):
        fields = line.rstrip('\n').split('\t')
        sid = fields[0]
        uid = fields[1]

        #url = 'http://twitter.com/%s/status/%s' % (uid, sid)
        #print url

        tweet = None
        text = "Not Available"
        if sid in cache:
            text = cache[sid]
        else:
            try:
                f = urllib.urlopen("http://twitter.com/%s/status/%s" % (uid, sid))
                #Thanks to Arturo!
                html = f.read().replace("</html>", "") + "</html>"
                soup = BeautifulSoup(html)

                jstt = soup.find_all("p", "js-tweet-text")
                tweets = list(set([x.get_text() for x in jstt]))
                #print len(tweets)
                #print tweets
                if (len(tweets)) > 1:
                    continue

                text = tweets[0]
                cache[sid] = tweets[0]

                for j in soup.find_all("input", "json-data", id="init-data"):
                    js = json.loads(j['value'])
                    if "embedData" in js:
                        tweet = js["embedData"]["status"]
                        text = js["embedData"]["status"]["text"]
                        cache[sid] = text
                        break
            except Exception:
                continue

        if tweet is not None and tweet["id_str"] != sid:
            text = "Not Available"
            cache[sid] = "Not Available"
        text = text.replace('\n', ' ', )
        text = re.sub(r'\s+', ' ', text)
        #print json.dumps(tweet, indent=2)
        handle.write(text.encode('utf-8'))
        handle.write("\n")
        if fields[2] == '"positive"':
            handle.write("1")
        elif fields[2] == '"negative"':
            handle.write("-1")
        else:
            handle.write("0")
        handle.write("\n")
        print "\t".join(fields + [text]).encode('utf-8')
