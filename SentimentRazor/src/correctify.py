__author__ = 'shailesh'

from xml.etree import ElementTree as ET
from xml.dom import minidom


def Prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = ET.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")

filePath = "/home/shailesh/PycharmProjects/SentimentRazor/files/FinalReviewsList.xml"
root = ET.parse(filePath).getroot()
for i in range(len(root)):
    docID = root[i].attrib["id"]
    for j in range(len(root[i])):
        if root[i][j].tag == "stars":
            stars = root[i][j].text
        elif root[i][j].tag == "polarity":
            if int(docID) <=200 and root[i][j].text == "NULL":
                if float(stars) < 3.0:
                    root[i][j].text = str(-1)
                if float(stars) > 3.0:
                    root[i][j].text = str(1)
                else:
                    print "ERROR MISSED DOCID:", docID

# XMLstring = Prettify(root)
XMLstring = ET.tostring(root, 'utf-8')
with open(filePath, 'w') as file1:
    file1.write(XMLstring)