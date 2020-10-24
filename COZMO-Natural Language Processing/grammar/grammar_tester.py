import nltk

from nltk import grammar, load_parser

clue_grammar = "clueGrammar.fcfg"
clue_scenario = 'working_scenario'

with open(clue_grammar, "r") as grammar_file:
    grammarText = grammar_file.read()

myGrammar = grammar.FeatureGrammar.fromstring(grammarText)
parser = nltk.FeatureEarleyChartParser(myGrammar)

ep = load_parser(clue_grammar)
facts = []
with open(clue_scenario) as scenario:
    for sentence in scenario:
        tokens = sentence.replace('.', ' ').split()
        trees = parser.parse(tokens)

        # for tree in ep.parse(tokens):
        #     tree.draw()
        for part in trees:
            facts.append(part.label()['SEM'])
            print(part.label()['SEM'])
