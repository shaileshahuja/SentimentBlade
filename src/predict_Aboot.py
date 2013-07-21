from __future__ import division
import simplejson as json
from Utils import UtilMethods as util
from nltk.tokenize import wordpunct_tokenize
from nltk.corpus import stopwords,names
from termcolor import colored,cprint
import nltk, math

__author__ = 'shailesh'

def classify(predicted, lower, upper):
    if predicted > lower:
        return 1
    elif predicted < upper:
        return -1
    else:
        return 0

def PredictBase(adjectives, lexicon):
    list2 = [l for l in adjectives if l in lexicon and math.fabs(float(lexicon[l])) > 0.1]
    if 0 < len(list2):
        return 12.0/len(list2)
    #    elif len(list2) < 8:
    #        return 2.0
    else:
        return 1.0
#    return 1.0

def PredictMultiplier(i, words, lexicon):
    multiplier = 1.0
    NegativeModifiers = ["not","n't", "no", "nothing"]
    PositiveModifiers = ["very","so","really"]
    NeutralModifiers = ["neither","nor"]
    TooExceptionList = ["good", "awesome","brilliant","kind","great","tempting","big","overpowering","full","filled","stuffed","perfect","rare"]
    if i > 0:
        if words[i-1].lower() == "not" and words[i].lower() in lexicon:
            multiplier*=-0.5
        elif (words[i-1].lower() in NegativeModifiers or (len(words[i-1]) > 2 and words[i-1].lower().endswith("nt") and words[i-1].lower()[-3] not in ['a','e','i','o','u']) or words[i-1].lower().endswith("n't")) \
            or (i > 1 and (words[i-2].lower() in NegativeModifiers or (len(words[i-2]) > 2 and words[i-2].lower().endswith("nt") and words[i-2].lower()[-3] not in ['a','e','i','o','u']) or
                               words[i-2].lower().endswith("n't") or (words[i-1].lower() == "t" and words[i-2].lower() == "'")))or (i > 2 and words[i-2].lower() == "t" and words[i-3].lower() == "'"):
            multiplier *=-1.0
        elif words[i-1].lower() in PositiveModifiers:
            multiplier *= 2.0
        elif words[i-1].lower() in NeutralModifiers or (i > 1 and words[i-2].lower() in NeutralModifiers):
            multiplier *= 0.0
        elif words[i-1].lower() == "too" and words[i].lower() not in TooExceptionList and words[i].lower() in lexicon:
            if words[i].lower() in ["much","many"]:
                multiplier = -100.0
            elif float(lexicon[words[i].lower()]) < 0:
                multiplier *= 2.0
            else:
                multiplier *= -0.5
    return multiplier

def CalculateNotScore(notCount):
    if notCount >=10:
        notScore = 4
    elif notCount >=7:
        notScore = 2
    elif notCount >=4:
        notScore = 1
    else:
        notScore = 0
    return notScore

def DumpDetails(sentences, lexicon, notCount, label):
    AdjR = 0.0
    adjAll = []
#    if text.startswith("For more photos and reviews do check out fourleggedfoodies"):
#        x = 1
    for sentence in sentences:
        if "Adjectives" in sentence:
            if not isinstance(sentence["Adjectives"],list):
                sentence["Adjectives"] = [sentence["Adjectives"]]
            adjList = [w.lower() for w in sentence["Adjectives"] if w.lower() not in stopWords and w.lower() not in engnames]
            adjAll.extend(adjList)
            adjectives = set(adjList)
        else:
            adjectives = set()
        ExtraAdjectives = adjectives | GlobalAdjList
        AdjS = 0.0
        words = wordpunct_tokenize(sentence["Text"])
        if len(words) <=3:
            ExtraAdjectives|= set([x.lower for x in words])
        for i in range(len(words)):
            multiplier = PredictMultiplier(i, words, lexicon)
            if words[i].lower() in ExtraAdjectives and words[i].lower() in lexicon:
                score = float(lexicon[words[i].lower()])*multiplier
                if multiplier < 1:
                    colortext = colored(words[i] + " (" + '{:.3}'.format(score) + ")", 'red',None,['underline'])
                elif multiplier > 1:
                    colortext = colored(words[i] + " (" + '{:.3}'.format(score) + ")", 'red',None,['bold'])
                else:
                    colortext = colored(words[i] + " (" + '{:.3}'.format(score) + ")", 'red')
                AdjS+= score
                print colortext,
            else:
                print words[i],
        print
        colortext = colored("Adjectives: " + '{:.3}'.format(AdjS),'red')
        print colortext
        AdjR+=AdjS
    print
    notScore = CalculateNotScore(notCount)
    print "Label:", label, "Not Count:", notCount
    base = PredictBase(adjAll, lexicon)  # to change the base of the multiplier according to number of adjectives and text length
    colortext = colored("Adjectives: " + str(AdjR) + "*" + str(base) + " - " + str(notScore) + " = " + str(AdjR*base - notScore),'red')
    print colortext

