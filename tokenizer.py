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
        return _text

    def split_with_tokenizer(self, text):
        tokens = self.nltk_sentenizer.tokenize(text)
        return tokens

    def get_concat_rules(self):
        prev_word_patterns = '|'.join(('з\.', 'двухф\.', 'отриц\.'))
        # TODO: здесь надо написать паттерны для предыдущего предложения
        concat_rules_prev = (
            [r'[\W]з\.$|^З\.$', r'\W+двухф\.$|^Двухф\.$', r'\W+отриц\.$|^Отриц\.$', r'\W+двухфаз\.$|^Двухфаз\.$', r'\W+отр\.$|^Отр\.$']  # r'\W+%\.$|^%\.$', вместо % сокращенное слово
        )

        begin_exceptions = '|'.join(('Tbc', 'Твс', '[\-–]'))
        # TODO: здесь надо написать паттерны соединения последющего предложения
        concat_rules_post = (
            [r'^[\--]', r'^Tbc', r'^Твс']
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
            [r'\n']
        )
        split_rules = '|'.join(split_rules)
        return split_rules

    def split_after_concatization(self, tokens):
        split_rules = self.get_split_rules()
        _tokens = chain.from_iterable([re.split(fr"{split_rules}", token)
                                       for token in tokens])
        _tokens = list(filter(None, _tokens))
        return _tokens

    def tokenize(self, text: str) -> Iterator[str]:
        _text = self.split_dot(text)
        tokens = self.split_with_tokenizer(_text)
        tokens = self.concat(tokens)
        tokens = self.split_after_concatization(tokens)
        return tokens


if __name__ == "__main__":
    text = """Жалобы на  давящие, сжимающие боли за грудиной усиливающиеся в ходьбе до 150 м ,которые купируютя покоем или приемом нитроспрея в течение 12мин., перебои  в  работе сердца, повышение АД до 180/100 мм ртст с диффузной гол.болью при опт АД 130\80 мм рт мт.Ухудшение самочувствия  в течение 3 мес - усилились жалобы со стороны сердца., снижение ТФН, нестабильность АД, малая эффективность амб.терапии. Не обследовалась. Амб принимает эналапил. Клиника ИБС около 3-ех лет, Гипертония около 5-ти лет.

Наследственность  отягощена по ИБС  Перенесенные заболевания:- МКБ, ДОА коленных суставов.

Аллергологический анамнез: Аллергия нет
Эпидемиологический анамнез: В контакте с инфекционным больным не был. Туберкулез, вирусный гепатит, венерические болезни отрицает.   Диарея: нет.
Онкологический анамнез: Онкологические заболевания отрицает.
Гемотрансфузионный анамнез: Гемотрасфузии отрицает.
Акушерский анамнез: Менопауза
Наследственный анамнез: Наследственность не отягощена"""
    tokenizer = Tokenizer()
    result = tokenizer.tokenize(text)
    print(result)
