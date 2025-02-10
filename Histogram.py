import numpy as np
import matplotlib.pyplot as plt
import networkx as nx

import networkx as nx
import matplotlib.pyplot as plt

def visualize_block_tree(tree, peer_id):
    G = nx.DiGraph()
    def add_edges(node):
        for child in node.children:
            G.add_edge(node.block.id, child.block.id)
            add_edges(child)
    add_edges(tree.root)
    plt.figure(figsize=(12, 8))
    pos = nx.nx_agraph.graphviz_layout(G, prog="dot")  
    node_colors = ["red" if node == 0 else "darkred" for node in G.nodes]
    nx.draw(G, pos, with_labels=True, node_size=800, node_color=node_colors, font_size=10, 
            font_color="white", edge_color="black", arrows=True)
    plt.title(f"BlockTree Visualization for Peer {peer_id}")
    plt.savefig(f"Images/blocktree_{peer_id}.png", dpi=300, bbox_inches='tight')
    plt.close()

def blocks_ratio(bins, n, z0, z1, Tk):
    total_blocks = sum(bins)
    if total_blocks > 0:
        bins = [b / total_blocks for b in bins]
    peer_ids = np.arange(len(bins))
    plt.figure(figsize=(8, 5))
    plt.hist(peer_ids, bins=len(bins), weights=bins, edgecolor='black', alpha=0.7, align='mid')
    plt.xlabel('Peer ID')
    plt.ylabel('Number of Blocks Mined')
    plt.title(f'Histogram of Blocks Mined (n={n}, z0={z0}, z1={z1}, Tk={Tk})')
    plt.xticks(peer_ids)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.savefig(f"Images/histogram_{n}_{z0}_{z1}_{Tk}.png", dpi=300, bbox_inches='tight')
    plt.close()
