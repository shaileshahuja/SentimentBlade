"""
A crawler for www.yelp.com. Please note that Yelp does not encourage crawling (as described in their robots.txt).
I havent seen their TOS. Use at your own risk.
"""
__author__ = 'shailesh'

import urllib2
import sys
import HTMLParser
from bs4 import BeautifulSoup, SoupStrainer
import re
from Review import Review
from XMLHandler import DumpCrawlerOutputAsXML
import time


class YelpCrawler():

    def __init__(self, baseURL, filePath):
        self.filePath = filePath
        self.baseURL = baseURL
        self.IncompleteReviews = 0

    def GetPageHTML(self, url):
        """
        Takes in link to a page and parses out raw HTML
        """
        data = None
        while True:
            try:
                req = urllib2.Request(url)
                page = urllib2.urlopen(req)
                data = page.read()
                page.close()
                if "<title>Yelp Captcha</title>" in data[:1000]:
                    raise urllib2.URLError("Captcha page encountered")
                break
            except urllib2.URLError:
                print "GetPageHTML failed"
                print sys.exc_value
                time.sleep(5)
                continue
        return data

    def GetReviewCount(self, soup):
        """
        Takes in the soup object and return the number of reviews for that restaurant
        """
        countText = soup.find(True, id="total_reviews").text
        count = re.findall(r'[0-9]+',countText.strip())
        return int(count[0])

    def Crawl(self):
        reviews = []
        html = self.GetPageHTML(self.baseURL)
        soup = self.GetSoupElement(html)
        count = self.GetReviewCount(soup)
        reviews += self.GetAllReviewsInPage(soup)
        while len(reviews) + self.IncompleteReviews < count:
            print "Reviews Crawled:", len(reviews)
            url = self.baseURL + "?start=" + str(len(reviews) + self.IncompleteReviews)
            print "URL:", url
            html = self.GetPageHTML(url)
            print "HTML start\n", html[:1000],"\n HTML end"
            soup = self.GetSoupElement(html)
            reviews += self.GetAllReviewsInPage(soup)
        DumpCrawlerOutputAsXML(reviews, self.filePath)

    def GetSoupElement(self,html):
        try:
            soup = BeautifulSoup(html)
            return soup
        except HTMLParser.HTMLParseError:
            print "BeautifulSoup parsing failed"

    def GetAllReviewsInPage(self,soup):
        pageReviews = []
        # return [review.text for review in soup.findAll("p", class_="review_comment ieSucks")]
        for review in soup.findAll("li", class_="review clearfix  externalReview"):
            try:
                rating = review.find("meta", itemprop="ratingValue")["content"]
                url = review.find("a", class_="i-wrap ig-wrap-common i-orange-link-common-wrap")["href"]
                date = review.find("meta", itemprop="datePublished")["content"]
                userInfo = review.find("ul", class_="user-passport-info ieSucks")
                user = userInfo.find("a")["href"]
                reviewText = review.find("p", class_="review_comment ieSucks").text
                useful = review.find("li", class_="useful ufc-btn").find("span", recursive=False).text
                funny = review.find("li", class_="funny ufc-btn").find("span", recursive=False).text
                cool = review.find("li", class_="cool ufc-btn").find("span", recursive=False).text
                pageReviews.append(Review.CreateFromRawData(rating, url, date, user, reviewText, useful, funny, cool))
            except AttributeError:
                self.IncompleteReviews += 1
                continue
        return pageReviews

if __name__ == "__main__":
#Test out the code
    url = "http://www.yelp.com.sg/biz/kokkari-estiatorio-san-francisco"
    filePath = "../files/CrawlerOutput.xml"
    crawler = YelpCrawler(url, filePath)
    crawler.Crawl()