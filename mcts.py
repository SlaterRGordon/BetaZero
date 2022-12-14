import copy
import numpy as np
from node import Node
from utils import stateEncoder, policyDecoder, resultConvert

class MCTS():
    def __init__(self, nn, lock):
        self.nn = nn
        self.lock = lock
        
    def search(self, node, iterations):
        root = node
        
        for i in range(iterations):
            # select a leaf node
            current = root
            while current.expanded:
                current = self.select(current)
            
            # check if the game has ended
            if current.state.is_game_over():
                current.backpropagate(resultConvert[current.state.result()])
                break
            
            # evaluate node
            encodedState = stateEncoder(current.state)
            value, policy = self.nn.predict(encodedState, verbose=0)
            probs = policyDecoder(policy[0], current.state.legal_moves)
            
            # normalize probs
            sumProbs = sum(probs)
            if sumProbs == 0:
                probs = [1 for move in current.state.legal_moves]
                sumProbs = sum(probs)
            prob_factor = 1 / sumProbs
            probs = [prob_factor * p for p in probs]
            
            # expand leaf node
            self.expand(current, probs)
                    
            # backpropogate
            current.backpropagate(value[0][0])
        
        # pick child based on policy probs
        index = np.random.choice(len(root.probs), p=root.probs)
        
        return node.children[index]
    
    def select(self, node):
        # caluclate c puct
        c = np.log((node.visits + 19653) / 19652) + 1
        scores = []
        
        # for each child calculate ucb score
        for i, child in enumerate(node.children):
            q = child.value / 1 + child.visits
            score = q + c * child.prior * np.sqrt(node.visits / (1 + child.visits))
            scores.append(score)
        
        # return best child
        return node.children[np.argmax(scores)]

    def expand(self, node, probs):
        node.expanded = True
        node.probs = probs
        
        # create new children and add them to node
        for i, move in enumerate(node.state.legal_moves):
            state = copy.deepcopy(node.state)
            state.push(move)
            child = Node(state, node)
            node.addChild(child, probs[i], move)
    
    
        
            
        