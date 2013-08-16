from __future__ import division
import simplejson as json
from Utils import UtilMethods as util
from termcolor import cprint
import math
from xml.etree import ElementTree as ET
from Sentiment import Sentiment
from God import God

__author__ = 'shailesh'


class PerformanceTest:

    def __init__(self, lexPath, docPath):
        self.lexicon = util.LoadLexiconFromCSV(lexPath)
        self.docPath = docPath
        if docPath.endswith("json"):
            self.docType = "json"
        elif docPath.endswith("xml"):
            self.docType = "xml"
        else:
            self.docType = "json"

    def GetIter(self, filePath, filetype):
        """

        :param filePath:
        :param filetype:
        :return:
        """
        assert filetype in ['xml', 'json']
        if filetype == 'xml':
            root = ET.parse(filePath).getroot()
            return iter(root), None
        if filetype == 'json':
            with open(filePath, 'r') as file1:
                TrainingFile = file1.read()
            TrainingData = json.loads(TrainingFile)
            return iter(range(1, len(TrainingData["ClassificationModel"]) + 1)), TrainingData["ClassificationModel"]

    def NextXMLElement(self, iterator):
        doc = next(iterator)
        sentences = []
        label = None
        docId = doc.get('id')
        for element in doc:
            if element.tag == "stars":
                stars = element.text
            elif element.tag == "polarity":
                label = element.text
            elif element.tag == "sentence":
                sentence = dict()
                for data in element:
                    if data.tag == "text":
                        sentence["Text"] = data.text
                    elif data.tag == "adjectives":
                        if data.text is not None:
                            sentence["Adjectives"] = data.text.split()
                    elif data.tag == "dependencies":
                        if data.text is not None:
                            sentence["Dependencies"] = data.text.split()
                        else:
                            sentence["Dependencies"] = []
                sentences.append(sentence)
        return sentences, label, 0, docId

    def NextJSONElement(self, iterator, data):
        docId = next(iterator)
        current = data[str(docId)]
        sentences = []
        notCount = current["NotCount"]
        if "Sentences" in current:
            if not isinstance(current["Sentences"], list):
                current["Sentences"] = [current["Sentences"]]
            sentences = current["Sentences"]
        label = current["Label"]
        return sentences, label, notCount, docId

    def NextElement(self, iterator, data, filetype):
        if filetype == 'json':
            return self.NextJSONElement(iterator, data)
        if filetype == 'xml':
            return self.NextXMLElement(iterator)

    def PerformTest(self):
        god = God(True)
        god.SetDebugParameters(7, -7)
        posx, negx, neutx, accx, = 0, 0, 0, 0
        maxnegf1 = maxneutf1 = maxposf1 = maxacc = 0
        for threshold in range(1, 0, -1):
            iterator, data = self.GetIter(self.docPath, self.docType)
            predictedOverall = []
            expectedSentiment = []
            posCount = negCount = neutCount = sadCount = TotPos = TotNeg = TotNeut = 0
            while True:
                try:
                    sentences, label, notCount, docId = self.NextElement(iterator, data, self.docType)
                    if not sentences:
                        continue
                    if label == 'NULL':
                        break
                    label = int(label)
                    expectedSentiment.append(label)
                    predicted = god.PredictReviewScore(sentences, self.lexicon, notCount, label)
                    predictedOverall.append(Sentiment.GetSentimentClass(predicted, threshold))
                    if label == Sentiment.POSITIVE:
                        TotPos += 1
                    elif label == Sentiment.NEGATIVE:
                        TotNeg += 1
                    else:
                        TotNeut += 1
                    if god.DebugRequested(predicted, label):
                        print "ID", docId, "\n"
                        sadCount += 1
                except StopIteration:
                    break

            print "Sad Count:", sadCount
            pos_prec = util.precision_with_class(predictedOverall, expectedSentiment, 1)
            neg_prec = util.precision_with_class(predictedOverall, expectedSentiment, -1)
            neut_prec = util.precision_with_class(predictedOverall, expectedSentiment, 0)
            pos_rec = util.recall_with_class(predictedOverall, expectedSentiment, 1)
            neg_rec = util.recall_with_class(predictedOverall, expectedSentiment, -1)
            neut_rec = util.recall_with_class(predictedOverall, expectedSentiment, 0)
            pos_f1 = util.f1_with_class(predictedOverall, expectedSentiment, 1)
            neg_f1 = util.f1_with_class(predictedOverall, expectedSentiment, -1)
            neut_f1 = util.f1_with_class(predictedOverall, expectedSentiment, 0)
            accuracy = util.accuracy(predictedOverall,expectedSentiment)
            print "Current Positive stats (", threshold, "): ","\t", '{:.2%}'.format(pos_prec), "\t", '{:.2%}'.format(pos_rec), "\t", '{:.2%}'.format(pos_f1)
            print "Current Negative stats (", threshold, "): ", "\t",'{:.2%}'.format(neg_prec), "\t", '{:.2%}'.format(neg_rec), "\t", '{:.2%}'.format(neg_f1)
            print "Current Neutral stats (", threshold, "): ", "\t",'{:.2%}'.format(neut_prec), "\t", '{:.2%}'.format(neut_rec), "\t", '{:.2%}'.format(neut_f1)
            cprint("Current Accuracy ( " + str(threshold) + " ):\t\t\t" + '{:.2%}'.format(accuracy),'red')
            if pos_f1 > maxposf1:
                maxposf1 = pos_f1
                posx = threshold
            if neg_f1 > maxnegf1:
                maxnegf1 = neg_f1
                negx = threshold
            if neut_f1 > maxneutf1:
                maxneutf1 = neut_f1
                neutx = threshold
            if accuracy > maxacc:
                maxacc = accuracy
                accx = threshold
        print "Maximum Positive F1: ", '{:.2%}'.format(maxposf1), "at", posx
        print "Maximum Negative F1: ", '{:.2%}'.format(maxnegf1), "at", negx
        print "Maximum Neutral F1: ", '{:.2%}'.format(maxneutf1), "at", neutx
        cprint("Maximum Accuracy: " + '{:.2%}'.format(maxacc) + " at " + str(accx), 'red')

        #    sentences = sent_tokenize(text)
        #    predictedSentences = PredictAllSentences(sentences, predictedOverall, lexicon)

if __name__ == "__main__":
    jsonFile = "../files/1000NTLKMovieReviews.json"
    textFile = "../files/1000HungryGoWhereReviews.txt"
    textSFile = "../files/100HungryGoWhereReviews.txt"
    XMLFile = "../files/1000YelpKokariEstoriatoReviews.xml"
    lexPath = "../files/SentiWordNet_Lexicon_concise.csv"
    # se = PerformanceTest(lexPath, jsonFile)
    se = PerformanceTest(lexPath, XMLFile)
    # se = PerformanceTest(lexPath, textFile)
    # se = PerformanceTest(lexPath, textSFile)
    se.PerformTest()

