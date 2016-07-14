import json
import sys
import heapq
from datetime import datetime

class Graph:
    def __init__(self):
        self.latest = None
        self.edges = [] #heap of edges

    def reject(self, timestamp):
        ##print "Reject ", self.latest, timestamp
        if timestamp >= self.latest:
            return False
        if timestamp < self.latest:
            delta =  self.latest - timestamp
            return delta.days > 0 or delta.seconds > 60 
        #print "Rejecting ", timestamp
        return True

    def update_edges(self, txn):
        found = False
        inp_set = set([txn['actor'], txn['target']])
        new_edges = []
        for e in self.edges:
            cur_set = set([e['actor'], e['target']])
            if cur_set == inp_set:
                found = True
                # if this edge exists - update the time
                if txn['created_time'] > e['created_time']:
                    e['created_time'] = txn['created_time']
            if not self.reject(e['created_time']):
                #ignore_old_edges
                new_edges.append(e)
                
        if not found:
            new_edges.append(txn)
        self.edges = new_edges

    def compute_median(self):
        degrees = {}
        for e in self.edges:
            for name in [e['actor'], e['target']]:
                if name in degrees.keys():
                    degrees[name] = degrees[name] + 1
                else: 
                    degrees[name] = 1

        #print "Degrees: ", degrees
        degrees_list = degrees.values()
        #print "Degrees_list: ", degrees_list
        middle = len(degrees_list)/2
        degrees_list = sorted(degrees_list)
        if len(degrees_list) % 2 == 0 and middle != 0:
            return (degrees_list[middle] + degrees_list[middle-1])/2.
        else:
            return degrees_list[middle]
                    
    def process(self, txn):
        if self.latest == None or self.latest < txn['created_time']:
            self.latest = txn['created_time']
        #print "Latest: ", self.latest
        self.update_edges(txn)
        #print self.edges
        return self.compute_median()
            

if(len(sys.argv) != 3):
    #print "Usage: sliding_median.py <inpfile> <outfile>"
    sys.exit(0)

try:
    txns = open(sys.argv[1])
    out = open(sys.argv[2], 'w')
except IOError as e:
    #print "I/O error({0}): {1}".format(e.errno, e.strerror)
    sys.exit(0)

g = Graph()
date_fmt = '%Y-%m-%dT%H:%M:%SZ'
for t in txns:
    #print "======================================================================================"
    txn = None
    set_fields = set(['created_time', 'actor', 'target'])
    try:
        txn = json.loads(t)
        if set_fields == set(txn.keys()) and txn['created_time'] and txn['actor'] and txn['target']:
            #print "Created_time: ", txn['created_time']
            txn['created_time'] = datetime.strptime(txn['created_time'], date_fmt)
            print >> out, ('%.3f' % g.process(txn))[:-1]
    except:
        continue

