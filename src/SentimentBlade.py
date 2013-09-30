__author__ = 'shailesh'

import os
import json
from Utils import UtilMethods as util
from YelpCrawler import YelpCrawler
from XMLHandler import LoadCrawledXMLFile,DumpSortedReviews
from Angel import Angel
from Sentiment import Sentiment


class SentimentBlade:

    def __init__(self, url):
        self.url = url

    def Run(self):
        crawlerOutputPath = "../files/CrawlerOutput2.xml"
        self.crawl(crawlerOutputPath)

        filePath = "../files/FilteredReviews.xml"
        self.filter(crawlerOutputPath, filePath)

        self.parse(filePath)

        classificationData = self.predict(filePath)
        filename = os.path.join(os.path.dirname(filePath), 'YelpPredictedReviews.json')
        self.dump(classificationData, filename)

    def crawl(self, crawlerOutputPath):
        #CRAWL
        crawler = YelpCrawler(url, crawlerOutputPath)
        crawler.Crawl()

    def parse(self, filePath):
        #PARSE
        _, fileExtension = os.path.splitext(filePath)
        os.system("java -jar ../files/stanfordparser.jar " + fileExtension[1:] + " " + filePath)

    def filter(self, crawlerOutputPath, filePath):
         #FILTER
        # TODO: filter reviews here
        reviews = LoadCrawledXMLFile(crawlerOutputPath)
        # now dump the output to xml file
        DumpSortedReviews(reviews, filePath)

    def predict(self, filePath):
         #PREDICT
        lexicon = util.LoadLexiconFromCSV("../files/lexicons/SentiWordNet_Lexicon_concise.csv")
        angel = Angel(lexicon, True)
        parsedReviewsPath = os.path.join(os.path.dirname(filePath), "YelpParsedReviews.json")
        with open(parsedReviewsPath, 'r') as file:
            TrainingFile = file.read()
        classificationData = json.loads(TrainingFile)
        for k in range(len(classificationData["ClassificationModel"])):
            current = classificationData["ClassificationModel"][str(k + 1)]
            notCount = current["NotCount"]
            if "Sentences" in current:
                if not isinstance(current["Sentences"], list):
                    current["Sentences"] = [current["Sentences"]]
                sentences = current["Sentences"]
            else:
                continue
            current["Label"] = Sentiment.GetSentimentClass(angel.PredictReviewScore(sentences, notCount), 1)
            angel.DumpDetails(sentences, current["Label"])
        return classificationData

    def dump(self, classificationData, filename):
           #DUMP
        classifiedData = json.dumps(classificationData, indent=4)
        with open(filename, 'w') as file:
            file.write(classifiedData)
        print "Classification complete. Final output stored at:," + filename


if __name__ == "__main__":
    url = "http://www.yelp.com.sg/biz/kokkari-estiatorio-san-francisco"
    SB = SentimentBlade(url)
    # SB.Run()
    SB.parse("../files/tweets.txt")