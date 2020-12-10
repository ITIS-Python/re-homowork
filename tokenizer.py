import os
import re
from itertools import chain
from typing import Iterator

import joblib


class Tokenizer:
    def __init__(self) -> None:
        sentenizer_path = os.path.abspath(os.path.join(
            os.path.dirname(__file__),
            "files",
            "sent_tokenizer.joblib",
        ))
        self.nltk_sentenizer = joblib.load(sentenizer_path)

    def split_dot(self, text: str) -> str:
        # TODO: Здесь нужно написать паттерн разделения точки от заглавных букв
        _text = re.sub(r'([а-яё])(\.)([А-ЯЁ])', r'\1. \3', text)        
        return _text
    
    def split_with_tokenizer(self, text):
        tokens = self.nltk_sentenizer.tokenize(text)
        return tokens

    def get_concat_rules(self):
        prev_word_patterns = '|'.join(('з\.$', 'двухф\.$', 'отриц\.$','Хрон\.$','ч\$',
                                       'ассоцир\.$','стац\.$','вир\.$','H\.$',
                                       'п\.к\.$','хрон\.$'))
        #twprev_word_patterns = '|'.join(('род\.$', 'ор\.$'))
        # TODO: здесь надо написать паттерны для предыдущего предложения
        #print(prev_word_patterns)
        concat_rules_prev = [r'{0}'.format(prev_word_patterns)]

        begin_exceptions = '|'.join(('^Tbc', '^Твс', '^[\-–]'))
        # TODO: здесь надо написать паттерны соединения последющего предложения
        concat_rules_post = [r'{0}'.format(begin_exceptions)]
            # your code here
            
        
        return concat_rules_prev, concat_rules_post

    def concat(self, tokens):
        _tokens = []
        
        concat_rules_prev, concat_rules_post = self.get_concat_rules()

        for token in tokens:
            token = [token.strip()]
            #print(tokens)
            #g = input()
            if _tokens:
                #print(_tokens[-1])
                is_concated = False
                
                for concat_rule in concat_rules_prev:
                    #print(concat_rule)
                    if re.search(concat_rule, _tokens[-1]):
                        #print(_tokens)
                        #print(token)
                        _tokens[-1] += f" {token.pop(0)}"
                        #print(token.pop(0))
                        #g = input()
                        is_concated = True
                        #print(is_concated)
                        break
                #print('ggf')
                #print(_tokens)
                #print(token)
                #g = input()
                if not is_concated:
                    for concat_rule in concat_rules_post:
                        if re.search(concat_rule, token[0]):
                            _tokens[-1] += f" {token.pop(0)}"
                            #print(_tokens)
                            #print(token)
                            #g = input()
                            break
            _tokens.extend(token)            
            #print(_tokens)
        #print(_tokens)
        #g = input()
        return _tokens

    def get_split_rules(self):
        # TODO: здесь нужно написать паттерны разделения предложений
        split_rules = ('\n([^-]\s+)','([а-яё]\n[А-ЯЁ])')
            # your code here       
        split_rules = '|'.join(split_rules)
        print()
        return split_rules

    def split_after_concatization(self, tokens):
        split_rules = self.get_split_rules()
        _tokens = chain.from_iterable([re.split(fr"{split_rules}", token)
                                       for token in tokens])
        #print(tokens)
        _tokens = list(filter(None, _tokens))
        #print(_tokens)
        #g = input()
        return _tokens

    def tokenize(self, text: str) -> Iterator[str]:
        _text = self.split_dot(text)
        tokens = self.split_with_tokenizer(_text)
        tokens = self.concat(tokens)
        tokens = self.split_after_concatization(tokens)
        return tokens


if __name__ == "__main__":
    filename = 'D://For_python/PROGRAMS_ON_BLOK/dz_29_10_20/re-homowork-master/files/texts/01.txt'
    with open(filename, "r", encoding='utf-8') as file:
        text = file.read()

   
    tokenizer = Tokenizer()
    result = tokenizer.tokenize(text)
    print(result)
