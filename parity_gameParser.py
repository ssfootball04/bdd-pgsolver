# Generated from parity_game.g4 by ANTLR 4.8
# encoding: utf-8
from antlr4 import *
from io import StringIO
import sys
if sys.version_info[1] > 5:
	from typing import TextIO
else:
	from typing.io import TextIO


def serializedATN():
    with StringIO() as buf:
        buf.write("\3\u608b\ua72a\u8133\ub9ed\u417c\u3be7\u7786\u5964\3\t")
        buf.write(".\4\2\t\2\4\3\t\3\4\4\t\4\4\5\t\5\4\6\t\6\4\7\t\7\3\2")
        buf.write("\3\2\3\2\3\2\6\2\23\n\2\r\2\16\2\24\3\3\3\3\3\3\3\3\3")
        buf.write("\3\5\3\34\n\3\3\3\3\3\3\4\3\4\3\5\3\5\3\6\3\6\3\7\3\7")
        buf.write("\3\7\7\7)\n\7\f\7\16\7,\13\7\3\7\2\2\b\2\4\6\b\n\f\2\2")
        buf.write("\2*\2\16\3\2\2\2\4\26\3\2\2\2\6\37\3\2\2\2\b!\3\2\2\2")
        buf.write("\n#\3\2\2\2\f%\3\2\2\2\16\17\7\3\2\2\17\20\5\6\4\2\20")
        buf.write("\22\7\4\2\2\21\23\5\4\3\2\22\21\3\2\2\2\23\24\3\2\2\2")
        buf.write("\24\22\3\2\2\2\24\25\3\2\2\2\25\3\3\2\2\2\26\27\5\6\4")
        buf.write("\2\27\30\5\b\5\2\30\31\5\n\6\2\31\33\5\f\7\2\32\34\7\7")
        buf.write("\2\2\33\32\3\2\2\2\33\34\3\2\2\2\34\35\3\2\2\2\35\36\7")
        buf.write("\4\2\2\36\5\3\2\2\2\37 \7\6\2\2 \7\3\2\2\2!\"\7\6\2\2")
        buf.write("\"\t\3\2\2\2#$\7\6\2\2$\13\3\2\2\2%*\5\6\4\2&\'\7\5\2")
        buf.write("\2\')\5\6\4\2(&\3\2\2\2),\3\2\2\2*(\3\2\2\2*+\3\2\2\2")
        buf.write("+\r\3\2\2\2,*\3\2\2\2\5\24\33*")
        return buf.getvalue()


