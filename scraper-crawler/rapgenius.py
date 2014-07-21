#
# Nikhil Karnik
# rapgenius.py
# API for scraping data from RapGenius
#


RAPGENIUS_URL = 'http://rapgenius.com'
RAPGENIUS_SEARCH_URL = 'http://rapgenius.com/search'
RAPGENIUS_ARTIST_URL = 'http://rapgenius.com/artists'

from bs4 import BeautifulSoup
#from BeautifulSoup import BeautifulSoup
import urllib2
import requests
import re
from urlparse import parse_qs, urlsplit


class artist:

    def __init__(self, name, url):
        self.name = name
        self.url = url

        self.popularSongs = [] #array of 'popular songs' from artist's page. Initially empty.
        self.songs = [] #array of songs on artist page that are not listed as 'popular songs.' Initially empty.

    def __str__(self):
        return self.name + ' - ' + self.url

    #instantiates object's popular song array and returns it
    def getPopularSongs(self):
        self.popularSongs = getArtistPopularSongs(self.url)
        return self.popularSongs


    #this pretty slow right now
    def getAllSongs(self):
        self.songs = getArtistSongs(self.url)



class song:

    def __init__(self, name, url):
        self.name = name
        self.url = url
        self.artist = None
        self.featuredArtists = []
        self.producers = []
        self.year = 0
        self.rawLyrics = ""
    
    def set_year(self):
        self.year, self.rawLyrics = getYear(self.url)
    
    def set(self):
        self.artist, self.featuredArtists, self.producers = setSong(self.url)
    
    def set_artist(self):
        self.artist = getSongArtist(self.url)

    def set_features(self):
        self.featuredArtists = getSongFeaturedArtists(self.url)

    def set_producers(self):
        self.producers = getSongProducers(self.url)


    def __str__(self):
        return self.name + ' - ' + self.url

    def getRawLyrics(self):
        self.rawLyrics = getLyricsFromUrl(self.url)
        return self.rawLyrics

#Searches for 'artistName', returns list of matches
#returns list of artist objects
def searchArtist(artistName):
    searchUrl = RAPGENIUS_SEARCH_URL+'?q='+searchUrlFormat(artistName)
    soup = BeautifulSoup(urllib2.urlopen(searchUrl).read())
    results = []
    artistRe = re.compile('/artists/.')

    #if exact artist name is entered, rapgenius redirects to artist page
    try:
        if re.match('/artists/[0-9]*/follows', soup.find('a', href=artistRe).get('href')):
            #TODO - get actual artist name from artist url (to ensure proper capitalization, etc)
            results.append(artist(artistName, getArtistUrl(artistName)))
    except:
        pass

    try:
        for row in soup.find_all('a', href=artistRe):
            #print ''.join(row.findAll(text=True)) + RAPGENIUS_URL+row.get('href')
            results.append(artist(''.join(row.findAll(text=True)), RAPGENIUS_URL+row.get('href')))
    
    except:
        pass

    return results

def getArtistUrl(artistName):
    return RAPGENIUS_ARTIST_URL+"/" + artistName.replace(" ","-")#TODO - figure out other character replacements

#converts search query into something that can be put into search URL 
def searchUrlFormat(query):
    return query.replace(' ','+')#TODO check other cases

#returns array song objects
#TODO - same problem I had with getting all artist songs. With the urlopen request,
#		the results are paginated, and this currently only returns the first page
#		of results. Fix this + add depth/number of results feature eventually
def searchSong(songName):
    searchUrl = RAPGENIUS_SEARCH_URL+'?q='+searchUrlFormat(songName)
    soup = BeautifulSoup(urllib2.urlopen(searchUrl).read())
    songs = []
    for row in soup.find_all('a', class_='song_link'): #force to ignore 'hot song' results
        if(row.parent.get('class')!=None):
            songs.append(song(''.join(row.findAll(text=True)).strip(), RAPGENIUS_URL+row.get('href')))
    #TODO - object model

    #print songs
    return songs

#returns string of (unannotated) lyrics, given a url
def getLyricsFromUrl(url):
    #TODO - exeptions
    soup = BeautifulSoup(urllib2.urlopen(url).read())
    ret = ""
    for row in soup('div', {'class':'lyrics'}):
        text = ''.join(row.findAll(text=True))
        data = text.strip() +'\n'
        ret += data
    return data

def getYear(url):
    soup = BeautifulSoup(requests.get(url).text)
    ret = ""
    for row in soup('div', {'class':'lyrics'}):
        text = ''.join(row.findAll(text=True))
        data = text.strip() +'\n'
        ret += data
    
    try:
        s1 = soup('div', {'class':'album_title_and_track_number'})
        part = s1[0].findAll('a')[0]['href']
        fin = BeautifulSoup(requests.get('http://rapgenius.com'+part).text)
        s2 = fin('h1', {'class':'name'})
        s3 = s2[0].contents[-1]
        #print s3
        index = s3.rfind(') L')
        year = s3[index-4:index]
        try:
            year = int(year)
            return year, data
        except:
            return 0, data
    except:
        return 0, data
    

