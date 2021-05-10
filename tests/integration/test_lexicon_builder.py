#!/bin/python3
import unittest
import os
import sys

import rdflib
from touch import touch
from parameterized import parameterized_class

sys.path.insert(0, os.path.join("..", ".."))

import lexicons_builder


# couple de mots similaire: rire amuser
# rire avion


@parameterized_class(
    ("lang", "depth", "word", "format"),
    [
        ("fr", "1", "test", "ttl"),
        ("en", "1", "test", "ttl"),
        # ("nl", "1", "test", "ttl"),
        # ("de", "1", "test", "ttl"),
        # ("cz", "1", "test", "ttl"),
    ],
)
class TestLexiconBuilder(unittest.TestCase):

    out_file_txt = "_test.txt"
    out_file_ttl = "_test.ttl"
    # print(self.lang)

    @classmethod
    def setUpClass(cls):

        cls.args = {
            "word": cls.word,
            "depth": int(cls.depth),
            "format": "ttl",
            "outfile": cls.out_file_ttl,
            "lang": cls.lang,
        }

        cls.graph = lexicons_builder.build_lexicon(
            words=[cls.args["word"]],
            lang=cls.args["lang"],
            depth=cls.args["depth"],
            nlp_model_paths=None,
            wolf_path=None,
            wordnet=False,
            web=True,
        )

    # def test_args(self):
    #     print(self.args_list)

    # def setUp(self):
    #     touch(self.out_file_txt)
    #     touch(self.out_file_ttl)
    #     self.args_list = [
    #         self.word,
    #         "--depth",
    #         self.depth,
    #         "--format",
    #         "ttl",
    #         "--out-file",
    #         self.out_file_ttl,
    #         "--lang",
    #         self.lang,
    #     ]
    #     # print(self.args_list)
    #     self.graph = lexicon_builder.main(self.args_list)

    # def tearDown(self):
    #     os.remove(self.out_file_txt)
    #     os.remove(self.out_file_ttl)

    # def test_parser(self):
    #     lexicon_builder.parse_args(self.args_list)

    def test___contains(self):
        self.assertTrue("test" in self.graph)
        self.assertFalse("notest" in self.graph)

    def test_str(self):
        self.assertIsInstance(self.graph.to_str(), str)
        g2 = rdflib.Graph()
        g2.parse(data=str(self.graph), format="ttl")

    def test___len__(self):
        # we want more than 10 words
        self.assertTrue(len(self.graph) > 10)

    # def test_to_text_file(self):
    #     self.graph.parse(self.graph_test_path, format="ttl")
    #     self.g.to_text_file(self.out_file)
    #     with open(self.out_file) as f:
    #         words = sorted([line.strip() for line in f if line.strip()])
    #     self.assertEqual(words, self.g.to_list())

    # def test_good_words(self):
    #     self.graph.parse(self.graph_test_path, format="ttl")
    #     for word in self.g.to_list():
    #         self.assertTrue(word)  # no empty words
    #         self.assertTrue(unidecode(word.lower().strip()) == word)  # no

    # def test_is_empty(self):
    #     self.assertTrue(self.g.is_empty())
    #     self.assertRaises(ValueError, self.g._set_root_word_attribute)
    #     rw_strings = ["root_word_string_1", "root_word_string_2", "root_word_string_3"]
    #     for w in rw_strings:
    #         self.g.add_root_word(w)
    #         self.assertFalse(self.g.is_empty())
    #     self.assertTrue(rw_strings == self.g.to_list())

    # def test_add_several_root_words(self):
    #     self.g.add_root_word("root_word_string_1")
    #     self.g.add_root_word("root_word_string_2")
    #     self.g.add_root_word("root_word_string_3")
    #     self.g.to_text_file(self.out_file)
    #     with open(self.out_file) as f:
    #         words = sorted([line.strip() for line in f if line.strip()])
    #     self.assertEqual(words, self.g.to_list())

    # def test_add_several_root_words_with_previous_graph(self):
    #     self.g.parse(self.graph_test_path, format="ttl")
    #     self.g.add_root_word("root_word_string_1")
    #     self.g.add_root_word("root_word_string_2")
    #     self.g.add_root_word("root_word_string_3")

    #     self.g.to_text_file(self.out_file)
    #     with open(self.out_file) as f:
    #         words = sorted([line.strip() for line in f if line.strip()])
    #     self.assertEqual(words, self.g.to_list())
    #     self.test_list_is_sorted()

    def test_list_is_sorted(self):
        self.assertTrue(sorted(set(self.graph.to_list())) == self.graph.to_list())


unittest.main()
