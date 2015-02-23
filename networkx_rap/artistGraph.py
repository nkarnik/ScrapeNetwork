"""
This script is for taking a pickled list of songs (with nested metadata) and 
transforming it into a proper networkx graph.

Author: Nikhil Karnik
"""

import sys
import networkx as nx
import numpy as np
import pickle
import matplotlib
import itertools

import matplotlib.pyplot as plt

def artistGraph(songs):
    """
    Create graph with all songs in pickled file
    """
    graph = nx.Graph()
    for song in songs:
        #Add artists and producers as nodes
        artist = str(song.artist.name.encode('utf-8','xmlcharrefreplace'))
        producers = [str(p.name.encode('utf-8','xmlcharrefreplace')) for p in song.producers]
        try:
            graph.node[artist]
            graph.node[artist]['songs'] += 1
 
        except KeyError:
            graph.add_node(artist, songs = 1, features = 0, productions = 0)
            
        #Add Producers
        for p in producers:
            try:
                graph.node[p]
                graph.node[p]['productions'] += 1
                
            except KeyError:
                graph.add_node(p, songs = 0, features = 0, productions = 1)
            
    
    for song in songs:
        #make connections (Edges) for each song
        artist = str(song.artist.name.encode('utf-8','xmlcharrefreplace'))
        features = [str(f.name.encode('utf-8','xmlcharrefreplace')) for f in song.featuredArtists]
        producers = [str(p.name.encode('utf-8','xmlcharrefreplace')) for p in song.producers]
        
        for f in features:
        #Ignore artists that only have featured credits
            try:
                graph.node[f]
                graph.node[f]['features'] += 1
                
                try:
                    e = graph.edge[artist][f]
                    e['weight'] += 1
                    e['difference'] = 1/float(e['weight'])
                    
                except KeyError:
                    graph.add_edge(artist, f, weight=1, difference=1)
            
            except KeyError:
                pass
        
        for p in producers:
        #Make connections for production credits
            if artist == p:
                continue
                
            try:
                e = graph.edge[artist][p]
                e['weight'] += 1
                e['difference'] = 1/float(e['weight'])
                    
            except KeyError:
                graph.add_edge(artist, p, weight=1, difference=1)
                

    return graph
    
def subGraph(songs):
    """
    Copies code and functionality of artistGraph (unnecessarily, but alas...)
    but limits to artists with > 90 songs and producers with > 50 songs.
    These numbers are pretty arbitrary and were selected for the purpose of
    limiting the number of nodes and edges to something visually managable
    """

    #First add nodes, then add combinations of edges.
    graph = nx.Graph()
    for song in songs:
        #Add artists and producers as nodes
        artist = str(song.artist.name.encode('utf-8','xmlcharrefreplace'))
        producers = [str(p.name.encode('utf-8','xmlcharrefreplace')) for p in song.producers]
        try:
            graph.node[artist]
            graph.node[artist]['songs'] += 1
 
        except KeyError:
            graph.add_node(artist, songs = 1, features = 0, productions = 0)
            
        #Add Producers
        for p in producers:
            try:
                graph.node[p]
                graph.node[p]['productions'] += 1
                
            except KeyError:
                graph.add_node(p, songs = 0, features = 0, productions = 1)
                
                
    #Select only artists with more than 90 songs or producers with more than 50 songs
    best = [n for n in graph.nodes_iter(data=True) if (n[1]['songs'] > 150 or n[1]['productions'] > 90)]        
    graph = nx.Graph()
    graph.add_nodes_from(best)
    
    for song in songs:
        #make connections (Edges) for each song
        artist = str(song.artist.name.encode('utf-8','xmlcharrefreplace'))
        features = [str(f.name.encode('utf-8','xmlcharrefreplace')) for f in song.featuredArtists]
        producers = [str(p.name.encode('utf-8','xmlcharrefreplace')) for p in song.producers]
        
        try:
        #make connections between combinations of featured artists
            fcombs = itertools.combinations(features, 2)
            for f in fcombs:
                try:
                    graph.node[f[0]]
                    graph.node[f[1]]
                    try:
                        e = graph.edge[f[0]][f[1]]
                        e['weight'] += 1
                        e['difference'] = 1/float(e['weight'])
                    
                    except KeyError:
                        graph.add_edge(f[0], f[1], weight=1, difference=1)
                    
                except KeyError:
                    continue
            
        except:
            pass
        
        try:
            graph.node[artist]
            
        except KeyError:
            continue
                           
        for f in features:
        #Add and increment featured artists edges
            try:
                graph.node[f]
                graph.node[f]['features'] += 1
                
                try:
                    e = graph.edge[artist][f]
                    e['weight'] += 1
                    e['difference'] = 1/float(e['weight'])
                    
                except KeyError:
                    graph.add_edge(artist, f, weight=1, difference=1)
            
            #Ignore artists that only have featured credits
            except KeyError:
                pass
        
        for p in producers:
        #Make connections for production credits
            try:
                graph.node[p]
                
            except KeyError:
                continue
                
            if artist == p:
                continue
                
            try:
                e = graph.edge[artist][p]
                e['weight'] += 1
                e['difference'] = 1/float(e['weight'])
                    
            except KeyError:
                graph.add_edge(artist, p, weight=1, difference=1)
                
              
        for p in producers:
        #Make connections for producers and featured artists
            try:
                graph.node[p]
                
            except KeyError:
                continue
                
            for f in features:
                try:
                    graph.node[f]
                    
                except KeyError:
                    continue
                    
                if f == p:
                    continue
                
                try:
                    e = graph.edge[f][p]
                    e['weight'] += 1
                    e['difference'] = 1/float(e['weight'])
                    
                except KeyError:
                    graph.add_edge(f, p, weight=1, difference=1)
        
    return graph   
    
    
def plotGraph(g,filename):
    """
    Creates a plot of the graph passed in after transforming
    the full graph into a minimum spanning tree. The MST of a graph
    like this has some significance (but also some locally strange paths)
    and is nice to look add due to the reduced edge density.
    """

    plt.figure(figsize=(15, 10))
    np.random.seed(5)
    mst = nx.minimum_spanning_tree(g, weight='difference')
    pos = nx.spring_layout(mst, iterations=900, k=.008, weight='difference')

    mst_edges = list(nx.minimum_spanning_edges(g, weight='difference'))
    degs = mst.degree()
    nodesize = [degs[v]*80 for v in mst]

    nl = mst.nodes()

    nx.draw_networkx_edges(g, pos, edgelist=mst_edges, alpha=.2)
    nx.draw_networkx_nodes(g, pos, nodelist = nl, node_size=nodesize, node_color=nodesize)

        
    nx.draw_networkx_labels(g, pos, font_color='k', font_size=7)

    plt.title("Artist Network", fontsize=18)
    plt.xticks([])
    plt.yticks([])
    plt.savefig(filename)

class artist:

    def __init__(self, name, url):
        self.name = name
        self.url = url


class song:

    def __init__(self, name, url):
        self.name = name
        self.url = url
        self.artist = None
        self.featuredArtists = []
        self.producers = []
        self.year = 0
        self.lyrics = ""

if __name__ == "__main__":
 
  #Set input and output files and load input file
  inputPickleFile = sys.argv[1]
  outputGraphPNG = sys.argv[2]
  songs = pickle.load(open(inputPickleFile))

  #generate graph and output plotted PNG output
  rapGraph = subGraph(songs)
  plotGraph(rapGraph,outputGraphPNG) 
