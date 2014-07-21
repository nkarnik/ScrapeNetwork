import csv
import Queue
import threading
import requests
from rapgenius import *

threads = []
rappers = []
result1, result2, result3, result4 = [], [], [], []

with open('raplist.csv', 'rb') as file:
    reader = csv.reader(file)
    for row in reader:
        rappers.append(row[0])

r1 = rappers[0:250]
r2 = rappers[250:500]
r3 = rappers[500:800]
r4 = rappers[800:]

q1 = Queue.Queue()
q2 = Queue.Queue()
q3 = Queue.Queue()
q4 = Queue.Queue()

for rapper in r1:
    q1.put(rapper)

for rapper in r2:
    q2.put(rapper)

for rapper in r3:
    q3.put(rapper)

for rapper in r4:
    q4.put(rapper)


#define a worker function
def worker(queue):
    queue_full = True
    while queue_full:
        try:
            #get your data off the queue, and do some work
            item = queue.get(False)
            try:
                r = searchArtist(item)[0]
                if r is None:
                    pass
                else:
                    songs = getAllArtistSongs(r.url)
                    if songs is None:
                        pass
                    else:
                        print (str(r), songs, len(result1))
                        if len(result1) < 280:
                            result1.append((r,songs))
                            print "result1 is" + len(result1)
                        elif len(result2) < 280:
                            result2.append((r,songs))
                            print "result2 is" + len(result2)
                        elif len(result3) < 280:
                            result3.append((r,songs))
                            print "result3 is" + len(result3)
                        else:
                            result4.append((r,songs))
                            print "result4 is" + len(result4)
                        del item
                        del r
                        del songs
            except:
                pass

        except Queue.Empty:
            queue_full = False

#create as many threads as you want
thread_count = 10
def test(q):
    for i in range(thread_count):
        t = threading.Thread(target=worker, args = (q,))
        threads.append(t)
        t.start()

def end(q):
    if q.empty():
        for t in threads:
            t.exit()
        threads = []
        