def PredictSentiment(sentences, lexicon, notCount):
    AdjR = 0.0
    # if text.startswith("For more photos and reviews do check out fourleggedfoodies"):
    #     x = 1
    adjAll = []
    for sentence in sentences:
        if "Adjectives" in sentence:
            if not isinstance(sentence["Adjectives"],list):
                sentence["Adjectives"] = [sentence["Adjectives"]]
            adjList = [w.lower() for w in sentence["Adjectives"] if w.lower() not in stopWords and w.lower() not in engnames]
            adjAll.extend(adjList)
            adjectives = set(adjList)
        else:
            adjectives = set()
        ExtraAdjectives = adjectives | GlobalAdjList
        AdjS = 0.0
        words = wordpunct_tokenize(sentence["Text"])
        if len(words) <=3:
            ExtraAdjectives|= set([x.lower() for x in words])
        for i in range(len(words)):
            if words[i].lower() in ExtraAdjectives and words[i].lower() in lexicon:
                AdjS += float(lexicon[words[i].lower()])*PredictMultiplier(i,words, lexicon)
        # sentence["Label"] = classify(AdjS,0,0)
        AdjR+=AdjS
    AdjR *= PredictBase(adjAll, lexicon)
    notScore = CalculateNotScore(notCount)
    return AdjR - notScore

GlobalAdjList = {"disappointing","disappointed","fresh","freshly","tasty","delicious","poor","disappointment","badly","sadly","sucks","sucked","crispy","yelled","love","loved","loving"}
stopWords = set(stopwords.words("english"))
engnames = set(names.words())
filename = "/home/shailesh/webservice/src/classifier_v3.0/ParsedTrainingData.txt"
with open(filename,'r') as file:
    TrainingFile = file.read()
TrainingData = json.loads(TrainingFile)
filepath = "/home/shailesh/webservice/src/classifier_v3.0/SentiWordNet_Lexicon_concise.csv"
lexicon = util.LoadLexiconFromCSV(filepath)
posx, posy, negx, negy, neutx, neuty,accx,accy = 0,0,0,0,0,0,0,0
maxnegf1 = maxneutf1 = maxposf1 = maxacc = 0
for i in range(-1,0,1):
    for j in range(1, 0,-1):
        predictedOverall = []
        expectedSentiment = []
        posCount = negCount = neutCount = sadCount = TotPos = TotNeg = TotNeut =  0
        for k in range(int(len(TrainingData["ClassificationModel"]))):
            current = TrainingData["ClassificationModel"][str(k + 1)]
            notCount = current["NotCount"]
            if "Sentences" in current:
                if not isinstance(current["Sentences"],list):
                    current["Sentences"] = [current["Sentences"]]
                sentences = current["Sentences"]
            else:
                continue
            label = current["Label"]
            expectedSentiment.append(label)
            predicted = PredictSentiment(sentences, lexicon, notCount)
            predictedOverall.append(classify(predicted,j,i))
            if label == 1:
                TotPos+=1
            elif label == -1:
                TotNeg+=1
            else:
                TotNeut+=1
            # AdjList.append((label, len([l for l in list2 if lexicon.has_key(('a',l)) and math.fabs(float(lexicon[('a',l)])) > 0.1])))
            # AdjListPred.append((classify(predicted,j,i),len([l for l in list2 if lexicon.has_key(('a',l)) and math.fabs(float(lexicon[('a',l)])) > 0.1])))
#            if classify(predicted,j,i) != classify(predicted2,j,i):
#                if classify(predicted,j,i) == label:
#                    print "Predict Function 1 is correct"
#                elif classify(predicted2,j,i) == label:
#                    print "Predict Function 2 is correct"
#                else:
#                    print "Both functions are incorrect"
            if (predicted > 3.0 and label == -1) or (predicted < -3.0 and label == 1):
                DumpDetails(sentences, lexicon, notCount, label)
                print "ID", k + 1,"\n"
                sadCount+=1
        print "Sad Count:", sadCount
        #print "Minimum Not Count", limit + 1, "Pos:",'{:.2%}'.format(posCount/TotPos), "Neg:",'{:.2%}'.format(negCount/TotNeg), "Neut:",'{:.2%}'.format(neutCount/TotNeut)
#        cfist = nltk.ConditionalFreqDist(AdjList)
#        cfistPred = nltk.ConditionalFreqDist(AdjListPred)
#        print "Expected"
#        for key,value in cfist.items():
#            print key, value
#        print "Predicted"
#        for key,value in cfistPred.items():
#            print key, value
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
print "Maximum Positive F1: ",'{:.2%}'.format(maxposf1), "at", posx, posy
print "Maximum Negative F1: ",'{:.2%}'.format(maxnegf1), "at", negx, negy
print "Maximum Neutral F1: ",'{:.2%}'.format(maxneutf1), "at", neutx, neuty
cprint("Maximum Accuracy: " + '{:.2%}'.format(maxacc) + " at " + str(accx) + str(accy),'red')

#    sentences = sent_tokenize(text)
#    predictedSentences = PredictAllSentences(sentences, predictedOverall, lexicon)


