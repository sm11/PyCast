import urllib
import json
import re
import os
import sys
from xml.dom import minidom
from xml.etree import ElementTree as etree

# progress bar functions
def _reporthook(numblocks, blocksize, filesize, url=None):
    try:
        percent = min((numblocks*blocksize*100)/filesize, 100)
    except:
        percent = 100
    if numblocks != 0:
        bar = '#' * (percent/5) + '-' * (20-percent/5)
        print('\r[%s] %s%s   ' % (bar, percent, '%')),
        sys.stdout.flush()

def geturl(url, dst):
        urllib.urlretrieve(url, dst,
                           lambda nb, bs, fs, url=url: _reporthook(nb,bs,fs,url))


def main():
    correctGrab = False

    # correctly get the user's podcast
    while not correctGrab:

        podcastSearch = raw_input("Podcast you want to listen to: ")
        podcastSearch = re.sub(r" ", "+", podcastSearch)

        # grab podcast info
        url = "https://itunes.apple.com/search?term=" + podcastSearch + "&entity=podcast"
        response = urllib.urlopen(url)
        data = json.loads(response.read())

        podcastName = data["results"][0]["trackName"]
        podcastId = data["results"][0]["collectionId"]

        print ("Podcast: " + podcastName)
        userCheck = raw_input("Continue? (y/n) ")

        if userCheck == 'Y' or userCheck == 'y' :
            break

    # grab podcast feed
    url = "https://itunes.apple.com/lookup?id=" + str(podcastId) + "&entity=podcast"
    response = urllib.urlopen(url)
    data = json.loads(response.read())

    rss = data["results"][0]["feedUrl"]

    # grab all podcast .mp3 files
    url_str = rss
    xml_str = urllib.urlopen(url_str).read()
    xmldoc = minidom.parseString(xml_str)

    values = xmldoc.getElementsByTagName('enclosure')
    titles = xmldoc.getElementsByTagName('title')

    # append the title list such that the correct title is corresponding to the
    # equivlanet .mp3 link
    nameChecker = True
    counter = 0
    while nameChecker:
        if podcastName == titles[counter].firstChild.nodeValue:
            counter = counter + 1
        else:
            nameChecker = False

    titles = titles[counter:]

    # insert mp3 list into mp3list array
    mp3list = []
    for val in values:
        mp3list.append(val.attributes['url'].value)

    # get how the user wants to download the files
    userDownload = raw_input('Which file(s) to download? ')

    downloadAll = False
    downloadOne = 0
    downloadNew = False;
    downloadRangeStart = 0
    downloadRangeFinish = 0
    badInput = False

    if userDownload == "All" or userDownload == "all":
        downloadAll = True
    elif userDownload.isdigit() > 0:
        downloadOne = len(mp3list) - int(userDownload)
    elif 'to' in userDownload or '-' in userDownload:
        if('to' in userDownload ):
            rangeList = re.split('to', userDownload)
        else:
            rangeList = re.split('-', userDownload)
        if downloadRangeStart < 1 or downloadRangeFinish < 1:
            print ("Error: bad input")
            badInput = True
        downloadRangeStart = len(mp3list) - int(rangeList[1])
        downloadRangeFinish = len(mp3list) - int(rangeList[0])
        if downloadRangeStart > downloadRangeFinish:
            print ("Error: bad input")
            badInput = True
    elif userDownload == "latest" or userDownload == "new" or userDownload == "New":
        downloadNew = True
    else:
        print ("Error: bad input")
        badInput = True

    if badInput == True:
        sys.exit()

    if downloadAll:
        for i in range(len(mp3list)):
            print("Downloading: " + str(titles[i].firstChild.nodeValue))
            saveLoc = os.path.dirname(os.path.realpath(__file__)) + "/" + titles[i].firstChild.nodeValue + ".mp3"
            geturl(mp3list[i], saveLoc)
            print("\n")

    if downloadOne > 0:
        print("Downloading: " + str(titles[int(downloadOne)].firstChild.nodeValue))
        saveLoc = os.path.dirname(os.path.realpath(__file__)) + "/" + titles[int(downloadOne)].firstChild.nodeValue + ".mp3"
        geturl(mp3list[int(downloadOne)], saveLoc)

    if downloadRangeStart > 0 and downloadRangeFinish > 0:
        for i in range(downloadRangeStart, downloadRangeFinish + 1):
            print("Downloading: " + str(titles[i].firstChild.nodeValue))
            saveLoc = os.path.dirname(os.path.realpath(__file__)) + "/" + titles[i].firstChild.nodeValue + ".mp3"
            geturl(mp3list[i], saveLoc)
            print("\n")

    if downloadNew:
        print("Downloading: " + str(titles[0].firstChild.nodeValue))
        saveLoc = os.path.dirname(os.path.realpath(__file__)) + "/" + titles[0].firstChild.nodeValue + ".mp3"
        geturl(mp3list[int(downloadOne)], saveLoc)

if __name__ == '__main__':
    main()