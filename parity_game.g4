grammar parity_game;

parity_game:
    'parity' identifier ';' (node_spec)+
    ;

node_spec:
    identifier parity owner successors (NAME)? ';'
    ;

identifier:
     NUMBER
     ;

parity:
     NUMBER
     ;

owner:
     NUMBER
     ;

NUMBER:
    [0-9]+
    ;

NAME:
    '"' (.)*? '"'
    ;

BOOL:
    [0-1]
    ;

successors:
    identifier (',' identifier)*
    ;

WS:
    [ \t\r\n]+ -> skip
    ;

