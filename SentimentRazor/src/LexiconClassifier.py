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

__author__ = 'shailesh'

class LexiconClassifier(object):

    def __init__(self):
        self.GlobalAdjList = {"disappointing","disappointed","fresh","freshly","tasty","delicious","poor","disappointment","badly","sadly","sucks","sucked","crispy","yelled","love","loved","loving","poorly","underwhelming"}
        self.stopWords = set(stopwords.words("english"))
        self.engnames = set(names.words())

    def classify(self, predicted, lower, upper):
        if predicted > lower:
            return 1
        elif predicted < upper:
            return -1
        else:
            return 0

    def confidence(self, predicted):
        # confidence for neutral reviews
        if math.fabs(predicted) <= 0.5:
            return 0.95
        if math.fabs(predicted) < 1.0:
            return 1.20 - math.fabs(predicted)
        # confidence for positive and negative reviews
        if math.fabs(predicted) > 7:
            return 0.95
        return math.fabs(predicted) / 7.30

    def PredictBase(self, adjectives, lexicon):
        list2 = [l for l in adjectives if l in lexicon and math.fabs(float(lexicon[l])) > 0.1]
        if 0 < len(list2):
            return 12.0/len(list2)
        #    elif len(list2) < 8:
        #        return 2.0
        else:
            return 1.0
    #    return 1.0


    def PredictMultiplier(self, word, dependencies, lexicon, words, i):
        multiplier = 1.0
        NegativeModifiers = {"not","n't", "no", "nothing","at"}
        PositiveModifiers = {"very","so","really", "super", "extremely"}
        NeutralModifiers = {"neither","nor"}
        TooExceptionList = {"good", "awesome","brilliant","kind","great","tempting","big","overpowering","full","filled","stuffed","perfect","rare"}
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


    def CalculateNotScore(self, notCount):
        if notCount >=10:
            notScore = 4
        elif notCount >=7:
            notScore = 2
        elif notCount >=4:
            notScore = 1
        else:
            notScore = 0
        return notScore


    def ExtractSentDetails(self, sentence):
        if "Adjectives" in sentence:
            adjList = [w.lower() for w in sentence["Adjectives"] if w.lower() not in self.stopWords and w.lower() not in self.engnames]
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
        AdjR = 0.0
        adjAll = []
        for sentence in sentences:
            # if sentence["Text"].startswith("Joanie is not helpful"):
            #     x = 1
            adjectives, dependencies = self.ExtractSentDetails(sentence)
            adjAll.extend(adjectives)
            allAdjectives = adjectives | self.GlobalAdjList
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
        base = self.PredictBase(adjAll, lexicon)  # to change the base of the multiplier according to number of adjectives and text length
        colortext = colored("Adjectives: " + str(AdjR) + "*" + str(base) + " - " + str(notScore) + " = " + str(AdjR*base - notScore),'red')
        print colortext


    def PredictSentiment(self, sentences, lexicon, notCount):
        AdjR = 0.0
        # if text.startswith("For more photos and reviews do check out fourleggedfoodies"):
        #     x = 1
        adjAll = []
        for sentence in sentences:
            adjectives, dependencies = self.ExtractSentDetails(sentence)
            adjAll.extend(adjectives)
            allAdjectives = adjectives | self.GlobalAdjList
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
        return AdjR - notScore


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

    def ClassificationFunction(self, lexiconPath, filePath, fileType):
        lexicon = util.LoadLexiconFromCSV(lexiconPath)
        posx, posy, negx, negy, neutx, neuty,accx,accy = 0,0,0,0,0,0,0,0
        maxnegf1 = maxneutf1 = maxposf1 = maxacc = 0
        for i in range(-1,0,1):
            for j in range(1, 0,-1):
                iterator, data = self.GetIter(filePath, fileType)
                predictedOverall = []
                expectedSentiment = []
                posCount = negCount = neutCount = sadCount = TotPos = TotNeg = TotNeut = 0
                while True:
                    try:
                        sentences, label, notCount, docId = self.NextElement(iterator, data, fileType)
                        if not sentences:
                            continue
                        if label == 'NULL':
                            break
                        label = int(label)
                        expectedSentiment.append(label)
                        predicted = self.PredictSentiment(sentences, lexicon, notCount)
                        predictedOverall.append(self.classify(predicted,j,i))
                        if label == 1:
                            TotPos+=1
                        elif label == -1:
                            TotNeg+=1
                        else:
                            TotNeut+=1
                        if self.classify(predicted,j,i) != label:
                            self.DumpDetails(sentences, lexicon, notCount, label)
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
                accuracy = util.accuracy(predictedOverall, expectedSentiment)
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
        print "Maximum Positive F1: ",'{:.2%}'.format(maxposf1), "at", posx, posy
        print "Maximum Negative F1: ",'{:.2%}'.format(maxnegf1), "at", negx, negy
        print "Maximum Neutral F1: ",'{:.2%}'.format(maxneutf1), "at", neutx, neuty
        cprint("Maximum Accuracy: " + '{:.2%}'.format(maxacc) + " at " + str(accx) + str(accy),'red')

if __name__ == '__main__':
    clr = LexiconClassifier()
    filePath = "/home/shailesh/SentimentRazor/files/ParsedReviewList.xml"
    fileType = 'xml'
    lexiconPath = "/home/shailesh/SentimentRazor/files/SentiWordNet_Lexicon_concise.csv"
    clr.ClassificationFunction(lexiconPath, filePath, fileType)


