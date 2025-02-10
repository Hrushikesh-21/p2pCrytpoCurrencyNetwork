from block import *
import os
class BlockNode:
    def __init__(self, block, time):
        self.block = block
        self.parent = None
        self.children = []
        self.time = time

class BlockTree:
    def __init__(self):
        self.nodes = {}  
        self.root = None
    
    def add_block(self, block, time):
        if block in self.nodes:
            self.nodes[block].time = time
            return
        node = BlockNode(block,time)
        self.nodes[block] = node 
        if block.prevBlock is None:  
            self.root = node
            return
        cur_block = block
        while cur_block.prevBlock not in self.nodes:
            parent_node = BlockNode(cur_block.prevBlock,-1)
            self.nodes[cur_block.prevBlock] = parent_node
            parent_node.children.append(node)
            node.parent = parent_node
            cur_block = cur_block.prevBlock
            node = parent_node
        parent_node = self.nodes[cur_block.prevBlock]
        parent_node.children.append(node)
        node.parent = parent_node
    
    def dfs(self, node, fd, prefix="", is_last=True):   
        connector = "└── " if is_last else "├── "  
        parent_id = node.block.prevBlock.id if node.block.prevBlock else 0
        fd.write(prefix + connector + f"Block: {node.block.id} Time: {node.time} Parent: {parent_id}\n")
        new_prefix = prefix + ("    " if is_last else "│   ")
        for i, child in enumerate(node.children):
            last_child = (i == len(node.children) - 1)
            self.dfs(child, fd, new_prefix, last_child)  
  
    
    def writeTree(self, peer_id):
        os.makedirs("Files", exist_ok=True) 
        filename = os.path.join("Files", f"{peer_id}_tree.txt")
        with open(filename, "w", encoding="utf-8") as f: 
            if self.root:
                self.dfs(self.root, f)
