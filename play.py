import chess
from tqdm import tqdm
import numpy as np
import multiprocessing as mp
from mcts import MCTS
from node import Node
from utils import stateEncoder, policyEncoder, resultConvert
import threading
from queue import Queue

class SelfPlay():
    def __init__(self, model, num_simulations=1000):
        self.num_simulations = num_simulations
        self.model = model
        state = chess.Board()
        self.node = Node(state, None)
        self.data = []
        self.lock = threading.Lock()
        
    def runSimulations(self):
        root = self.node
        for i in range(self.num_simulations):
            print("Generating Data")
            examples = self.simulate(root)
            for example in examples:
                self.addToData(example[1], example[2], example[3])
            # self.generateData(root)
            print("Training Model")
            self.train(32)
            
    def train(self, batchSize):
        losses = []
        
        print(len(self.data))
        
        for i in range(0, len(self.data), batchSize):
            states, policies, values = map(list, zip(*self.data[i:i + batchSize]))
            
            states = np.reshape(np.array(states), (-1, 8, 8, 17))
            policies = np.array(policies)
            values = np.reshape(np.array(values), (-1, 1))
            
            labels = {'policy': policies, 'value': values}
            history = self.model.fit(states, labels)
            losses += [history.history['loss']]
            print("Batch {}: {}".format(i, history.history['loss']))
        
        print("Total: {}".format(np.mean(losses)))
        self.data = []
        self.saveModel()
        
    def saveModel(self):
        self.model.save('bestModel.h5')
    
    def simulate(self, root):
        mcts = MCTS(self.model, self.lock)
        node = root
        
        examples = []
        
        while not node.state.is_game_over() and node.depth < 300:
            # Run MCTS to find the best child for the current node
            node = mcts.search(node, 5)
            examples.append([node, node.state, None, None])

        if node.state.is_game_over():
            result = resultConvert[node.state.result()] * node.color * -1
        else:
            result = -1
        
        for example in examples:
            example[3] = result
            result = result * -1
            example[2] = example[0].getActualProbabilities()
        
        return examples
    
    # def generateData(self, root):
    #     results = Queue()
    #     def simulate(model, root):
    #         with self.lock:
    #             mcts = MCTS(model, self.lock)
    #             node = root
                
    #             examples = []
                
    #             while not node.state.is_game_over() and node.depth < 300:
    #                 # Run MCTS to find the best child for the current node
    #                 node = mcts.search(node, 5)
    #                 examples.append([node, node.state, None, None])
    #                 print(node.depth)

    #         if node.state.is_game_over():
    #             result = resultConvert[node.state.result()] * node.color * -1
    #         else:
    #             result = -1
            
    #         for example in examples:
    #             example[3] = result
    #             result = result * -1
    #             example[2] = example[0].getActualProbabilities()
            
    #         results.put(examples)
        
    #     num_threads = mp.cpu_count() // 2
    #     threads = [threading.Thread(target=simulate, args=(), kwargs={'model': self.model, 'root': root}) for _ in range(num_threads)]
        
    #     # Start the threads
    #     for thread in threads:
    #         thread.start()
            
    #     for thread in threads:
    #         thread.join()
        
    #     # Get the results from the queue
    #     for _ in range(results.qsize()):
    #         for example in results.get():
    #             self.addToData(example[1], example[2], example[3])
                    
    
    def addToData(self, state, policy, result):
        policy = policyEncoder(policy, state.legal_moves)
        state = stateEncoder(state)
        result = np.array(result)
        
        self.data.append([state, policy, result])
        
            
        