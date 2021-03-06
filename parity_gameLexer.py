# Generated from parity_game.g4 by ANTLR 4.8
from antlr4 import *
from io import StringIO
from typing.io import TextIO
import sys



def serializedATN():
    with StringIO() as buf:
        buf.write("\3\u608b\ua72a\u8133\ub9ed\u417c\u3be7\u7786\u5964\2\t")
        buf.write("\63\b\1\4\2\t\2\4\3\t\3\4\4\t\4\4\5\t\5\4\6\t\6\4\7\t")
        buf.write("\7\4\b\t\b\3\2\3\2\3\2\3\2\3\2\3\2\3\2\3\3\3\3\3\4\3\4")
        buf.write("\3\5\6\5\36\n\5\r\5\16\5\37\3\6\3\6\7\6$\n\6\f\6\16\6")
        buf.write("\'\13\6\3\6\3\6\3\7\3\7\3\b\6\b.\n\b\r\b\16\b/\3\b\3\b")
        buf.write("\3%\2\t\3\3\5\4\7\5\t\6\13\7\r\b\17\t\3\2\5\3\2\62;\3")
        buf.write("\2\62\63\5\2\13\f\17\17\"\"\2\65\2\3\3\2\2\2\2\5\3\2\2")
        buf.write("\2\2\7\3\2\2\2\2\t\3\2\2\2\2\13\3\2\2\2\2\r\3\2\2\2\2")
        buf.write("\17\3\2\2\2\3\21\3\2\2\2\5\30\3\2\2\2\7\32\3\2\2\2\t\35")
        buf.write("\3\2\2\2\13!\3\2\2\2\r*\3\2\2\2\17-\3\2\2\2\21\22\7r\2")
        buf.write("\2\22\23\7c\2\2\23\24\7t\2\2\24\25\7k\2\2\25\26\7v\2\2")
        buf.write("\26\27\7{\2\2\27\4\3\2\2\2\30\31\7=\2\2\31\6\3\2\2\2\32")
        buf.write("\33\7.\2\2\33\b\3\2\2\2\34\36\t\2\2\2\35\34\3\2\2\2\36")
        buf.write("\37\3\2\2\2\37\35\3\2\2\2\37 \3\2\2\2 \n\3\2\2\2!%\7$")
        buf.write("\2\2\"$\13\2\2\2#\"\3\2\2\2$\'\3\2\2\2%&\3\2\2\2%#\3\2")
        buf.write("\2\2&(\3\2\2\2\'%\3\2\2\2()\7$\2\2)\f\3\2\2\2*+\t\3\2")
        buf.write("\2+\16\3\2\2\2,.\t\4\2\2-,\3\2\2\2./\3\2\2\2/-\3\2\2\2")
        buf.write("/\60\3\2\2\2\60\61\3\2\2\2\61\62\b\b\2\2\62\20\3\2\2\2")
        buf.write("\6\2\37%/\3\b\2\2")
        return buf.getvalue()


class parity_gameLexer(Lexer):

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    T__0 = 1
    T__1 = 2
    T__2 = 3
    NUMBER = 4
    NAME = 5
    BOOL = 6
    WS = 7

    channelNames = [ u"DEFAULT_TOKEN_CHANNEL", u"HIDDEN" ]

    modeNames = [ "DEFAULT_MODE" ]

    literalNames = [ "<INVALID>",
            "'parity'", "';'", "','" ]

    symbolicNames = [ "<INVALID>",
            "NUMBER", "NAME", "BOOL", "WS" ]

    ruleNames = [ "T__0", "T__1", "T__2", "NUMBER", "NAME", "BOOL", "WS" ]

    grammarFileName = "parity_game.g4"

    def __init__(self, input=None, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.8")
        self._interp = LexerATNSimulator(self, self.atn, self.decisionsToDFA, PredictionContextCache())
        self._actions = None
        self._predicates = None


