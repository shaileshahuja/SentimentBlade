__author__ = 'shailesh'

from xml.etree import ElementTree as ET
from nltk.stem.wordnet import WordNetLemmatizer
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.text import Text, TextCollection


def Lemmatize(lemmatizer, token, tag):
    """
    function to lemmatize a token using pos tags if possible
    """
    if tag[0].lower() in {'a', 'n', 'v', 'r'}:
        return lemmatizer.lemmatize(token.lower(), tag[0].lower())
    return lemmatizer.lemmatize(token.lower())


def AddInBag(bagOfWords, tokens):
    """
    function to add a tokens list in the bag of words
    if the token is not in the bag, it is added
    """
    global vocabc
    for token in tokens:
        if token not in bagOfWords:
            bagOfWords[token] = vocabc
            vocabc += 1

# use a test file with less data for faster debugging
filePath = "/home/shailesh/SentimentRazor/files/test.xml"
lemmatizer = WordNetLemmatizer()
root = ET.parse(filePath).getroot()  # parsing the xml file
texts = []
# set storing the vocabulary of the test documents
bagOfWords = {}
documents = {}
idc = 1
global vocabc
vocabc = 1
for doc in root:
    docTokens = []
    review = doc.find('review').text
    label = doc.find('polarity').text
    sentences = sent_tokenize(review)
    for sentence in sentences:
        # tokenise the sentence
        tokens = word_tokenize(sentence)
        # POS tag the sentence
        tagged_tokens = nltk.pos_tag(tokens)
        # remove punctuation tokens
        filtered_tokens = filter(lambda (word, tag): word not in '.,-', tagged_tokens)
        # lemmatize the token, using POS tags if possible
        lemmatized_tokens = [Lemmatize(lemmatizer, token, tag) + "/" + tag[0] for token, tag in filtered_tokens]
        docTokens.extend(lemmatized_tokens)
        # add in the bag of words if the tokens are new
        AddInBag(bagOfWords, lemmatized_tokens)
    documents[idc] = {'label': label, 'review': review, 'tokens': docTokens}
    idc += 1
    texts.append(Text(docTokens))
textCollection = TextCollection(texts)

# writing the vocabulary to a file
bagPath = '/home/shailesh/SentimentRazor/files/BagOfWords.txt'
with open(bagPath, 'w') as file1:
    for word in bagOfWords:
        file1.write(str(bagOfWords[word]) + ':' + word + '\n')

# use nltk TextCollection class to compute tf-idf and store the document
# as a vector in a text file
vectorPath = '/home/shailesh/SentimentRazor/files/Tf-Idf.txt'
with open(vectorPath, 'w') as file1:
    for idc in documents:
        print "ID" + str(idc)
        tfidf = []
        for token in set(documents[idc]['tokens']):
            score = textCollection.tf_idf(token, documents[idc]['tokens'])
            tfidf.append(str(bagOfWords[token]) + ':' + str(score))
            print token + " " + str(bagOfWords[token]) + ':' + str(score)
        print
        documents[idc]['tf-idf'] = ' '.join(tfidf)
        tfidf_string = documents[idc]['tf-idf']
        label = documents[idc]['label']
        file1.write("%s %s\n" % (label, tfidf_string))

