import sys
from antlr4 import *
from antlr4.tree.Trees import Trees
from parity_gameLexer import parity_gameLexer
from parity_gameParser import parity_gameParser
from dd import autoref as _bdd
import numpy as np

def main(argv):

	# print('Enter a node specification in PGSolver input format')
	# input_stream = InputStream(input(">"))

	input_stream = StdinStream()
	lexer = parity_gameLexer(input_stream)
	stream = CommonTokenStream(lexer)
	parser = parity_gameParser(stream)
	tree = parser.parity_game()
	# print(Trees.toStringTree(tree, None, parser))

	##########################################################
	###### extract game graph from the parse tree		######
	##########################################################

	children = Trees.getChildren(tree)
	maxNodeInd = int(Trees.getNodeText(children[1].children[0]))
	numActualNodes = len(children) - 3														# subtracting 3 for the first three tokens
	# print(maxNodeInd, numActualNodes)

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

		# print(nodeInd, nodeColor, nodeOwner, nodeSuccessors)
		nodeList.append(nodeInd)
		nodePosDict[nodeInd] = i
		colorList.append(nodeColor)
		if(nodeColor in colorDict):
			colorDict[nodeColor] = colorDict[nodeColor].append(nodeInd)
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

	# convert a tuple(var, owner, nodeInd) into its symbolic representation
	# varType: 'x' | 'X'; owner: True | False; nodeInd < numActualNodes
	# uses simple binary encoding described in the lecture

	def createSymbolicString(varType, owner, nodeInd):

		nodeStr = bin(nodeInd)[2:].zfill( numVariables - 1 )
		symbolicStr = '{}0'.format(varType) if owner else '~{}0'.format(varType)
		for i in range( numVariables - 1 ):
			symbolicStr += ' /\ {}{}'.format(varType, i+1) if bool(int(nodeStr[i])) else ' /\ ~{}{}'.format(varType, i+1)
		return symbolicStr

	def applyBooleanOp(listFormulas, op):
		numFormulas = len(listFormulas)
		symbolicStr = ''
		for ind, formula in enumerate(listFormulas):
			if (ind == numFormulas - 1):
				symbolicStr += '( {} )'.format(formula)
			else:
				symbolicStr += '( {} ) {} '.format(formula, op)
		return symbolicStr

	# print(createSymbolicString('x', ownerList[1], nodeList[1]))

	bdd = _bdd.BDD()
	bdd.declare(*variableList)

	###################################
	####     vertex sets 	  	  #####
	###################################

	p0Nodes, p1Nodes = np.array(nodeList)[np.array(ownerList) == False], np.array(nodeList)[np.array(ownerList) == True]
	p0NodesSymbolicStr = applyBooleanOp([createSymbolicString('x', False, p0Node) for p0Node in p0Nodes], '\/')
	p1NodesSymbolicStr = applyBooleanOp([createSymbolicString('x', True, p1Node) for p1Node in p1Nodes], '\/')
	nextStatesSymbolicStr = applyBooleanOp([createSymbolicString('X', False, p0Node) for p0Node in p0Nodes] +
									[createSymbolicString('X', True, p1Node) for p1Node in p1Nodes], '\/')

	# print(p0NodesSymbolicStr, len(p0Nodes))
	# print(p1NodesSymbolicStr, len(p1Nodes))
	V_0 = bdd.add_expr(p0NodesSymbolicStr)
	V_1 = bdd.add_expr(p1NodesSymbolicStr)
	V_next = bdd.add_expr(nextStatesSymbolicStr)
	
	###################################
	####     edge function 	  	  #####
	###################################
	
	# edgeFns = []
	# for i in range(numActualNodes):
	# 	nodeInd, nodeOwner, nodeSucc = nodeList[i], ownerList[i], nodeSuccList[i]
	# 	SuccNodesSymbolicStr = applyBooleanOp([createSymbolicString('X', ownerList[nodePosDict[nodeSuccInd]], nodeSuccInd)
	# 										   for nodeSuccInd in nodeSucc], '\/')
	# 	nodeSymbolicStr = createSymbolicString('x', nodeOwner, nodeInd)
	# 	edgeFns.append('{} => {}'.format(nodeSymbolicStr, SuccNodesSymbolicStr))
	# edgeFnSymbolicStr = applyBooleanOp(edgeFns, '/\\')
    #
	# # print(edgeFnSymbolicStr)
	# E = bdd.add_expr(edgeFnSymbolicStr)

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

	# print(edgeSetSymbolicStr)
	E = bdd.add_expr(edgeSetSymbolicStr)

	###################################
	####     attractor fpi 	  	  #####
	###################################

	def attractor(player, region, V_0, V_1, E):

		reachStates = region
		V_alp = V_1 if player else V_0
		V_bet = V_0 if player else V_1

		prime = {}																				    # priming dictionary
		for i in range(numVariables):
			prime['x{}'.format(i)] = 'X{}'.format(i)

		previousAttractor = bdd.false
		currentAttractor = reachStates
		while( previousAttractor != currentAttractor):											   # fpi

			previousAttractor = currentAttractor												   # compute previous states
			previousStates = ( V_alp & bdd.exist( ['X{}'.format(i) for i in range(numVariables)] , E & currentAttractor ) ) \
							 | ( V_bet & ~bdd.exist( ['X{}'.format(i) for i in range(numVariables)] , E & ~currentAttractor ) )
			previousStatesPrimed = bdd.let(prime, previousStates)								   # prime previous states
			currentAttractor = previousStatesPrimed | currentAttractor							   # take union of newfoundstates and previousAttractor

		return currentAttractor

	region = bdd.add_expr(createSymbolicString('X', ownerList[0], nodeList[0]))					   # arbitrary reach states for player 0, unit testing
	currentAttractor = attractor(False,region)
	print('number of states in attractor: ', currentAttractor.count(nvars=numVariables))
	# assignments = list(bdd.pick_iter(currentAttractor, ['X{}'.format(i) for i in range(numVariables)]))
	# for assignment in assignments:
	# 	print(assignment)

	###################################
	####     solve game 	  	  #####
	###################################

	# use colorDict and set operations using BDD representation to find inverse
	# recursive Zielonka takes V_0, V_1, E (all in BDD representation) and colorMapping of the vertices as input
	# V_0, V_1 change, E remains constant. algorithm returns winning regions as sets in BDD representation

if __name__ == '__main__':
    main(sys.argv)
