from peer import Peer
import random
import numpy as np

def isConnected(Peers):
        # Check connectivity of the network
        peers = len(Peers)
        visited = [False for i in range(peers)]
        def dfs(node):
            visited[node] = True
            for neighbor in Peers[node].neighbors:
                if not visited[neighbor]:
                    dfs(neighbor)
        dfs(0)
        for node in range(peers):
            if not visited[node]:
                # if anything is not visted its not connected
                return False
        return True

def CreateNetwork(Peers):
    while True:
        # Keep creating Graphs until its all connected
        createGraph(Peers)
        if isConnected(Peers):
            return
        for peer in Peers:
            peer.clear_neighbors()

def createGraph(Peers):
    peers = len(Peers)
    # Current Degree of each Node
    degree = [0 for i in range(peers)]
    #Choices of the degree for each Peer
    choice = [random.randint(3,6) for i in range(peers)]
    # Available nodes
    available = set(range(peers))
    for i in range(peers):
        # Already Requirement Satisfied
        if i in available:
            available.remove(i)
        remain = min(choice[i]-degree[i],len(available))
        if remain<=0 : 
             continue
        # Randomly select other nodes
        neighbors = np.random.choice(list(available),remain,replace=False)
        for j in neighbors:
            Peers[i].neighbors.append(j)
            Peers[j].neighbors.append(i)
            degree[i] += 1
            degree[j] += 1
            if degree[j] == 6:
                available.remove(j)
def debug(Peers):
    for i in range(len(Peers)):
        print(f"Peer {i} connected to: {Peers[i].neighbors}")