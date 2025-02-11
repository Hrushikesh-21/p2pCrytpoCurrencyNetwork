from transaction import *
from block import *
from simulator import *
import numpy as np

class Event():
    def __init__(self, time, event_type, peer_id, sim, transaction=None, block=None):
        self.time = time
        self.event_type = event_type
        self.peer_id = peer_id
        self.sim = sim
        self.transaction = transaction
        self.block = block

    def __lt__(self, other):
        # Sort them using comparitor
        return self.time < other.time

    def Latency(self, dst, size):
        # Latency time between peer to dst of msg size (size)
        c_ij = self.sim.c[self.peer_id][dst]
        rho_ij = self.sim.rho[self.peer_id][dst]
        d_ij = np.random.exponential((96*1000)/c_ij)
        return d_ij + rho_ij + (size)/(c_ij)
    
    def handleEvents(self):
        # Event handler
        if(self.event_type == 'genTransaction'):
            self.genTransaction()
        elif(self.event_type == 'recTransaction'):
            self.recTransaction()
        elif(self.event_type == 'genBlock'):
            self.genBlock()
        elif(self.event_type == 'recBlock'):
            self.recBlock()
            
    def genTransaction(self):
        # random choice recepient id
        rec_id = np.random.choice([i for i in range(0, self.sim.numPeers) if i != self.peer_id])
        if self.sim.peers[self.peer_id].longestBlk.balances[self.peer_id] == 0:
            # Create a new Transcation
            self.sim.events.put(Event(self.time + np.random.exponential(self.sim.txnDelayMeanTime), 'genTransaction', self.peer_id, self.sim))
            return
        elif self.sim.peers[self.peer_id].longestBlk.balances[self.peer_id] == 1:
            amount = 1
        else:
            amount = np.random.randint(1, self.sim.peers[self.peer_id].longestBlk.balances[self.peer_id])
        # Schedule a new Transcation after a time T_tx
        transaction = Transaction(self.sim.trxn_id, self.peer_id, rec_id, amount)
        self.sim.trxn_id += 1
        self.sim.events.put(Event(self.time, 'recTransaction', self.peer_id, self.sim,transaction))
        self.sim.events.put(Event(self.time + np.random.exponential(self.sim.txnDelayMeanTime), 'genTransaction', self.peer_id, self.sim))
        return 

    def recTransaction(self):
        if self.transaction.id in self.sim.peers[self.peer_id].transaction_ids:
            return
        # add transcation ids to transcation_ids seen by the peer
        self.sim.peers[self.peer_id].transaction_ids.add(self.transaction.id)
        self.sim.peers[self.peer_id].transactions.append(self.transaction)
        self.broadcast()
        return 

    def verifyTrans(self, trans, balances):
        return balances[trans.sender] >= trans.amount and trans.amount>0

    def genBlock(self):
        if self.block != self.sim.peers[self.peer_id].longestBlk:
            return
        self.sim.bins[self.peer_id]+=1
        currBlk = self.block
        currBalances = deepcopy(self.block.balances)
        # Mined transcations are all the trnscation that are already mined
        minedTransactions = []
        while currBlk != None:
            if currBlk.transactions != None:
                minedTransactions = minedTransactions + currBlk.transactions
            currBlk = currBlk.prevBlock

        minedTransactions = set(minedTransactions)
        # transactions aval = transactions_seen - mined_transactions
        blkTransactions = []
        if self.sim.peers[self.peer_id].transactions != None:
            for trans in self.sim.peers[self.peer_id].transactions:
                # Verify transactions before adding
                if trans not in minedTransactions and self.verifyTrans(trans, currBalances):
                    currBalances[trans.sender] -= trans.amount
                    currBalances[trans.recipient] += trans.amount
                    blkTransactions.append(trans)
                if len(blkTransactions) == 999:
                    break
        # coin Base Transactions
        currBalances[self.peer_id] += 50
        # Generate new block
        newBlock = Block(self.sim.blk_id, self.block, self.peer_id, self.time, blkTransactions, currBalances, self.block.depth+1)
        self.sim.blk_id += 1
        # Recieve block to urself to create broadcast chain
        self.sim.peers[self.peer_id].longestBlk = newBlock
        newTask = Event(self.time, 'recBlock', self.peer_id, self.sim, None, newBlock)
        self.sim.events.put(newTask)
        return

    def verifyBlock(self, block):
        # verify the block send by the other peer
        currBlk = block.prevBlock
        currBalances = deepcopy(block.prevBlock.balances)
        minedTransactions = []
        while currBlk != None:
            if currBlk.transactions != None:
                minedTransactions = minedTransactions + currBlk.transactions
            currBlk = currBlk.prevBlock
        minedTransactions = set(minedTransactions)
        if block.transactions != None:
            for trans in block.transactions:
                if trans not in minedTransactions and self.verifyTrans(trans, currBalances):
                    currBalances[trans.sender] -= trans.amount
                    currBalances[trans.recipient] += trans.amount
                else:
                    return False
        return True

    def recBlock(self):
        if self.block.id in self.sim.peers[self.peer_id].block_ids:
            # If already seen dont do anything
            return
        # Add the block into the BlockTree
        self.sim.peers[self.peer_id].tree.add_block(self.block,self.time)
        # Add block_ids into already seen by the peer
        self.sim.peers[self.peer_id].block_ids.add(self.block.id)
        self.broadcast()
        if self.verifyBlock(self.block):
            if self.block.depth > self.sim.peers[self.peer_id].longestBlk.depth or (self.block.depth == self.sim.peers[self.peer_id].longestBlk.depth and self.block.timestamp < self.sim.peers[self.peer_id].longestBlk.timestamp):
                # If received block is the new longest block update the longest block and start mining on it
                self.sim.peers[self.peer_id].longestBlk = self.block
                T_k = np.random.exponential(self.sim.avgInterArrivalTime / (self.sim.lowHashPow if self.sim.peers[self.peer_id].isLowCPU else self.sim.highHashPow))
                newTask = Event(self.time + T_k, 'genBlock', self.peer_id, self.sim, None, self.block)
                self.sim.events.put(newTask)
        return
    
    def broadcast(self):
        # Broadcast the Block/Transaction to all others
        size = -1
        eve_type = 'recBlock'
        if self.transaction == None:
            if self.block.transactions != None:
                size = len(self.block.transactions)*8000 + 8000
            else:
                size = 8000
        else:
            size = 8000
            eve_type = 'recTransaction'
        for dst in self.sim.peers[self.peer_id].neighbors :
            latency = self.Latency(dst, size)
            newEvent = Event(self.time+latency, eve_type, dst, self.sim, self.transaction, self.block)
            self.sim.events.put(newEvent)
        return
    