def getArtistPopularSongs(url):
    soup = BeautifulSoup(urllib2.urlopen(url).read())
    songs = []
    for row in soup.find('ul', class_='song_list'):
        if(type(row.find('span'))!=int):
            songs.append(song(''.join(row.find('span').findAll(text=True)).strip(), RAPGENIUS_URL+row.find('a').get('href')))

    return songs

def getAllArtistSongs(url):
    soup = BeautifulSoup(requests.get(url).text)
    songs = []
    for row in soup.find('ul', class_='song_list').findNextSibling('ul'):
        try:
            songs.append( song(''.join(row.find('span').findAll(text=True)).strip(), RAPGENIUS_URL+row.find('a').get('href') ))
            continue
        except:
            #Do nothing, cheap hack
            #TODO - see if there is a better way to do this
            pass
    #we currently have the first 'page' of song results
    #Now, we have to load the rest and add it to the list
    #Possible future feature: choosing depth (number of pages) or number of songs to load, rather than forcing everything
    #No proper error-checking yet, so this probably breaks for some artists
    for r in soup('div', {'class':'pagination'}):
        links = r.findAll('a')
        #print links[-2].string
        try:
            last = int(links[-2].string)
            print last
            for i in xrange(last):
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
                for pageRow in page.find('ul', class_='song_list'):
                    if(type(pageRow.find('span'))!=int):
                        #print ''.join(pageRow.find('span').findAll(text=True)).strip()
                        songs.append(song(''.join(pageRow.find('span').findAll(text=True)).strip(), RAPGENIUS_URL+pageRow.find('a').get('href')))
        except:
            continue
    return songs
    
    
def getArtistSongs(url):
    soup = BeautifulSoup(urllib2.urlopen(url).read())
    songs = []
    for row in soup.find('ul', class_='song_list').findNextSibling('ul'):
        try:
            songs.append( song(''.join(row.find('span').findAll(text=True)).strip(), RAPGENIUS_URL+row.find('a').get('href') ))
        except:
            #Do nothing, cheap hack
            #TODO - see if there is a better way to do this
            pass
    #we currently have the first 'page' of song results
    #Now, we have to load the rest and add it to the list
    #Possible future feature: choosing depth (number of pages) or number of songs to load, rather than forcing everything
    #No proper error-checking yet, so this probably breaks for some artists
    for r in soup('div', {'class':'pagination'}):
        for row in r.findAll('a'): #TODO - see if I can make this prettier
            #print row.get('href')
            #print url+row.get('href')
            nextPage = BeautifulSoup(urllib2.urlopen(RAPGENIUS_URL+row.get('href')).read())
            for pageRow in nextPage.find('ul', class_='song_list'):
                if(type(pageRow.find('span'))!=int):
                    #print ''.join(pageRow.find('span').findAll(text=True)).strip()
                    songs.append(song(''.join(pageRow.find('span').findAll(text=True)).strip(), RAPGENIUS_URL+pageRow.find('a').get('href')))

    return songs

def setSong(url):
    soup = BeautifulSoup(requests.get(url).text)
    featured = []
    producers = []
    for row in soup.find('h1', class_= 'song_title'):
        try:

            aName = ''.join(row.findAll(text=True))
            aURL = row.get('href')
        except:
            pass 
            
    for r in soup('div', {'class':'featured_artists'}):
        for row in r.find_all('a'):
            featured.append(artist(''.join(row.findAll(text=True)), RAPGENIUS_URL+row.get('href')))        
    
    for r in soup('div', {'class':'producer_artists'}):
        for row in r.find_all('a'):
            producers.append(artist(''.join(row.findAll(text=True)), RAPGENIUS_URL+row.get('href')))
    
    return (artist(aName, RAPGENIUS_URL+aURL), featured, producers)
    
def getSongArtist(url):
    soup = BeautifulSoup(urllib2.urlopen(url).read())
    for row in soup.find('h1', class_= 'song_title'):
        try:

            aName = ''.join(row.findAll(text=True))
            aURL = row.get('href')
        except:
            pass 
    return artist(aName, RAPGENIUS_URL+aURL)

def getSongFeaturedArtists(url):
    artists = []
    soup = BeautifulSoup(urllib2.urlopen(url).read())
    for r in soup('div', {'class':'featured_artists'}):
        for row in r.find_all('a'):
            artists.append(artist(''.join(row.findAll(text=True)), RAPGENIUS_URL+row.get('href')))
    return artists

def getSongProducers(url):
    artists = []
    soup = BeautifulSoup(urllib2.urlopen(url).read())
    for r in soup('div', {'class':'producer_artists'}):
        for row in r.find_all('a'):
            artists.append(artist(''.join(row.findAll(text=True)), RAPGENIUS_URL+row.get('href')))
    return artists

def test_rap(rappers):
    indices = []
    for rapper in rappers:
        try:
            r = searchArtist(rapper)[0]
        except:
            continue
        
        indices.append(getAllArtistSongs(r.url))

def test():
    outkast = searchArtist("Outkast")[0]
    #print outkast.name
    #print outkast.url
    #outkast.getPopularSongs()
    #for song in outkast.popularSongs:
    #	print song.getRawLyrics()
    outkast.getAllSongs()
    for song in outkast.songs:
        print song.__str__()


