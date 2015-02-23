"""
Nikhil Karnik
rapgenius.py
API for scraping data from RapGenius
"""


RAPGENIUS_URL = 'http://rap.genius.com'
RAPGENIUS_SEARCH_URL = 'http://genius.com/search'
RAPGENIUS_ARTIST_URL = 'http://genius.com/artists'

from bs4 import BeautifulSoup
import requests
from urlparse import parse_qs, urlsplit


def getMostArtistSongs(url):
   """
   Input url is the link to the artist's homepage on RapGenius
   Output is a list of urls to each individual song (this requires paginating through the js)
   """

    soup = BeautifulSoup(requests.get(url).text)
    songs = []
    for row in soup.findAll('ul', class_='song_list primary_list '):
      try:
          songs.append(row.find('a').get('href'))
          continue
      except:
          print "couldnt find songs"
    
    for r in soup('div', {'class':'pagination'}):
        links = r.findAll('a')
        try:
            last = int(links[-2].string)
            for i in xrange(last):
              i += 2
              print i
  
              i += 2
              print i
              upart = links[-2].get('href')
              nurl = RAPGENIUS_URL + upart
              print nurl
              scheme, netloc, path, query_string, fragment = urlsplit(nurl)
              query_params = parse_qs(query_string)
              query_params['page'] = [str(i)]
              r = requests.get(RAPGENIUS_URL + path, params=query_params)
              r = r.text
              page = BeautifulSoup(r)
              for pageRow in page.find('ul', class_='song_list primary_list '):
                  if(type(pageRow.find('span'))!=int):
                      songs.append(pageRow.find('a').get('href'))

        except Exception as e:
            print e.message

    return songs


def setSong(url):
    """
    This function takes a song url as input and outputs
    all of the metadata of that song by scraping the RapGenius
    html formatting.
    """
    soup = BeautifulSoup(requests.get(url).text)
    featured = []
    producers = []
    aName = ''
    try:
        art =  soup.find('span', class_= 'text_artist')
        aName = art.contents[1].text
        print aName
    except:
        pass

    try:
      features = soup.find('span', class_='featured_artists').contents      
      for f in features:
          try:
              featured.append(f.text)
          except:
              pass
    except:
      pass

    try:
      features = soup.find('span', class_='producer_artists').contents      
      for f in features:
          try:
              producers.append(f.text)
          except:
              pass
    except:
      pass
   
    return (aName, featured, producers)
    
