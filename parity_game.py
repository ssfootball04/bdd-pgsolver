import sys
from antlr4 import *
from antlr4.tree.Trees import Trees
from parity_gameLexer import parity_gameLexer
from parity_gameParser import parity_gameParser
from dd import autoref as _bdd
import numpy as np
import copy
import argparse
import sys
from pprint import pprint

sys.setrecursionlimit(3500)


def main(argv):

    parser = argparse.ArgumentParser()
    parser.add_argument('--game_path', type=str, default=None, help='path to game specification')
    parser.add_argument('--algorithm', type=str, default='zielonka', help='zielonka | QPZ')
    opt = parser.parse_args()

    print("\n==================Options=================")
    pprint(vars(opt), indent=4)
    print("==========================================\n")

    # input_stream = StdinStream()
    input_stream = FileStream(opt.game_path)
    lexer = parity_gameLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = parity_gameParser(stream)
    tree = parser.parity_game()

    ##########################################################
    ###### extract game graph from the parse tree		######
    ##########################################################

    children = Trees.getChildren(tree)
    maxNodeInd = int(Trees.getNodeText(children[1].children[0]))
    numActualNodes = len(children) - 3  # subtracting 3 for the first three tokens

    nodeList, colorList, ownerList, nodeSuccList = [], [], [], []
    nodePosDict = {}  # required to lookup color, owner for a given nodeInd
    colorDict = {}  # required to lookup color inverse

    for i in range(numActualNodes):

        gameNode = children[i + 3]

        nodeInd = int(Trees.getNodeText(gameNode.children[0].children[0]))
        nodeColor = int(Trees.getNodeText(gameNode.children[1].children[0]))
        nodeOwner = bool(int(Trees.getNodeText(gameNode.children[2].children[0])))

        successorList = gameNode.children[3].children
        numSuccessors, nodeSuccessors = (len(successorList) + 1) // 2, []  # compensating for ',' tokens
        for j in range(numSuccessors):
            nodeSuccessors.append(int(Trees.getNodeText(successorList[2 * j].children[0])))

        nodeList.append(nodeInd)
        nodePosDict[nodeInd] = i
        colorList.append(nodeColor)
        if (nodeColor in colorDict):
            colorDict[nodeColor] = colorDict[nodeColor] + [nodeInd]
        else:
            colorDict[nodeColor] = [nodeInd]
        ownerList.append(nodeOwner)
        nodeSuccList.append(nodeSuccessors)

    ##########################################################
    ###### create BDD representation of the game 		######
    ##########################################################

    numVariables = int(
        np.ceil(np.log(numActualNodes) / np.log(2))) + 1  # 1 variable to encode the player and rest to encode vertices
    variableList = ['x{}'.format(i) for i in range(numVariables)] \
                   + ['X{}'.format(i) for i in range(numVariables)]  # variables corresponding to current and next state

    ###################################
    ####     helper fns 	  	  #####
    ###################################

    # maps a node index to its binary encoding
    def createSymbolicString(varType, owner, nodeInd):

        nodeStr = bin(nodeInd)[2:].zfill(numVariables - 1)
        symbolicStr = '{}0'.format(varType) if owner else '~{}0'.format(varType)
        for i in range(numVariables - 1):
            symbolicStr += ' /\ {}{}'.format(varType, i + 1) if bool(int(nodeStr[i])) else ' /\ ~{}{}'.format(varType,
                                                                                                              i + 1)
        return symbolicStr

    # applies a boolean op to a list of formula strings
    def applyBooleanOp(listFormulaStrings, op):
        numFormulas = len(listFormulaStrings)

        if (numFormulas == 0):
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
        if (len(statesStr) != 1):
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
        edges.append(applyBooleanOp([nodeSymbolicStr, applyBooleanOp(successors, '\/')], '/\\'))
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

    def attractor(player, region, V_0, V_1, V, E):

        reachStates = region
        V_player = V_1 if player else V_0
        V_opponent = V_0 if player else V_1

        previousAttractor = bdd.false
        currentAttractor = reachStates
        while (previousAttractor != currentAttractor):  # fpi

            previousAttractor = currentAttractor

            previousStates_player = (V_player & bdd.exist(['X{}'.format(i) for i in range(numVariables)], E & currentAttractor))
            previousStates_opponent = (V_opponent & ~bdd.exist(['X{}'.format(i) for i in range(numVariables)],
                                                               E & (~currentAttractor & V)))

            previousStates = previousStates_player | previousStates_opponent  # compute previous states
            previousStatesPrimed = bdd.let(prime, previousStates)  # prime previous states
            currentAttractor = previousStatesPrimed | currentAttractor  # take union of newfoundstates and previousAttractor

        return currentAttractor

    ###################################
    ####     setminus	op 	  	  #####
    ###################################

    def setminus(region, V_0, V_1, nodeMask):

        if (region == bdd.false):
            return V_0, V_1, nodeMask

        # calculate new node mask
        regionAssignments = list(bdd.pick_iter(region, care_vars=['X{}'.format(i) for i in range(numVariables)]))
        removeNodes = [assignmentToNodeInd(assignment, primed=True) for assignment in regionAssignments]
        new_nodeMask = copy.deepcopy(nodeMask)
        for nodeInd in removeNodes:
            new_nodeMask[nodePosDict[nodeInd]] = False

        removeNodesSymbolicStr = applyBooleanOp([createSymbolicString('x', ownerList[nodePosDict[nodeInd]], nodeInd)
												 for nodeInd in removeNodes], '\/')
        removeSet = bdd.add_expr(removeNodesSymbolicStr)

        new_V0 = V_0 & ~removeSet
        new_V1 = V_1 & ~removeSet

        return new_V0, new_V1, new_nodeMask

    ###################################
    ####     color inverse 	  	  #####
    ###################################

    # find set of nodes of a given color in the graph
    def colorInverse(color, nodeMask):

        region = copy.deepcopy(colorDict[color])
        removeSet = []
        for nodeInd in region:
            if (not nodeMask[nodePosDict[nodeInd]]):
                removeSet.append(nodeInd)
        for nodeInd in removeSet:
            region.remove(nodeInd)
        return region

    ###################################
    ####  zielonka's algorithm    #####
    ###################################

    def zielonka(V_0, V_1, E, nodeMask, debug=False):

        if ((V_0 == bdd.false) & (V_1 == bdd.false)):
            return bdd.false, bdd.false

        V_0primed = bdd.let(prime, V_0)
        V_1primed = bdd.let(prime, V_1)
        V = V_0primed | V_1primed

        d = np.array(colorList)[nodeMask].max()
        i = d % 2
        j = 1 - i

        colorSet = colorInverse(d, nodeMask)
        colorSetSymbolicStr = applyBooleanOp([createSymbolicString('X', ownerList[nodePosDict[nodeInd]], nodeInd)
                                              for nodeInd in colorSet], '\/')
        colorSetNodes = bdd.add_expr(colorSetSymbolicStr)
        colorSetAttractor = attractor(i, colorSetNodes, V_0, V_1, V, E)

        if (colorSetAttractor == V):

            if (i == 0):
                return V, bdd.false
            else:
                return bdd.false, V

        else:

            G1_V0, G1_V1, G1_nodeMask = setminus(colorSetAttractor, V_0, V_1, nodeMask)
            wr_G1_V0, wr_G1_V1 = zielonka(G1_V0, G1_V1, E, G1_nodeMask, debug)

            if ((j == 1) & (wr_G1_V1 == bdd.false)):

                return V, bdd.false

            elif ((j == 0) & (wr_G1_V0 == bdd.false)):

                return bdd.false, V
            else:

                wr_G1_j = wr_G1_V1 if j == 1 else wr_G1_V0
                wr_G1_j_attractor = attractor(j, wr_G1_j, V_0, V_1, V, E)

                G2_V0, G2_V1, G2_nodeMask = setminus(wr_G1_j_attractor, V_0, V_1, nodeMask)
                wr_G2_V0, wr_G2_V1 = zielonka(G2_V0, G2_V1, E, G2_nodeMask, debug)

                if (i == 0):
                    return wr_G2_V0, V & ~wr_G2_V0
                else:
                    return V & ~wr_G2_V1, wr_G2_V1

    ###################################
    ####  QPZ algorithm    		  #####
    ###################################

    def QPZ(V_0, V_1, E, nodeMask, p_0, p_1, debug=False):

        if ((V_0 == bdd.false) & (V_1 == bdd.false)):
            return bdd.false, 0                                                # return winning region, Player i

        V_0primed = bdd.let(prime, V_0)
        V_1primed = bdd.let(prime, V_1)
        V = V_0primed | V_1primed

        d = np.array(colorList)[nodeMask].max()
        i = d % 2
        j = 1 - i
        p_j = p_1 if (i == 0) else p_0
        p_0_new = p_0 if (i == 0) else p_0 // 2
        p_1_new = p_1 // 2 if (i == 0) else p_1

        if ((d == 0) or (p_j == 0)):
            return V, 0

        qpz_1, _ = QPZ(V_0, V_1, E, nodeMask, p_0_new, p_1_new)
        wr_j_V0, wr_j_V1, _ = setminus(qpz_1, V_0, V_1, nodeMask)
        wr_j = bdd.let(prime, wr_j_V0) | bdd.let(prime, wr_j_V1)

        A = attractor(j, wr_j, V_0, V_1, V, E)
        G1_V0, G1_V1, G1_nodeMask = setminus(A, V_0, V_1, nodeMask)
        G1_V = bdd.let(prime, G1_V0) | bdd.let(prime, G1_V1)

        colorSet = colorInverse(d, nodeMask)
        colorSetSymbolicStr = applyBooleanOp([createSymbolicString('X', ownerList[nodePosDict[nodeInd]], nodeInd)
                                              for nodeInd in colorSet], '\/')
        colorSetNodes = bdd.add_expr(colorSetSymbolicStr)
        colorSetAttractor = attractor(i, colorSetNodes, V_0, V_1, V, E)

        G2_V0, G2_V1, G2_nodeMask = setminus(colorSetAttractor, G1_V0, G1_V1, G1_nodeMask)

        wr_j_G2, _ = QPZ(G2_V0, G2_V1, E, G2_nodeMask, p_0, p_1)
        A_2 = attractor(j, wr_j_G2, G1_V0, G1_V1, G1_V, E)

        G3_V0, G3_V1, G3_nodeMask = setminus(A_2, G1_V0, G1_V1, G1_nodeMask)

        qpz_G3, _ = QPZ(G3_V0, G3_V1, E, G3_nodeMask, p_0_new, p_1_new)
        wr_j3_V0, wr_j3_V1, wr_j3_nodeMask = setminus(A & A_2 & qpz_G3, V_0, V_1, nodeMask)
        wr_j3 = bdd.let(prime, wr_j3_V0) | bdd.let(prime, wr_j3_V1)

        result_V0, result_V1, _ = setminus(A & A_2 & wr_j3, V_0, V_1, nodeMask)
        result = bdd.let(prime, result_V0) | bdd.let(prime, result_V1)

        return result, i

    if(opt.algorithm == 'zielonka'):

        nodeMask = np.array([True for i in range(numActualNodes)])
        wr_v0, wr_v1 = zielonka(V_0, V_1, E, nodeMask)

        print("Player 0 wins from nodes:")
        statesStr = getStatesForPrinting(wr_v0)
        print(statesStr)

        print("Player 1 wins from nodes:")
        statesStr = getStatesForPrinting(wr_v1)
        print(statesStr)

    elif(opt.algorithm == 'QPZ'):

        nodeMask = np.array([True for i in range(numActualNodes)])
        wr, i = QPZ(V_0, V_1, E, nodeMask, numActualNodes, numActualNodes)

        print("Player {} wins from nodes:".format(i))
        statesStr = getStatesForPrinting(wr)
        print(statesStr)

    else:
        raise Exception('Invalid algorithm. Available options: zielonka | QPZ')

if __name__ == '__main__':
    main(sys.argv)