# CS765 Assignment 1  
## Simulation of a P2P Cryptocurrency Network  

### Setup  
Create the required directories in the current directory:  
```sh
mkdir Images
mkdir Files
```
Install the required libraries:  
```sh
pip install matplotlib numpy networkx pygraphviz
```

### Usage  
Run the script with the required arguments:  
```sh
python main.py --numPeers NUMPEERS --slowPerc SLOWPERC --lowCpuPerc LOWCPUPERC \
               --txnDelayMeanTime TXNDELAYMEANTIME --maxSimTime MAXSIMTIME \
               [--maxBlockSize MAXBLOCKSIZE] [--maxTransactionSize MAXTRANSACTIONSIZE] [--miningFee MININGFEE]
```

### 🔹 Required Arguments  
| Argument                | Description |
|-------------------------|-------------|
| `--numPeers`           | Number of peers in the network |
| `--slowPerc`           | Percentage of peers that are slow |
| `--lowCpuPerc`         | Percentage of peers with low CPU power |
| `--txnDelayMeanTime`   | Average inter-arrival time between transactions |
| `--maxSimTime`         | Maximum simulation time before termination |

### 🔹 Optional Arguments  
| Argument                | Description |
|-------------------------|-------------|
| `--maxBlockSize`       | Maximum block size |
| `--maxTransactionSize` | Maximum transaction size |
| `--miningFee`          | Mining fee per Block |

### Example Command  
```sh
python main.py --numPeers 100 --slowPerc 20 --lowCpuPerc 15 \
               --txnDelayMeanTime 10000 --maxSimTime 5000000\
```

---


