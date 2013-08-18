from God import God

__author__ = 'shailesh'

import os
import sys
import math
from nltk.tokenize import wordpunct_tokenize
from nltk.corpus import stopwords, names
import json
from Utils import UtilMethods as util
from YelpCrawler import YelpCrawler
from XMLHandler import LoadCrawledXMLFile,DumpSortedReviews

class SentimentBlade:

    def __init__(self, url):
        self.url = url

    def Run(self):
        #CRAWL
        crawlerOutputPath = "../files/CrawlerOutput.xml"
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
        god = God(True)
        filename = os.path.join(os.path.dirname(filePath),"ParsedList.json")
        with open(filename, 'r') as file:
            TrainingFile = file.read()
        lexicon = util.LoadLexiconFromCSV(os.path.join(os.path.dirname(sys.argv[0]),"SentiWordNet_Lexicon_concise.csv"))
        classificationData = json.loads(TrainingFile)
        for k in range(len(classificationData["ClassificationModel"])):
            current = classificationData["ClassificationModel"][str(k + 1)]
            notCount = current["NotCount"]
            if "Sentences" in current:
                if not isinstance(current["Sentences"],list):
                    current["Sentences"] = [current["Sentences"]]
                sentences = current["Sentences"]
            else:
                continue
            current["Label"] = classify(PredictSentiment(sentences, lexicon, notCount),1,1)
        return classificationData

filePath = "../files/samples.txt"

classifiedData = json.dumps(PredictAndAppendLabel(classificationData), indent = 4)
filename = os.path.join(os.path.dirname(filePath), 'PredictedList.json')
with open(filename,'w') as file:
    file.write(classifiedData)

print "Classification complete. Final output stored at:," + filename

if __name__ == "__main__":
    url = "http://www.yelp.com.sg/biz/kokkari-estiatorio-san-francisco"
    SB = SentimentBlade(url)
    SB.Run()