class parity_gameParser ( Parser ):

    grammarFileName = "parity_game.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ "<INVALID>", "'parity'", "';'", "','" ]

    symbolicNames = [ "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "NUMBER", "NAME", "BOOL", "WS" ]

    RULE_parity_game = 0
    RULE_node_spec = 1
    RULE_identifier = 2
    RULE_parity = 3
    RULE_owner = 4
    RULE_successors = 5

    ruleNames =  [ "parity_game", "node_spec", "identifier", "parity", "owner", 
                   "successors" ]

    EOF = Token.EOF
    T__0=1
    T__1=2
    T__2=3
    NUMBER=4
    NAME=5
    BOOL=6
    WS=7

    def __init__(self, input:TokenStream, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.8")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None




    class Parity_gameContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def identifier(self):
            return self.getTypedRuleContext(parity_gameParser.IdentifierContext,0)


        def node_spec(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(parity_gameParser.Node_specContext)
            else:
                return self.getTypedRuleContext(parity_gameParser.Node_specContext,i)


        def getRuleIndex(self):
            return parity_gameParser.RULE_parity_game

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterParity_game" ):
                listener.enterParity_game(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitParity_game" ):
                listener.exitParity_game(self)




    def parity_game(self):

        localctx = parity_gameParser.Parity_gameContext(self, self._ctx, self.state)
        self.enterRule(localctx, 0, self.RULE_parity_game)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 12
            self.match(parity_gameParser.T__0)
            self.state = 13
            self.identifier()
            self.state = 14
            self.match(parity_gameParser.T__1)
            self.state = 16 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 15
                self.node_spec()
                self.state = 18 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not (_la==parity_gameParser.NUMBER):
                    break

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Node_specContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def identifier(self):
            return self.getTypedRuleContext(parity_gameParser.IdentifierContext,0)


        def parity(self):
            return self.getTypedRuleContext(parity_gameParser.ParityContext,0)


        def owner(self):
            return self.getTypedRuleContext(parity_gameParser.OwnerContext,0)


        def successors(self):
            return self.getTypedRuleContext(parity_gameParser.SuccessorsContext,0)


        def NAME(self):
            return self.getToken(parity_gameParser.NAME, 0)

        def getRuleIndex(self):
            return parity_gameParser.RULE_node_spec

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterNode_spec" ):
                listener.enterNode_spec(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitNode_spec" ):
                listener.exitNode_spec(self)




    def node_spec(self):

        localctx = parity_gameParser.Node_specContext(self, self._ctx, self.state)
        self.enterRule(localctx, 2, self.RULE_node_spec)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 20
            self.identifier()
            self.state = 21
            self.parity()
            self.state = 22
            self.owner()
            self.state = 23
            self.successors()
            self.state = 25
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==parity_gameParser.NAME:
                self.state = 24
                self.match(parity_gameParser.NAME)


            self.state = 27
            self.match(parity_gameParser.T__1)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class IdentifierContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def NUMBER(self):
            return self.getToken(parity_gameParser.NUMBER, 0)

        def getRuleIndex(self):
            return parity_gameParser.RULE_identifier

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterIdentifier" ):
                listener.enterIdentifier(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitIdentifier" ):
                listener.exitIdentifier(self)




    def identifier(self):

        localctx = parity_gameParser.IdentifierContext(self, self._ctx, self.state)
        self.enterRule(localctx, 4, self.RULE_identifier)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 29
            self.match(parity_gameParser.NUMBER)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ParityContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def NUMBER(self):
            return self.getToken(parity_gameParser.NUMBER, 0)

        def getRuleIndex(self):
            return parity_gameParser.RULE_parity

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterParity" ):
                listener.enterParity(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitParity" ):
                listener.exitParity(self)




    def parity(self):

        localctx = parity_gameParser.ParityContext(self, self._ctx, self.state)
        self.enterRule(localctx, 6, self.RULE_parity)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 31
            self.match(parity_gameParser.NUMBER)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class OwnerContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def NUMBER(self):
            return self.getToken(parity_gameParser.NUMBER, 0)

        def getRuleIndex(self):
            return parity_gameParser.RULE_owner

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterOwner" ):
                listener.enterOwner(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitOwner" ):
                listener.exitOwner(self)




    def owner(self):

        localctx = parity_gameParser.OwnerContext(self, self._ctx, self.state)
        self.enterRule(localctx, 8, self.RULE_owner)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 33
            self.match(parity_gameParser.NUMBER)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class SuccessorsContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def identifier(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(parity_gameParser.IdentifierContext)
            else:
                return self.getTypedRuleContext(parity_gameParser.IdentifierContext,i)


        def getRuleIndex(self):
            return parity_gameParser.RULE_successors

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterSuccessors" ):
                listener.enterSuccessors(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitSuccessors" ):
                listener.exitSuccessors(self)




    def successors(self):

        localctx = parity_gameParser.SuccessorsContext(self, self._ctx, self.state)
        self.enterRule(localctx, 10, self.RULE_successors)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 35
            self.identifier()
            self.state = 40
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==parity_gameParser.T__2:
                self.state = 36
                self.match(parity_gameParser.T__2)
                self.state = 37
                self.identifier()
                self.state = 42
                self._errHandler.sync(self)
                _la = self._input.LA(1)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx





