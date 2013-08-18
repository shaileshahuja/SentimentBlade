__author__ = 'shailesh'

import os
import json
from Utils import UtilMethods as util
from YelpCrawler import YelpCrawler
from XMLHandler import LoadCrawledXMLFile,DumpSortedReviews
from God import God
from Sentiment import Sentiment


class SentimentBlade:

    def __init__(self, url):
        self.url = url

    def Run(self):
        #CRAWL
        crawlerOutputPath = "../files/CrawlerOutput2.xml"
        crawler = YelpCrawler(url, crawlerOutputPath)
        crawler.Crawl()

        #FILTER
        # TODO: filter reviews here
        reviews = LoadCrawledXMLFile(crawlerOutputPath)
        # now dump the output to xml file
        filePath = "../files/FilteredReviews.xml"
        DumpSortedReviews(reviews, filePath)

        #PARSE
        os.system("java -jar ../files/stanfordparser.jar xml " + filePath)

        #PREDICT
        lexicon = util.LoadLexiconFromCSV("../files/SentiWordNet_Lexicon_concise.csv")
        god = God(lexicon, True)
        parsedReviewsPath = os.path.join(os.path.dirname(filePath), "ParsedList.json")
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
            current["Label"] = Sentiment.GetSentimentClass(god.PredictReviewScore(sentences, notCount), 1)
            god.DumpDetails(sentences, notCount, current["Label"])

        #DUMP
        classifiedData = json.dumps(classificationData, indent=4)
        filename = os.path.join(os.path.dirname(filePath), 'PredictedList.json')
        with open(filename,'w') as file:
            file.write(classifiedData)
        print "Classification complete. Final output stored at:," + filename


if __name__ == "__main__":
    url = "http://www.yelp.com.sg/biz/kokkari-estiatorio-san-francisco"
    SB = SentimentBlade(url)
    SB.Run()
