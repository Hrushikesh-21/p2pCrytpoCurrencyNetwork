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
        #Inter-arrival Block Time
        self.avgInterArrivalTime = 10*1000
        # Hash Power
        self.lowHashPow = (100 / (1000 - 9*self.lowCpuPerc))/numPeers
        self.highHashPow = 10*self.lowHashPow
        # rho_ij in ms, c_ij in bits/ms
        self.rho = np.random.uniform(10, 500, (self.numPeers, self.numPeers))
        self.c = [[]*self.numPeers]
        self.peers = []
        #Genesis Block
        self.Genisis = None
        #Bins for drawing histogram for frac of number of blocks
        self.bins = [0]*(self.numPeers)

    def run(self):
        # mask for slow nodes and low nodes
        slows_mask = np.random.permutation([True] * int(self.numPeers * self.slowPerc/100) + [False] * (self.numPeers - int(self.numPeers * self.slowPerc/100)))
        lows_mask = np.random.permutation([True] * int(self.numPeers * self.lowCpuPerc/100) + [False] * (self.numPeers - int(self.numPeers * self.lowCpuPerc/100)))
        peers = []
        for i in range(self.numPeers):
            peers.append(Peer(i, slows_mask[i], lows_mask[i]))
        # create the Network
        CreateNetwork(peers)

        #Prints the network for checking
        debug(peers)

        self.peers = peers
        #init c matrix
        self.c = [[5 if peers[i].isSlow or peers[j].isSlow else 100 for j in range(self.numPeers)] for i in range(self.numPeers)] * (1000)

        #First Block Genesis
        self.Genesis = Block(self.blk_id, None, -1, 0, None, [0]*self.numPeers, 0)
        self.blk_id += 1

        for i in range(self.numPeers):
            # Add block into the Tree for visualization
            self.peers[i].tree.add_block(self.Genesis,0)
            # Add Genesis block to every peer
            self.peers[i].longestBlk = self.Genesis
            # Everyone starts mining on Genesis Block
            T_k = np.random.exponential(self.avgInterArrivalTime / (self.lowHashPow if self.peers[i].isLowCPU else self.highHashPow))
            newTask = Event(T_k, 'genBlock', i, self, None, self.Genesis)
            self.events.put(newTask)
            self.events.put(Event(0, 'genTransaction', i, self, None, None))

        # self.events contains the PQ of all events sorted by timestamp
        while (not self.events.empty()) and self.events.queue[0].time <= self.maxSimTime:
            event = self.events.get()
            print(event.event_type, event.peer_id, event.time)
            event.handleEvents()
        
        print("Simulation completed")
        print("Total peers: ", self.numPeers)
        print("Total blocks mined: ", self.blk_id-1)
        print("Total transactions: ", self.trxn_id-1)

        # Longest Blockchain depth
        max_depth = 0
        # Frac conatains fraction of blocks mined by each type
        # Frac[0] = slow and low Hash
        # Frac[1] = slow and high Hash
        # Frac[2] = Fast and low Hash
        # Frac[3] = Fast and high Hash
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
            # Write the tree into the file (see Files/{i}_tree.txt)
            self.peers[i].writeFile()
        # PLot the Histogram for frac mined by each peer
        #blocks_ratio(self.bins,self.numPeers,self.slowPerc,self.lowCpuPerc,self.txnDelayMeanTime,self.avgInterArrivalTime)
        # Create Frac
        total_blocks = sum(Frac)
        if total_blocks > 0:
            Frac = [f / total_blocks for f in Frac]
        print(f"Fraction of blocks by each tye :{Frac}")
        # Visualize Tree using Graphviz
        #visualize_block_tree(self.peers[0].tree, self.avgInterArrivalTime)
        return max_depth




