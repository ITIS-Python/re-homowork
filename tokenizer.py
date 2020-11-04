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
        _text = re.sub(r'\.\s*([A-ZА-Я])', r'. \1', text)
        _text = re.sub(r'([^:])\n+[\s\n]*', r'\1. ', _text)
        _text = re.sub(r'\.\.', r'.', _text)
        _text = re.sub(r':\s*\.', ':', _text)
        print(_text, '\n')
        return _text

    def split_with_tokenizer(self, text):
        tokens = self.nltk_sentenizer.tokenize(text)
        return tokens

    def get_concat_rules(self):
        prev_word_patterns = '|'.join(('з\.', 'двухф\.', 'отриц\.'))
        # TODO: здесь надо написать паттерны для предыдущего предложения
        concat_rules_prev = (
            [r'[\W]з\.$|^З\.$', r'\W+двухф\.$|^Двухф\.$', r'\W+отриц\.$|^Отриц\.$', r'\W+двухфаз\.$|^Двухфаз\.$']  # r'\W+%\.$|^%\.$', вместо % сокращенное слово
        )

        begin_exceptions = '|'.join(('Tbc', 'Твс', '[\-–]'))
        # TODO: здесь надо написать паттерны соединения последющего предложения
        concat_rules_post = (
            [r'^[а-я]', r'^Tbc', r'^Твс']
        )
        return concat_rules_prev, concat_rules_post

    def concat(self, tokens):
        _tokens = []

        concat_rules_prev, concat_rules_post = self.get_concat_rules()

        for token in tokens:
            token = [token.strip()]
            if _tokens:
                is_concated = False

                for concat_rule in concat_rules_prev:
                    if re.search(concat_rule, _tokens[-1]):
                        print('rule:', concat_rule, '\ntoken:', _tokens[-1], '\nadded token:', token[0], '\n')
                        _tokens[-1] += f" {token.pop(0)}"
                        is_concated = True
                        break

                if not is_concated:
                    for concat_rule in concat_rules_post:
                        if re.search(concat_rule, token[0]):
                            _tokens[-1] += f" {token.pop(0)}"
                            break
            _tokens.extend(token)
        return _tokens

    def get_split_rules(self):
        # TODO: здесь нужно написать паттерны разделения предложений
        split_rules = (
            []
        )
        split_rules = '|'.join(split_rules)
        return split_rules

    def split_after_concatization(self, tokens):
        split_rules = self.get_split_rules()
        _tokens = chain.from_iterable([re.split(fr"{split_rules}", token)
                                       for token in tokens])
        _tokens = list(filter(None, tokens))
        return _tokens

    def tokenize(self, text: str) -> Iterator[str]:
        _text = self.split_dot(text)
        tokens = self.split_with_tokenizer(_text)
        tokens = self.concat(tokens)
        tokens = self.split_after_concatization(tokens)
        return tokens


if __name__ == "__main__":
    text = """Жалобы на
-  давящие боли за грудиной при ходьбе на 100м, без иррадиации, купирующие нитратами от 0-2 доз/сутки
- приступы сердцебиения с перебоями в работе сердца
- Контроля АД на амбулаторном этапе нет
- Общая слабость, повышенная утомляемость

Счтает себя с апреля 2018г, когда впервые появились вышеуказанные жалобы. До этого к врачам не обращался. С клиникой нестабильной стенокардии обследован в Ульяновской обласной больнице. После выписке направлен на плановую КАГ.  
Амбулаторно принимал мертенил,АСК,клопидогрель (Россия- 2 недели) , НГ

 Перенесенные заболевания: Туберкулез:  нет.  Вирусный гепатит: нет. Венерические заболевания: нет.
Условия жизни: удовлетворительно 
Аллергологический анамнез: Аллергия нет
Эпидемиологический анамнез: В контакте с инфекционным больным не был. Туберкулез, вирусный гепатит, венерические болезни отрицает.   Диарея: нет.
Онкологический анамнез: Онкологические заболевания отрицает.
Гемотрансфузионный анамнез: Гемотрасфузии отрицает.
Наследственный анамнез: Наследственность не отягощена"""
    tokenizer = Tokenizer()
    result = tokenizer.tokenize(text)
    print(result)
