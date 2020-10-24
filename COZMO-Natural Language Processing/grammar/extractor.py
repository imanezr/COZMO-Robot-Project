import nltk

from nltk import grammar, load_parser, ApplicationExpression
from nltk.sem.logic import AndExpression

class ClueExtractor:

    def __init__(self):
        grammar_path = "./grammar/clueGrammar.fcfg"
        with open(grammar_path, "r") as grammar_file:
            self.grammar_text = grammar_file.read()
        self.my_grammar = grammar.FeatureGrammar.fromstring(self.grammar_text)
        self.parser = nltk.FeatureEarleyChartParser(self.my_grammar)
        self.ep = load_parser(grammar_path)

    def get_labels(self, sentence):
        tokens = sentence.replace('.', ' ').split()
        tree = self.parser.parse(tokens)
        facts = []
        for part in tree:
            facts.append(part.label()['SEM'])
            # print(part.label()['SEM'])

        return self.build_dict(facts)

    def build_dict(self, facts):
        dict = {}
        for fact in facts:
            if isinstance(fact, ApplicationExpression):
                dict[fact.pred] = fact.args
            elif isinstance(fact, AndExpression):
                if str(fact.first.pred) == "Interval" and str(fact.second.pred) == "access":
                    dict['Access'] = [fact.second.args[1],
                                      fact.second.args[0],
                                      fact.first.args[0],
                                      fact.first.args[1]]
                else:
                    dict[fact.first.pred] = fact.first.args
                    dict[fact.second.pred] = fact.second.args
        return dict


    def add_facts(self, facts):
        for key, values in facts.items():
            key_str = str(key)
            values_str = [str(value) for value in values]
            if key_str == "cause":
                print(values_str)
            elif key_str == "WeaponRoom":
                print(values_str)
            elif key_str == "MurderRoom":
                print(values_str)
            elif key_str == "Weapon":
                print(values_str)
            elif key_str == "WeaponTime":
                print(values_str)
            elif key_str == "MurderTime":
                print(values_str)


if __name__ == "__main__":
    extractor = ClueExtractor()

    a = extractor.get_labels("Colonel Mustard  killed Mr. Black.")
    extractor.add_facts(a)

    a = extractor.get_labels("Mr.Black was Shot.")
    extractor.add_facts(a)

    a = extractor.get_labels("Mr.Black  was_in the Kitchen between seven and eleven.")
    extractor.add_facts(a)

    a = extractor.get_labels("Mr.Black died_in the Study")
    extractor.add_facts(a)

    a = extractor.get_labels("A Revolver was_found_in the Study.")
    extractor.add_facts(a)

    a = extractor.get_labels("Colonel Mustard was_in the Study between eight and ten.")
    extractor.add_facts(a)
