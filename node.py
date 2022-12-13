class Node():
    def __init__(self, state, parent):
        self.state = state
        self.parent = parent
        self.children = []
        self.value = 0
        self.prior = None
        self.probs = [1 for move in state.legal_moves]
        self.visits = 0
        self.color = 1
        self.depth = 0
        self.expanded = False
        self.move = None
    
    def addChild(self, child, prior, move):
        child.parent = self
        child.color = self.color*-1 # set the color of the child to the opposite of the parent's color
        child.prior = prior
        child.depth = self.depth + 1
        child.move = move
        
        # add the child to the list of children for the current node
        self.children.append(child)
        
    def backpropagate(self, value):
        self.visits += 1
        self.value += value*self.color
        
        # if the current node has a parent, backpropagate the value to the parent
        if self.parent is not None:
            self.parent.backpropagate(self.value)
    
    def getActualProbabilities(self):
        probs = []
        
        # if the node has not been visited, return a list of 1s
        if self.visits == 0:
            return [1 for move in self.state.legal_moves]
        
        # calculate the probability for each child
        for child in self.children:
            prob = child.visits / self.visits
            probs.append(prob)
            
        probsSum = sum(probs)
        
        # if the sum is 0, return a list of 1s
        if probsSum == 0:
            return [1 for move in self.state.legal_moves]
        
        # normalize the probabilities
        probs = [prob / probsSum for prob in probs]
    
        return probs
            
        