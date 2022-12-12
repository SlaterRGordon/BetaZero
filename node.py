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
        child.color = self.color*-1
        child.prior = prior
        child.depth = self.depth + 1
        child.move = move
        self.children.append(child)
        
    def backpropagate(self, value):
        self.visits += 1
        self.value += value*self.color
        
        if self.parent is not None:
            self.parent.backpropagate(self.value)
    
    def getActualProbabilities(self):
        probs = []
        
        if self.visits == 0:
            return [1 for move in self.state.legal_moves]
            
        for child in self.children:
            prob = child.visits / self.visits
            probs.append(prob)
            
        probsSum = sum(probs)
        if probsSum == 0:
            return [1 for move in self.state.legal_moves]
        probs = [prob / probsSum for prob in probs]
    
        return probs
            
        