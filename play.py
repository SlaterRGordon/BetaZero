import chess
import numpy as np
from mcts import MCTS
from node import Node
from utils import stateEncoder, policyEncoder, resultConvert
from queue import Queue
import threading
import multiprocessing as mp
import time
import random

class SelfPlay():
    def __init__(self, model, num_simulations=1000):
        self.num_simulations = num_simulations
        self.model = model
        state = chess.Board()
        self.node = Node(state, None)
        self.data = []
        self.lock = threading.Lock()
        self.times = []
        
    def runSimulations(self):
        # initialize the root of the simulation tree
        root = self.node
        
        # run the specified number of simulations
        for i in range(self.num_simulations):
            
            # generate examples from the simulations
            self.generateData(root)
                
            # train the model with the generated data
            self.train(32)
            
    def generateData(self, root):
        results = Queue()
        
        def simulate(root, model):
            # initialize mcts and root node
            mcts = MCTS(self.model, self.lock)
            node = root
            
            # initialize list to store examples
            examples = []
            
            # continue searching until the game is over or the maximum depth is reached
            while not node.state.is_game_over() and node.depth < 200:
                # Run mcts to find the best child for the current node
                node = mcts.search(node, 5)
                
                # add the node to the list of examples
                examples.append([node, node.state, None, None])
            
            if node.state.is_game_over():
                result = resultConvert[node.state.result()] * node.color * -1
            else:
                result = -1
            
            # set the policy and value for each example
            for example in examples:
                example[3] = result
                result = result * -1
                example[2] = example[0].getActualProbabilities()
            
            results.put(examples)
        
        num_threads = mp.cpu_count() // 2
        threads = [threading.Thread(target=simulate, args=(), kwargs={'model': self.model, 'root': root}) for _ in range(num_threads)]
        
        # start timer
        start = time.time()
        
        # Start the threads
        for thread in threads:
            thread.start()
            
        for thread in threads:
            thread.join()
            
        # end timer
        end = time.time()
        self.times.append(end - start)
        
        print("Simulate Time: {}, Per Game Time: {}".format(end - start, (end - start) / 8))
        print("Average Simulate Time: {}, Average Per Game Time: {}".format(np.mean(self.times), np.mean(self.times) / 8))
        
        # Get the results from the queue
        for _ in range(results.qsize()):
            for example in results.get():
                self.addToData(example[1], example[2], example[3])   
            
    def train(self, batchSize):
        # initialize list to store losses
        losses = []
        
        # shuffle data
        random.shuffle(self.data)
        
        # iterate over the data in batches
        for i in range(0, len(self.data), batchSize):
            # unpack the data into states, policies, and values
            states, policies, values = map(list, zip(*self.data[i:i + batchSize]))
            
            # reshape the states into a 4D tensor
            states = np.reshape(np.array(states), (-1, 8, 8, 17))
            
            # convert the policies and values to numpy arrays
            policies = np.array(policies)
            values = np.reshape(np.array(values), (-1, 1))
            
            # train the model with the data
            labels = {'policy': policies, 'value': values}
            history = self.model.fit(states, labels)
            losses += [history.history['loss']]
            
            # print the loss for the current batch
            print("Batch {}: {}".format(i, history.history['loss']))
        
        # print the mean loss for all batches
        print("Total: {}".format(np.mean(losses)))
        
        # reset the training data and save model
        self.data = []
        self.model.save('bestModel.h5')
    
    def addToData(self, state, policy, result):
        # encode policy and state to a format that the model recognizes
        policy = policyEncoder(policy, state.legal_moves)
        state = stateEncoder(state)
        result = np.array(result)
        
        self.data.append([state, policy, result])
        
    def pickMove(self, state, iterations):
        mcts = MCTS(self.model)
        node = Node(state, None)
        child = mcts.search(node, iterations)
        
        return child     
    