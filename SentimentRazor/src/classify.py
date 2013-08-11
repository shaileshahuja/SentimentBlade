__author__ = 'shailesh'

from LexiconClassifier import LexiconClassifier
from Utils import UtilMethods as util
from xml.etree import ElementTree as ET
import numpy as np
from sklearn.svm import LinearSVC
from sklearn.feature_extraction.text import TfidfVectorizer


def Train(clr, root, vectorizer):
    """
    method to train the SVM classifier on the human labelled data
    """
    X = []
    Y = []
    for doc in root:
        confidence = doc.find('confidence').text
        if confidence != '1':  # consider only human labelled data
            continue
        review = ''
        label = int(doc.find('polarity').text)
        XMLsentences = doc.findall('sentence')
        # repeat the first sentence twice - upweighting
        XMLsentences = [XMLsentences[0]] * 2 + XMLsentences[1:]
        for XMLsentence in XMLsentences:
            review += XMLsentence.find('text').text
        X.append(review)
        Y.append(label)
    y_train = np.asarray(Y)
    print "Extracting features from the training dataset using a sparse vectorizer"

    X_train = vectorizer.fit_transform(X)
    print "n_samples: %d, n_features: %d" % X_train.shape
    print
    clr.fit(X_train, y_train)


filePath = "/home/shailesh/SentimentRazor/files/ParsedReviewList.xml"
fileType = 'xml'
lexiconPath = "/home/shailesh/SentimentRazor/files/SentiWordNet_Lexicon_concise.csv"
print "Loading data..."
tree = ET.parse(filePath)
root = tree.getroot()
print "Data Loaded."
# creating an instance of lexicon classifier
lexClr = LexiconClassifier()
# creating an instance of SVM classifier
SVMclr = LinearSVC(loss='l2', penalty='l2', dual=True, tol=1e-3, C=0.1, class_weight={-1: 50, 0: 30, 1: 1})
# vectorizer
vectorizer = TfidfVectorizer(sublinear_tf=True, max_df=0.5,
                             stop_words='english',
                             token_pattern=ur"(?u)\b\w\w+\b")  # add \/\w to include pos tags
Train(SVMclr, root, vectorizer)
iterator = iter(root)
lexicon = util.LoadLexiconFromCSV(lexiconPath)
# iterate till the all documents have been classified
while True:
    try:
        doc = next(iterator)
        confidence = doc.find('confidence').text
        # only classify those reviews which haven't been human labelled
        if confidence == '1':
            continue
        sentences = []
        docId = doc.get('id')
        review = doc.find('review').text
        label = doc.find('polarity').text
        XMLsentences = doc.findall('sentence')
        for XMLsentence in XMLsentences:
            sentence = dict()
            for data in XMLsentence:
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
        if not sentences:
            continue
        review = sentences[0]["Text"]
        for sentence in sentences:
            review += sentence["Text"]
        # prediction score using lexicon based classifier
        predicted = lexClr.PredictSentiment(sentences, lexicon, 0)
        lexLabel = lexClr.classify(predicted, 1, 1)
        lexConfidence = lexClr.confidence(predicted)
        # transform the document into tfidf vector
        X = vectorizer.transform([review])[0]
        # prediction results using SVM classifier
        SVMLabel = SVMclr.predict(X)[0]
        SVMConfidence = max(SVMclr.decision_function(X)[0])
        if lexConfidence > SVMConfidence:  # choose the label from classifier with higher confidence
            doc.find('polarity').text = str(lexLabel)
            doc.find('confidence').text = str(lexConfidence)
            print "Used LexiconClassifier"
        else:
            doc.find('polarity').text = str(SVMLabel)
            doc.find('confidence').text = str(SVMConfidence)
            print "Used SVM classifier"
    except StopIteration:
        break

# write the output to a XML file
filePath = "/home/shailesh/SentimentRazor/files/FinalReviewsList.xml"
for doc in root:
    for sentence in doc.findall('sentence'):
        doc.remove(sentence)
    doc.remove(doc.find('notCount'))
print "Writing cleaned and classfied output to " + filePath + "..."
tree.write(filePath)
