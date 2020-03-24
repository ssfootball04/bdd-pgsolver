import sys
from antlr4 import *
from antlr4.tree.Trees import Trees
from parity_gameLexer import parity_gameLexer
from parity_gameParser import parity_gameParser
from dd import autoref as _bdd
import numpy as np
import copy
import sys
sys.setrecursionlimit(3500)

def main(argv):

	input_stream = StdinStream()
	lexer = parity_gameLexer(input_stream)
	stream = CommonTokenStream(lexer)
	parser = parity_gameParser(stream)
	tree = parser.parity_game()

	##########################################################
	###### extract game graph from the parse tree		######
	##########################################################

	children = Trees.getChildren(tree)
	maxNodeInd = int(Trees.getNodeText(children[1].children[0]))
	numActualNodes = len(children) - 3														# subtracting 3 for the first three tokens

	nodeList, colorList, ownerList, nodeSuccList = [], [], [], []
	nodePosDict = {}																		# required to lookup color, owner for a given nodeInd
	colorDict = {}																			# required to lookup color inverse

	for i in range(numActualNodes):

		gameNode = children[i+3]

		nodeInd = int(Trees.getNodeText(gameNode.children[0].children[0]))
		nodeColor = int(Trees.getNodeText(gameNode.children[1].children[0]))
		nodeOwner = bool(int(Trees.getNodeText(gameNode.children[2].children[0])))

		successorList = gameNode.children[3].children
		numSuccessors, nodeSuccessors = (len(successorList) + 1) // 2, [] 				    # compensating for ',' tokens
		for j in range(numSuccessors):
			nodeSuccessors.append(int(Trees.getNodeText(successorList[2*j].children[0])))

		nodeList.append(nodeInd)
		nodePosDict[nodeInd] = i
		colorList.append(nodeColor)
		if(nodeColor in colorDict):
			colorDict[nodeColor] = colorDict[nodeColor] + [nodeInd]
		else:
			colorDict[nodeColor] = [nodeInd]
		ownerList.append(nodeOwner)
		nodeSuccList.append(nodeSuccessors)

	##########################################################
	###### create BDD representation of the game 		######
	##########################################################

	numVariables = int(np.ceil( np.log( numActualNodes ) / np.log(2) )) + 1	  				  # 1 variable to encode the player and rest to encode vertices
	variableList = ['x{}'.format(i) for i in range( numVariables )] \
				   + ['X{}'.format(i) for i in range( numVariables )]						  # variables corresponding to current and next state

	###################################
	####     helper fns 	  	  #####
	###################################

	# maps a node index to its binary encoding
	def createSymbolicString(varType, owner, nodeInd):

		nodeStr = bin(nodeInd)[2:].zfill( numVariables - 1 )
		symbolicStr = '{}0'.format(varType) if owner else '~{}0'.format(varType)
		for i in range( numVariables - 1 ):
			symbolicStr += ' /\ {}{}'.format(varType, i+1) if bool(int(nodeStr[i])) else ' /\ ~{}{}'.format(varType, i+1)
		return symbolicStr

	# applies a boolean op to a list of formula strings
	def applyBooleanOp(listFormulaStrings, op):
		numFormulas = len(listFormulaStrings)

		if(numFormulas==0):
			return ''

		symbolicStr = ''
		for ind, formula in enumerate(listFormulaStrings):
			if (ind == numFormulas - 1):
				symbolicStr += '( {} )'.format(formula)
			else:
				symbolicStr += '( {} ) {} '.format(formula, op)
		return symbolicStr

	# maps a truth assignment to the node index as per the binary encoding
	def assignmentToNodeInd(assignment, primed=True):
		s = ''
		x = 'X' if primed else 'x'
		for i in range(1, numVariables):
			s += '1' if assignment[x + str(i)] else '0'
		return int(s, 2)

	# returns the set of states corresponding to a bdd expression
	def getStatesForPrinting(expression, primed=True):

		x = 'X' if primed else 'x'
		assignments = list(bdd.pick_iter(expression, care_vars=['{}{}'.format(x, i) for i in range(numVariables)]))
		states, statesStr = [], '{'
		for assignment in assignments:
			states.append(assignmentToNodeInd(assignment, primed=primed))
		states = np.sort(np.array(states))[::-1]

		for state in states:
			statesStr += str(state) + ', '
		if(len(statesStr)!=1):
			statesStr = statesStr[:-2]

		return statesStr + '}'

	bdd = _bdd.BDD()
	bdd.declare(*variableList)

	###################################
	####     vertex sets 	  	  #####
	###################################

	p0Nodes, p1Nodes = np.array(nodeList)[np.array(ownerList) == False], np.array(nodeList)[np.array(ownerList) == True]
	p0NodesSymbolicStr = applyBooleanOp([createSymbolicString('x', False, p0Node) for p0Node in p0Nodes], '\/')
	p1NodesSymbolicStr = applyBooleanOp([createSymbolicString('x', True, p1Node) for p1Node in p1Nodes], '\/')
	
	V_0 = bdd.add_expr(p0NodesSymbolicStr) if len(p0NodesSymbolicStr) > 0 else bdd.false
	V_1 = bdd.add_expr(p1NodesSymbolicStr) if len(p1NodesSymbolicStr) > 0 else bdd.false
	
	###################################
	####     edge set	 	  	  #####
	###################################

	edges = []
	for i in range(numActualNodes):
		nodeInd, nodeOwner, nodeSucc = nodeList[i], ownerList[i], nodeSuccList[i]
		nodeSymbolicStr = createSymbolicString('x', nodeOwner, nodeInd)
		successors = []
		for nodeSuccInd in nodeSucc:
			SuccNodeSymbolicStr = createSymbolicString('X', ownerList[nodePosDict[nodeSuccInd]], nodeSuccInd)
			successors.append(SuccNodeSymbolicStr)
		edges.append( applyBooleanOp( [nodeSymbolicStr, applyBooleanOp(successors, '\/')], '/\\' ) )
	edgeSetSymbolicStr = applyBooleanOp(edges, '\/')

	E = bdd.add_expr(edgeSetSymbolicStr)

	##########################################################
	####     			solve game 	  	  				 #####
	##########################################################

	prime = {}  # priming dictionary
	for i in range(numVariables):
		prime['x{}'.format(i)] = 'X{}'.format(i)

	###################################
	####     attractor fpi 	  	  #####
	###################################

	def attractor(player, region, V_0, V_1, V, E, debug=False):

		reachStates = region
		V_player = V_1 if player else V_0
		V_opponent = V_0 if player else V_1

		previousAttractor = bdd.false
		currentAttractor = reachStates
		while( previousAttractor != currentAttractor):											   # fpi

			previousAttractor = currentAttractor

			previousStates_player = (V_player & bdd.exist(['X{}'.format(i) for i in range(numVariables)], E & currentAttractor))
			previousStates_opponent = (V_opponent & ~bdd.exist(['X{}'.format(i) for i in range(numVariables)], E & (~currentAttractor & V)))

			previousStates = previousStates_player | previousStates_opponent					   # compute previous states
			previousStatesPrimed = bdd.let(prime, previousStates)								   # prime previous states
			currentAttractor = previousStatesPrimed | currentAttractor							   # take union of newfoundstates and previousAttractor

		return currentAttractor

	###################################
	####     setminus	op 	  	  #####
	###################################

	def setminus(region, V_0, V_1, nodemask):

		new_V0 = V_0 & ~region
		new_V1 = V_1 & ~region
		
		# calculate new node mask
		regionAssignments = list(bdd.pick_iter(region, care_vars=['X{}'.format(i) for i in range(numVariables)]))
		removeNodes = [assignmentToNodeInd(assignment, primed=True) for assignment in regionAssignments]
		new_nodeMask = copy.deepcopy(nodeMask)
		for nodeInd in removeNodes:
			new_nodeMask[nodePosDict[nodeInd]] = False

		return new_V0, new_V1, new_nodeMask

	###################################
	####     color inverse 	  	  #####
	###################################

	# find set of nodes of a given color in the graph
	def colorInverse(color, nodeMask):

		region = copy.deepcopy(colorDict[color])
		removeSet = []
		for nodeInd in region:
			if(not nodeMask[nodePosDict[nodeInd]]):
				removeSet.append(nodeInd)
		for nodeInd in removeSet:
			region.remove(nodeInd)
		return region

	###################################
	####  zielonka's algorithm    #####
	###################################

	def zielonka(V_0, V_1, E, nodeMask, debug=False):

		if( (V_0 == bdd.false ) & (V_1 == bdd.false) ):
			return bdd.false, bdd.false

		d = np.array(colorList)[nodeMask].max()
		i = d % 2
		j = 1 - i

		V_0primed = bdd.let(prime, V_0)
		V_1primed = bdd.let(prime, V_1)
		V = V_0primed | V_1primed

		region = colorInverse(d, nodeMask)
		regionSymbolicStr = applyBooleanOp([createSymbolicString('X', ownerList[nodePosDict[nodeInd]], nodeInd)
											for nodeInd in region], '\/')
		regionNodes = bdd.add_expr(regionSymbolicStr)
		regionAttractor = attractor(i, regionNodes, V_0, V_1, V, E)
		
		if(regionAttractor == V):

			if(i==0):
				return V, bdd.false
			else:
				return bdd.false, V
		
		else:

			G1_V0, G1_V1, G1_nodeMask = setminus(regionAttractor, V_0, V_1, nodeMask)
			wr_G1_V0, wr_G1_V1 = zielonka(G1_V0, G1_V1, E, G1_nodeMask, debug)

			if( (j==1) & (wr_G1_V1 == bdd.false)):
				
				return V, bdd.false
			
			elif( (j==0) & (wr_G1_V0 == bdd.false)):
			
					return bdd.false, V
			else:

				wr_G1_j = wr_G1_V1 if j==1 else wr_G1_V0
				wr_G1_j_attractor = attractor(j,wr_G1_j,V_0,V_1, V, E)

				G2_V0, G2_V1, G2_nodeMask = setminus(wr_G1_j_attractor, V_0, V_1, nodeMask)
				wr_G2_V0, wr_G2_V1 = zielonka(G2_V0, G2_V1, E, G2_nodeMask, debug)

				if(i==0):
					return wr_G2_V0, V & ~wr_G2_V0
				else:
					return V & ~wr_G2_V1, wr_G2_V1

	nodeMask = np.array([True for i in range(numActualNodes)])
	wr_v0, wr_v1 = zielonka(V_0,V_1,E,nodeMask, debug=False)

	print("Player 0 wins from nodes:")
	statesStr = getStatesForPrinting(wr_v0)
	print(statesStr)

	print("Player 1 wins from nodes:")
	statesStr = getStatesForPrinting(wr_v1)
	print(statesStr)

if __name__ == '__main__':
    main(sys.argv)
