import numpy as np
import matplotlib.pyplot as plt
from simulator import Simulate

# Default values for parameters (normal conditions)
default_numPeers = 50
default_slowPerc = 20
default_lowCpuPerc = 30
default_txnDelayMeanTime = 2000
maxSimTime = 1000000
maxBlockSize = 1000
maxTransactionSize = 1
miningFee = 50

results = []

# Vary numPeers independently
numPeers_values = [5, 10, 20, 50, 100]
for numPeers in numPeers_values:
    S = Simulate(numPeers, default_slowPerc, default_lowCpuPerc, default_txnDelayMeanTime, maxSimTime, maxBlockSize , maxTransactionSize, miningFee)
    max_depth = S.run()
    results.append((numPeers, max_depth))

# Convert results to NumPy array
results = np.array(results)

# Extract data
numPeers_data = results[:, 0]
max_depth_data = results[:, 1]

# Plot max depth vs. numPeers
plt.figure(figsize=(8, 5))
plt.plot(numPeers_data, max_depth_data, marker='o', linestyle='-', color='b', label="Max Depth")
plt.xlabel("Number of Peers")
plt.ylabel("Maximum Blockchain Depth")
plt.title("Effect of Number of Peers on Max Blockchain Depth")
plt.legend()
plt.grid()
plt.savefig("Images/max_depth_vs_numPeers.png")
plt.close()

# Repeat for slowPerc
results = []
slowPerc_values = [10, 30, 50, 70]
for slowPerc in slowPerc_values:
    S = Simulate(default_numPeers, slowPerc, default_lowCpuPerc, default_txnDelayMeanTime, maxSimTime, maxBlockSize , maxTransactionSize, miningFee)
    max_depth = S.run()
    results.append((slowPerc, max_depth))

results = np.array(results)
plt.figure(figsize=(8, 5))
plt.plot(results[:, 0], results[:, 1], marker='o', linestyle='-', color='r', label="Max Depth")
plt.xlabel("Slow Node Percentage")
plt.ylabel("Maximum Blockchain Depth")
plt.title("Effect of Slow Nodes on Max Blockchain Depth")
plt.legend()
plt.grid()
plt.savefig("Images/max_depth_vs_slowPerc.png")
plt.close()

# Repeat for lowCpuPerc
results = []
lowCpuPerc_values = [10, 30, 50, 70]
for lowCpuPerc in lowCpuPerc_values:
    S = Simulate(default_numPeers, default_slowPerc, lowCpuPerc, default_txnDelayMeanTime, maxSimTime, maxBlockSize , maxTransactionSize, miningFee)
    max_depth = S.run()
    results.append((lowCpuPerc, max_depth))

results = np.array(results)
plt.figure(figsize=(8, 5))
plt.plot(results[:, 0], results[:, 1], marker='o', linestyle='-', color='g', label="Max Depth")
plt.xlabel("Low CPU Percentage")
plt.ylabel("Maximum Blockchain Depth")
plt.title("Effect of Low CPU Nodes on Max Blockchain Depth")
plt.legend()
plt.grid()
plt.savefig("Images/max_depth_vs_lowCpuPerc.png")
plt.close()

# Repeat for txnDelayMeanTime
results = []
txnDelay_values = [200, 2000, 200000, 200000]
for txnDelayMeanTime in txnDelay_values:
    S = Simulate(default_numPeers, default_slowPerc, default_lowCpuPerc, txnDelayMeanTime, maxSimTime ,maxBlockSize , maxTransactionSize, miningFee)
    max_depth = S.run()
    results.append((txnDelayMeanTime, max_depth))

results = np.array(results)
plt.figure(figsize=(8, 5))
plt.plot(results[:, 0], results[:, 1], marker='o', linestyle='-', color='purple', label="Max Depth")
plt.xlabel("Transaction Delay Mean Time")
plt.ylabel("Maximum Blockchain Depth")
plt.title("Effect of Transaction Delay on Max Blockchain Depth")
plt.legend()
plt.grid()
plt.savefig("Images/max_depth_vs_txnDelay.png")
plt.close()
