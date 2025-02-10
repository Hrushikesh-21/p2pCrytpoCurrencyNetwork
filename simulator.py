from queue import PriorityQueue
import numpy as np
import sys
from graph import *
from copy import deepcopy
from peer import *
from block import *
from transaction import *
from event import *
from Histogram import *

class Simulate():
    def __init__(self, numPeers, slowPerc, lowCpuPerc, txnDelayMeanTime, maxSimTime, maxBlockSize , maxTransactionSize, miningFee):
        self.numPeers = numPeers
        self.slowPerc = slowPerc
        self.lowCpuPerc = lowCpuPerc
        self.txnDelayMeanTime = txnDelayMeanTime
        self.maxSimTime = maxSimTime
        self.maxBlockSize = maxBlockSize
        self.maxTransactionSize = maxTransactionSize
        self.miningFee = miningFee
        self.events = PriorityQueue()
        self.c = [[]*numPeers]
        self.trxn_id = 1
        self.blk_id = 1

        # Hash Power
        self.avgInterArrivalTime = 10000*1000
        self.lowHashPow = (100 / (1000 - 9*self.lowCpuPerc))/numPeers
        self.highHashPow = 10*self.lowHashPow

        # rho_ij in ms, c_ij in bits/ms
        self.rho = np.random.uniform(10, 500, (self.numPeers, self.numPeers))
        self.c = [[]*self.numPeers]
        self.peers = []
        self.Genisis = None
        self.bins = [0]*(self.numPeers)

    def run(self):
        slows_mask = np.random.permutation([True] * int(self.numPeers * self.slowPerc/100) + [False] * (self.numPeers - int(self.numPeers * self.slowPerc/100)))
        lows_mask = np.random.permutation([True] * int(self.numPeers * self.lowCpuPerc/100) + [False] * (self.numPeers - int(self.numPeers * self.lowCpuPerc/100)))
        peers = []
        for i in range(self.numPeers):
            peers.append(Peer(i, slows_mask[i], lows_mask[i]))
        
        CreateNetwork(peers)

        debug(peers)

        self.peers = peers
        self.c = [[5 if peers[i].isSlow or peers[j].isSlow else 100 for j in range(self.numPeers)] for i in range(self.numPeers)] * (1000)

        # Initializing Transaction ids and block ids
        self.Genesis = Block(self.blk_id, None, -1, 0, None, [0]*self.numPeers, 0)
        self.blk_id += 1
        # firstTask = Event(0, 'recBlock', 0, self, None, self.Genesis)

        for i in range(self.numPeers):
            self.peers[i].tree.add_block(self.Genesis,0)
            self.peers[i].longestBlk = self.Genesis
            T_k = np.random.exponential(self.avgInterArrivalTime / (self.lowHashPow if self.peers[i].isLowCPU else self.highHashPow))
            newTask = Event(T_k, 'genBlock', i, self, None, self.Genesis)
            self.events.put(newTask)
            self.events.put(Event(0, 'genTransaction', i, self, None, None))

        while (not self.events.empty()) and self.events.queue[0].time <= self.maxSimTime:
            event = self.events.get()
            print(event.event_type, event.peer_id, event.time)
            event.handleEvents()

        #print("Depth of longest chain for peer 0: ", self.peers[0].longestBlk.depth)

        print("Simulation completed")
        print("Total peers: ", self.numPeers)
        print("Total blocks mined: ", self.blk_id-1)
        print("Total transactions: ", self.trxn_id-1)

        max_depth = 0
        Frac = [0,0,0,0]
        for i in range(self.numPeers):
            if peers[i].isSlow and peers[i].isLowCPU:
                Frac[0] += self.bins[i]
            elif peers[i].isSlow and not peers[i].isLowCPU:
                Frac[1] += self.bins[i]
            elif not peers[i].isSlow and peers[i].isLowCPU:
                Frac[2] += self.bins[i]
            else:
                Frac[3] += self.bins[i]
            max_depth = max(max_depth,self.peers[i].longestBlk.depth)
            self.peers[i].writeFile()
        blocks_ratio(self.bins,self.numPeers,self.slowPerc,self.lowCpuPerc,self.txnDelayMeanTime)
        total_blocks = sum(Frac)
        if total_blocks > 0:
            Frac = [f / total_blocks for f in Frac]
        print(f"Fraction of blocks by each tye :{Frac}")
        visualize_block_tree(self.peers[0].tree, self.avgInterArrivalTime)
        return max_depth




