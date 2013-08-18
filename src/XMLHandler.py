__author__ = 'shailesh'

from xml.etree import ElementTree as ET
from xml.dom import minidom
from Review import Review


def Prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = ET.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")


def DumpCrawlerOutputAsXML(reviews,filePath):
    """
    Creates an XML file storing the crawled reviews
    :param reviews: the reviews crawled by YelpCrawler
    :param filePath: the path at which to create and store the XML content
    """
    root = ET.Element("document")
    for i in range(len(reviews)):
        doc = ET.SubElement(root,"doc")
        doc.set("id",str(i + 1))
        stars = ET.SubElement(doc,"stars")
        stars.text = reviews[i].stars
        url = ET.SubElement(doc,"url")
        url.text = reviews[i].url
        date = ET.SubElement(doc,"date")
        date.text = reviews[i].date
        user = ET.SubElement(doc,"user")
        user.text = reviews[i].user
        reviewtext = ET.SubElement(doc,"review")
        reviewtext.text = reviews[i].review
        useful = ET.SubElement(doc,"useful")
        useful.text = reviews[i].useful
        funny = ET.SubElement(doc,"funny")
        funny.text = reviews[i].funny
        cool = ET.SubElement(doc,"cool")
        cool.text = reviews[i].cool

    XMLstring = Prettify(root)
    with open(filePath,'w') as file1:
        file1.write(XMLstring)


def LoadCrawledXMLFile(filePath):
    """
    function to load crawled data
    better way to handle this function is to use find method,
    although find method is slower than this implementation
    """
    reviews = []
    stars, url, date, user, review, useful, funny, cool = None, None, None, None, None, None, None, None
    root = ET.parse(filePath).getroot()
    for doc in root:
        for element in doc:
            if element.tag == "stars":
                stars = element.text
            elif element.tag == "url":
                url = element.text
            elif element.tag == "date":
                date = element.text
            elif element.tag == "user":
                user = element.text
            elif element.tag == "review":
                review = element.text
            elif element.tag == "useful":
                useful = element.text
            elif element.tag == "funny":
                funny = element.text
            elif element.tag == "cool":
                cool = element.text
        reviews.append(Review(stars, url, date, user, review, useful, funny, cool))
    return reviews


def DumpSortedReviews(reviews,filePath):
    root = ET.Element("document")
    for i in range(len(reviews)):
        doc = ET.SubElement(root,"doc")
        doc.set("id",str(i + 1))
        stars = ET.SubElement(doc,"stars")
        stars.text = reviews[i].stars
        url = ET.SubElement(doc,"url")
        url.text = reviews[i].url
        date = ET.SubElement(doc,"date")
        date.text = reviews[i].date
        user = ET.SubElement(doc,"user")
        user.text = reviews[i].user
        reviewtext = ET.SubElement(doc,"review")
        reviewtext.text = reviews[i].review
        polarity = ET.SubElement(doc,"polarity")
        polarity.text = "NULL"
        confidence = ET.SubElement(doc,"confidence")
        if i < 200:
            confidence.text = str(1)
        else:
            confidence.text = str(0)

    XMLstring = Prettify(root)
    with open(filePath,'w') as file1:
        file1.write(XMLstring)

