1Install antlr 4.8 jar file in usr local lib and export class parth using  following commands

$ cd /usr/local/lib
$ wget https://www.antlr.org/download/antlr-4.8-complete.jar
$ export CLASSPATH=".:/usr/local/lib/antlr-4.8-complete.jar:$CLASSPATH"
$ alias antlr4='java -jar /usr/local/lib/antlr-4.8-complete.jar'

2.In the folder where grammar file is stored, install python3 runtime 

$pip install antlr4-python3-runtime

3.Run Antlr to generate the parser

antlr4 -Dlanguage=Python3 parity_game.g4

4.To run python code

$ python3 parity_game.py

