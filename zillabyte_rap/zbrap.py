import zillabyte
#rgenius.py is the module that houses the two functions above
from rgenius import *
import csv


def getsongs(controller, tup):
  #receives the name of an artist and builds genius.com url to find artist
  artist = tup["artist"]
  artistUrl = "http://genius.com/artists/" + artist

  #make request to genius.com to get list of urls for an artist
  songs = getMostArtistSongs(artistUrl)

  #emit each song separately
  for song in songs:
    #print song
    controller.emit({"song" : song, "artist" : artist})
  return


def buildGraph(controller, tup):
  #extract song url and artist name  
  song = tup["song"]

  #artist name used only for debugging purposes
  artist = tup["artist"]
  #print song, artist

  #make request to rap.genius.com to get and emit artist, feature, and producer info
  songData = setSong(song)
  controller.emit({"song" : song, "artist": songData[0], "featuredArtists": songData[1], "producers": songData[2]})


def nt(controller):
  #function to handle custom source from my seed list of artists
  with open("rapperlist.csv") as rl:
    for line in rl:
      controller.emit({"artist" : line})
  controller.end_cycle()



#initialize app, use custom source and two Each steps with previously defined functions, and a sink
app = zillabyte.app(name = "pygenius")
app.source(name="raplist", next_tuple = nt, end_cycle_policy="explicit")\
   .each(execute = getsongs)\
   .each(execute = buildGraph)\
   .sink(name = "rapsink", columns = [{"song":"string"}, {"artist":"string"}, {"featuredArtists":"array"}, {"producers":"array"}])
