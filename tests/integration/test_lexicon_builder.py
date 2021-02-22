#!/bin/python3
import unittest
import os
import sys

from touch import touch
from parameterized import parameterized_class

sys.path.insert(0, os.path.join("..", "..", "src"))

import lexicon_builder


# couple de mots similaire: rire amuser
# rire avion


@parameterized_class(
    ("lang", "depth", "word"),
    [
        ("fr", "1", "test"),
        ("en", "1", "test"),
        ("nl", "1", "test"),
        ("de", "1", "test"),
        ("cz", "1", "test"),
    ],
)
class TestLexiconBuilder(unittest.TestCase):

    out_file_txt = "_test.txt"
    out_file_ttl = "_test.ttl"

    def setUp(self):
        touch(self.out_file_txt)
        touch(self.out_file_ttl)
        self.args_list = [
            self.word,
            "--depth",
            self.depth,
            "--format",
            "ttl",
            "--out-file",
            self.out_file_ttl,
            "--lang",
            self.lang,
        ]
        # print(self.args_list)

    def tearDown(self):
        os.remove(self.out_file_txt)
        os.remove(self.out_file_ttl)

    def test_parser(self):
        lexicon_builder.parse_args(self.args_list)

    # def test_assert_graph_is_not_empty(self):
    #     lexicon_builder.main(arguments)


unittest.main()
