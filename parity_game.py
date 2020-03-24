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

		if(numFormulas==0):
			return ''

		symbolicStr = ''
		for ind, formula in enumerate(listFormulas):
			if (ind == numFormulas - 1):
				symbolicStr += '( {} )'.format(formula)
			else:
				symbolicStr += '( {} ) {} '.format(formula, op)
		return symbolicStr

	def assignmentToNodeInd(assignment, primed=True):
		s = ''
		p = 'X' if primed else 'x'
		for i in range(1, numVariables):
			s += '1' if assignment[p + str(i)] else '0'
		return int(s, 2)

	def getStatesForPrinting(formula, primed=True):
		p = 'X' if primed else 'x'
		assignments = list(bdd.pick_iter(formula, care_vars=['{}{}'.format(p, i) for i in range(numVariables)]))
		states, statesStr = [], '{'
		for assignment in assignments:
			states.append(assignmentToNodeInd(assignment, primed=primed))
		states = np.sort(np.array(states))[::-1]
		for state in states:
			statesStr += str(state) + ', '
		return statesStr + '}'

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

	V_0 = bdd.add_expr(p0NodesSymbolicStr) if len(p0NodesSymbolicStr) > 0 else bdd.false
	V_1 = bdd.add_expr(p1NodesSymbolicStr) if len(p1NodesSymbolicStr) > 0 else bdd.false
	V_next = bdd.add_expr(nextStatesSymbolicStr)
	
	###################################
	####     edge function 	  	  #####
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

	prime = {}  # priming dictionary
	for i in range(numVariables):
		prime['x{}'.format(i)] = 'X{}'.format(i)

	###################################
	####     attractor fpi 	  	  #####
	###################################

	def attractor(player, region, V_0, V_1, V, E, debug=False):

		reachStates = region
		V_alp = V_1 if player else V_0
		V_bet = V_0 if player else V_1

		previousAttractor = bdd.false
		currentAttractor = reachStates
		while( previousAttractor != currentAttractor):											   # fpi

			previousAttractor = currentAttractor												   # compute previous states

			player_nodes = (V_alp & bdd.exist(['X{}'.format(i) for i in range(numVariables)], E & currentAttractor))
			opponent_nodes = (V_bet & ~bdd.exist(['X{}'.format(i) for i in range(numVariables)], E & (~currentAttractor & V)))
			previousStates = player_nodes | opponent_nodes

			if (debug):
				print('Nodes from player: ', getStatesForPrinting(player_nodes, False))
				print('Nodes from opponent: ', getStatesForPrinting(opponent_nodes, False))
				print('Previous states are: ', getStatesForPrinting(previousStates, False))

			previousStatesPrimed = bdd.let(prime, previousStates)								   # prime previous states
			currentAttractor = previousStatesPrimed | currentAttractor							   # take union of newfoundstates and previousAttractor

		return currentAttractor


	###################################
	####     solve game 	  	  #####
	###################################

	def colorInverse(color, nodeMask):

		region = copy.deepcopy(colorDict[color])
		removeSet = []
		for nodeInd in region:
			if(not nodeMask[nodePosDict[nodeInd]]):
				removeSet.append(nodeInd)
		for nodeInd in removeSet:
			region.remove(nodeInd)
		return region

	def zielonka(V_0, V_1, E, nodeMask, debug=False):

		if( (V_0 == bdd.false ) & (V_1 == bdd.false) ):
			return bdd.false, bdd.false

		if (debug):
			print('Starting Zielonka')

		d = np.array(colorList)[nodeMask].max()
		i = d % 2
		j = 1 - i

		if (debug):
			print('Max color: {}, i: {}, j:{}'.format(d,i,j))

		V_0primed = bdd.let(prime, V_0)
		V_1primed = bdd.let(prime, V_1)
		allNodes = V_0primed | V_1primed

		if (debug):
			print('All nodes are: ', getStatesForPrinting(allNodes))

		region = colorInverse(d, nodeMask)
		regionSymbolicStr = applyBooleanOp([createSymbolicString('X', ownerList[nodePosDict[nodeInd]], nodeInd)
											for nodeInd in region], '\/')
		regionNodes = bdd.add_expr(regionSymbolicStr)

		if (debug):
			print('Nodes with color {} in G_0: {}'.format(d, getStatesForPrinting(regionNodes)))

		regionAttractor = attractor(i, regionNodes, V_0, V_1, allNodes, E)

		if (debug):
			print('Attractor of nodes with color {} in G_0: {}'.format(d, getStatesForPrinting(regionAttractor)))

		if(regionAttractor == allNodes):

			if (debug):
				print('Solution is easy. No need to compute G1. {} wins.'.format(i))

			if(i==0):

				return allNodes, bdd.false

			else:

				return bdd.false, allNodes
		else:

			if (debug):
				print('Computing G1.')

			regionAssignments = list(bdd.pick_iter(regionAttractor, care_vars=['X{}'.format(i) for i in range(numVariables)]))
			removeNodes = [assignmentToNodeInd(assignment, primed=True) for assignment in regionAssignments]
			G1_nodeMask = copy.deepcopy(nodeMask)
			for nodeInd in removeNodes:
				G1_nodeMask[nodePosDict[nodeInd]] = False
			removeNodesSymbolicStr = applyBooleanOp([createSymbolicString('x', ownerList[nodePosDict[nodeInd]], nodeInd)
											for nodeInd in removeNodes], '\/')
			removeSet = bdd.add_expr(removeNodesSymbolicStr)
			G1_V0 = V_0 & ~removeSet
			G1_V1 = V_1 & ~removeSet

			if(debug):
				print('Nodes to remove: ', getStatesForPrinting(removeSet, False))
				print('G1_V0 nodes: ', getStatesForPrinting(G1_V0, False))
				print('G1_V1 nodes: ', getStatesForPrinting(G1_V1, False))
				print('Running Zielonka on G1.')

			wr_G1_V0, wr_G1_V1 = zielonka(G1_V0, G1_V1, E, G1_nodeMask, debug)

			if(debug):
				print('Zielonka on G1 completed.')
				print('wr_G1_V0 is: ', getStatesForPrinting(wr_G1_V0))
				print('wr_G1_V1 is: ', getStatesForPrinting(wr_G1_V1))

			if( (j==1) & (wr_G1_V1 == bdd.false)):

				if (debug):
					print('Solution is easy. No need to compute G2. {} wins.'.format(0))

				return allNodes, bdd.false

			elif( (j==0) & (wr_G1_V0 == bdd.false)):

				if (debug):
					print('Solution is easy. No need to compute G2. {} wins.'.format(1))

				return bdd.false, allNodes

			else:

				if (debug):
					print('Computing G2.')

				wr_G1_j = wr_G1_V1 if j==1 else wr_G1_V0
				wr_G1_j_attractor = attractor(j,wr_G1_j,V_0,V_1, allNodes, E)

				regionAssignments = list(bdd.pick_iter(wr_G1_j_attractor, care_vars=['X{}'.format(i) for i in range(numVariables)]))
				removeNodes = [assignmentToNodeInd(assignment, primed=True) for assignment in regionAssignments]
				G2_nodeMask = copy.deepcopy(nodeMask)
				for nodeInd in removeNodes:
					G2_nodeMask[nodePosDict[nodeInd]] = False
				removeNodesSymbolicStr = applyBooleanOp([createSymbolicString('x', ownerList[nodePosDict[nodeInd]], nodeInd)
					 							for nodeInd in removeNodes], '\/')
				removeSet = bdd.add_expr(removeNodesSymbolicStr)
				G2_V0 = V_0 & ~removeSet
				G2_V1 = V_1 & ~removeSet

				if (debug):
					print('Nodes to remove: ', getStatesForPrinting(removeSet, False))
					print('G2_V0 nodes: ', getStatesForPrinting(G2_V0, False))
					print('G2_V1 nodes: ', getStatesForPrinting(G2_V1, False))
					print('Running Zielonka on G2.')

				wr_G2_V0, wr_G2_V1 = zielonka(G2_V0, G2_V1, E, G2_nodeMask, debug)

				if (debug):
					print('Zielonka on G2 completed.')
					print('wr_G2_V0 is: ', getStatesForPrinting(wr_G2_V0))
					print('wr_G2_V1 is: ', getStatesForPrinting(wr_G2_V1))

				if(i==0):

					return wr_G2_V0, allNodes & ~wr_G2_V0

				else:

					return allNodes & ~wr_G2_V1, wr_G2_V1

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
