from __future__ import division
import simplejson as json
from Utils import UtilMethods as util
from nltk.tokenize import wordpunct_tokenize
from nltk.corpus import stopwords,names
from termcolor import colored,cprint
import nltk, math
from collections import defaultdict
from xml.etree import ElementTree as ET
import copy
from Sentiment import Sentiment

__author__ = 'shailesh'


class SentimentEngine:
    stopWords = set(stopwords.words())
    engNames = set(names.words())
    GlobalAdjList = {"disappointing", "disappointed", "disappointment", "fresh", "freshly", "tasty", "delicious",
                     "poor", "badly", "sadly", "sucks", "sucked", "crispy", "yelled", "love", "loved", "loving",
                     "poorly", "underwhelming"}

    def __init__(self, lexPath, docPath):
        self.lexicon = util.LoadLexiconFromCSV(lexPath)
        self.docPath = docPath
        if docPath.endswith("json"):
            self.docType = "json"
        elif docPath.endswith("xml"):
            self.docType = "xml"
        else:
            self.docType = "json"

    def GetSentimentClass(self, score, positiveThreshold=1, negativeThreshold=-1):
        """
        This method returns the type of sentiment given the score of the review.
        :param score: The score of a review
        :param positiveThreshold: If score is higher than this threshold, review is considered positive
        :param negativeThreshold: If score is lower than this threshold, review is considered negative
        """
        if score > positiveThreshold:
            return Sentiment.POSITIVE
        elif score < negativeThreshold:
            return Sentiment.NEGATIVE
        else:
            return Sentiment.NEUTRAL

    def PredictBase(self, adjectives, lexicon):
        """
        Predict the base of the multiplier using the number of polar adjectives.
        The values have been determined experimentally to maximize results.
        """
        # Get the list of Adjectives which have sentiment polarity greater than 0.1
        PolarAdjList = [l for l in adjectives if l in lexicon and math.fabs(float(lexicon[l])) > 0.1]
        if len(PolarAdjList) > 0:
            return 12.0/len(PolarAdjList)
        #    elif len(list2) < 8:
        #        return 2.0
        else:
            return 1.0
    #    return 1.0

    def PredictMultiplier(self, word, dependencies, lexicon, words, i):
        """
        Given a word, calculate how other words affect the polarity of this word.
        E.g: "not good" will change the polarity of "good" to negative.
        Returns a multiplier for the word.
        """
        multiplier = 1.0 # start with the default multiplier of one, which means no change in polarity
        NegativeModifiers = {"not","n't", "no", "nothing","at"}
        PositiveModifiers = {"very","so","really", "super", "extremely"}
        NeutralModifiers = {"neither","nor"}
        TooExceptionList = {"good", "awesome","brilliant","kind","great","tempting","big",
                            "overpowering","full","filled","stuffed","perfect","rare"}
        DilutionList = {"little", "bit"}
        modifierSet = set()
        for rel in dependencies:
            modifierSet |= dependencies[rel]
        if i > 0 and words[i - 1].lower() == "too" and word not in TooExceptionList:
            if word in ["much", "many"]:
                multiplier = -100.0
            elif float(lexicon[word]) < 0:
                multiplier *= 2.0
            else:
                multiplier *= -0.5
        elif modifierSet & NegativeModifiers:
            multiplier *= -1.0
        elif modifierSet & PositiveModifiers:
            multiplier *= 2.0
        elif modifierSet & NeutralModifiers:
            multiplier *= 0.0
        elif i > 0:
            if words[i - 1].lower() == "not":
                multiplier *= -1.0

        if (i > 0 and words[i - 1].lower() in DilutionList) or (i > 1 and words[i - 2].lower() in DilutionList):
            multiplier *= 0.5
        return multiplier
        # multiplier = 1.0
        # NegativeModifiers = ["not","n't", "no", "nothing"]
        # PositiveModifiers = ["very","so","really"]
        # NeutralModifiers = ["neither","nor"]
        # TooExceptionList = ["good", "awesome","brilliant","kind","great","tempting","big","overpowering","full","filled","stuffed","perfect","rare"]
        # if i > 0:
        #     if words[i-1].lower() == "not" and words[i].lower() in lexicon:
        #         multiplier*=-0.5
        #     elif (words[i-1].lower() in NegativeModifiers or (len(words[i-1]) > 2 and words[i-1].lower().endswith("nt") and words[i-1].lower()[-3] not in ['a','e','i','o','u']) or words[i-1].lower().endswith("n't")) \
        #         or (i > 1 and (words[i-2].lower() in NegativeModifiers or (len(words[i-2]) > 2 and words[i-2].lower().endswith("nt") and words[i-2].lower()[-3] not in ['a','e','i','o','u']) or
        #                            words[i-2].lower().endswith("n't") or (words[i-1].lower() == "t" and words[i-2].lower() == "'")))or (i > 2 and words[i-2].lower() == "t" and words[i-3].lower() == "'"):
        #         multiplier *=-1.0
        #     elif words[i-1].lower() in PositiveModifiers:
        #         multiplier *= 2.0
        #     elif words[i-1].lower() in NeutralModifiers or (i > 1 and words[i-2].lower() in NeutralModifiers):
        #         multiplier *= 0.0
        #     elif words[i-1].lower() == "too" and words[i].lower() not in TooExceptionList and words[i].lower() in lexicon:
        #         if words[i].lower() in ["much","many"]:
        #             multiplier = -100.0
        #         elif float(lexicon[words[i].lower()]) < 0:
        #             multiplier *= 2.0
        #         else:
        #             multiplier *= -0.5
        # return multiplier

    def CalculateNotScore(self, notCount):
        """
        Method to calculate the reduction in overall score based on the negativity in the review.
        The values have been determined experimentally.
        Ideally, this method should not be used, as it is against the objective of this program.
        Usage will be removed later.
        """
        if notCount >= 10:
            notScore = 4
        elif notCount >= 7:
            notScore = 2
        elif notCount >= 4:
            notScore = 1
        else:
            notScore = 0
        return notScore

    def ExtractSentDetails(self, sentence):
        """
        Method to extract properties form a sentence object.
        :param sentence: The dictionary of sentence properties extracted from the JSON/XML sentence element
        """
        if "Adjectives" in sentence:
            adjList = [w.lower() for w in sentence["Adjectives"] if w.lower() not in SentimentEngine.stopWords and w.lower() not in SentimentEngine.engNames]
            adjectives = set(adjList)
        else:
            adjectives = set()
        dependencies = defaultdict(dict)
        if "Dependencies" in sentence:
            if not isinstance(sentence["Dependencies"],list):
                sentence["Dependencies"] = [sentence["Dependencies"]]
            for dep in sentence["Dependencies"]:
                line = dep.split(',')
                if len(line) != 3:
                    continue
                relation, adj, other = line
                adj, other = adj.lower(), other.lower()
                if relation in {'amod', 'acomp', 'ccomp', 'pobj', 'dep'}:
                    adj, other = other, adj
                if relation not in dependencies[adj]:
                    dependencies[adj][relation] = set()
                dependencies[adj][relation].add(other)
                if relation == 'conj':
                    adjectives.add(other)
        dictconj, other = defaultdict(dict), None
        for adj in dependencies:
            if 'conj' in dependencies[adj]:
                for other in dependencies[adj]['conj']:
                    dictconj[other] = copy.deepcopy(dependencies[adj])
        for adj in dictconj:
            for relation in dictconj[adj]:
                if relation not in dependencies[adj]:
                    dependencies[adj][relation] = set()
                dependencies[adj][relation] |= dictconj[adj][relation]
        return adjectives, dependencies

    def DumpDetails(self, sentences, lexicon, notCount, label):
        """
        This method uses the same logic as predict sentiment to rate reviews.
        However, all the small details on how the calculation is done are printed for a review
        """
        AdjR = 0.0
        adjAll = []
        for sentence in sentences:
            # if sentence["Text"].startswith("Joanie is not helpful"):
            #     x = 1
            adjectives, dependencies = self.ExtractSentDetails(sentence)
            adjAll.extend(adjectives)
            allAdjectives = adjectives | SentimentEngine.GlobalAdjList
            AdjS = 0.0
            words = wordpunct_tokenize(sentence["Text"])
            if len(words) <= 3:
                allAdjectives |= set([x.lower() for x in words])
            for i in range(len(words)):
                word = words[i].lower()
                if word in {"but", "if"}:
                    AdjS = 0.0
                    print words[i],
                elif word in allAdjectives and word in lexicon:
                    multiplier = self.PredictMultiplier(word, dependencies[word],lexicon, words, i)
                    score = float(lexicon[word]) * multiplier
                    if multiplier < 1:
                        colortext = colored(words[i] + " (" + '{:.3}'.format(score) + ")", 'red',None,['underline'])
                    elif multiplier > 1:
                        colortext = colored(words[i] + " (" + '{:.3}'.format(score) + ")", 'red',None,['bold'])
                    else:
                        colortext = colored(words[i] + " (" + '{:.3}'.format(score) + ")", 'red')
                    AdjS += score
                    print colortext,
                else:
                    print words[i],
            print
            colortext = colored("Adjectives: " + '{:.3}'.format(AdjS),'red')
            print colortext
            AdjR += AdjS
        print
        notScore = self.CalculateNotScore(notCount)
        print "Label:", label, "Not Count:", notCount
        base = self.PredictBase(adjAll, lexicon)
        colortext = colored("Adjectives: " + str(AdjR) + "*" + str(base) + " - " + str(notScore) + " = " + str(AdjR*base),'red')
        print colortext

    def PredictSentiment(self, sentences, lexicon, notCount):
        """
        This method predicts the sentiment of a given review.
        """
        AdjR = 0.0
        # if text.startswith("For more photos and reviews do check out fourleggedfoodies"):
        #     x = 1
        adjAll = []
        for sentence in sentences:
            adjectives, dependencies = self.ExtractSentDetails(sentence)
            adjAll.extend(adjectives)
            allAdjectives = adjectives | SentimentEngine.GlobalAdjList
            AdjS = 0.0
            words = wordpunct_tokenize(sentence["Text"])
            if len(words) <= 3:
                allAdjectives |= set([x.lower() for x in words])
            for i in range(len(words)):
                word = words[i].lower()
                if word in {"but", "if"}:
                    AdjS = 0.0
                elif word in allAdjectives and word in lexicon:
                    AdjS += float(lexicon[word]) * self.PredictMultiplier(word, dependencies[word], lexicon, words, i)
            AdjR += AdjS
        AdjR *= self.PredictBase(adjAll, lexicon)
        notScore = self.CalculateNotScore(notCount)
        return AdjR

    def GetIter(self, filePath, filetype):
        assert filetype in ['xml', 'json']
        if filetype == 'xml':
            root = ET.parse(filePath).getroot()
            return iter(root), None
        if filetype == 'json':
            with open(filePath,'r') as file:
                TrainingFile = file.read()
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
                        if not data.text == None:
                            sentence["Adjectives"] = data.text.split()
                    elif data.tag == "dependencies":
                        if not data.text == None:
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

    def classify(self):
        posx, posy, negx, negy, neutx, neuty, accx, accy = 0, 0, 0, 0, 0, 0, 0, 0
        maxnegf1 = maxneutf1 = maxposf1 = maxacc = 0
        for i in range(-1, 0, 1):
            for j in range(1, 0, -1):
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
                        predicted = self.PredictSentiment(sentences, self.lexicon, notCount)
                        predictedOverall.append(self.GetSentimentClass(predicted, j, i))
                        if label == Sentiment.POSITIVE:
                            TotPos += 1
                        elif label == Sentiment.NEGATIVE:
                            TotNeg += 1
                        else:
                            TotNeut += 1
                        if self.GetSentimentClass(predicted, j, i) != label:
                            self.DumpDetails(sentences, self.lexicon, notCount, label)
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
                print "Current Positive stats (", j,i,"): ","\t", '{:.2%}'.format(pos_prec),"\t", '{:.2%}'.format(pos_rec),"\t",'{:.2%}'.format(pos_f1)
                print "Current Negative stats (", j,i,"): ", "\t",'{:.2%}'.format(neg_prec),"\t",'{:.2%}'.format(neg_rec),"\t",'{:.2%}'.format(neg_f1)
                print "Current Neutral stats (", j,i,"): ", "\t",'{:.2%}'.format(neut_prec),"\t",'{:.2%}'.format(neut_rec),"\t",'{:.2%}'.format(neut_f1)
                cprint("Current Accuracy ( " + str(j) + " " + str(i) + " ):\t\t\t" + '{:.2%}'.format(accuracy),'red')
                if pos_f1 > maxposf1:
                    maxposf1 = pos_f1
                    posx = j
                    posy = i
                if neg_f1 > maxnegf1:
                    maxnegf1 = neg_f1
                    negx = j
                    negy = i
                if neut_f1 > maxneutf1:
                    maxneutf1 = neut_f1
                    neutx = j
                    neuty = i
                if accuracy > maxacc:
                    maxacc = accuracy
                    accx = j
                    accy = i
        print "Maximum Positive F1: ", '{:.2%}'.format(maxposf1), "at", posx, posy
        print "Maximum Negative F1: ", '{:.2%}'.format(maxnegf1), "at", negx, negy
        print "Maximum Neutral F1: ", '{:.2%}'.format(maxneutf1), "at", neutx, neuty
        cprint("Maximum Accuracy: " + '{:.2%}'.format(maxacc) + " at " + str(accx) + str(accy), 'red')

        #    sentences = sent_tokenize(text)
        #    predictedSentences = PredictAllSentences(sentences, predictedOverall, lexicon)

if __name__ == "__main__":
    jsonFile = "../files/MovieReviews.json"
    textFile = "../files/ParsedTrainingData.txt"
    XMLFile = "../files/ParsedReviewList.xml"
    lexPath = "../files/SentiWordNet_Lexicon_concise.csv"
#     se = SentimentEngine(lexPath, jsonFile)
#     se = SentimentEngine(lexPath, XMLFile)
    se = SentimentEngine(lexPath, textFile)
    se.classify()

