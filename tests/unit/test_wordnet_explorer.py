#!/bin/python3
import unittest
import os
import sys

from touch import touch
from parameterized import parameterized_class

sys.path.insert(0, os.path.join("..", ".."))
import lexicons_builder.wordnet_explorer.explorer as exp

sys.path.insert(0, os.path.join("..", "..", "lexicons_builder", "graphs"))
from graphs import Graph


@parameterized_class(
    ("lang", "depth", "word"),
    [
        ("fra", 1, "test"),
        ("eng", 1, "test"),
        ("fra", 2, "test"),
        ("eng", 2, "test"),
    ],
)
class TestExplorer(unittest.TestCase):

    langs = ("eng", "fra")
    words = ("test", "poireau")
    wrong_langs = ("frgg", "enrr", "depp", "nlhh", "itff")
    word_test_fr = "chaussette"
    out_file = "_test"

    def setUp(self):
        self.g = exp.explore_wordnet(self.word, self.lang, self.depth)
        touch(self.out_file)

    def tearDown(self):
        os.remove(self.out_file)

    def test_explore(self):
        for good_lang, word in zip(self.langs, self.words):
            g = exp.explore_wordnet(word, good_lang, 2)

    def test_to_list(self):
        for i in range(5):
            g = exp.explore_wordnet(self.word_test_fr, "fra", i)
            self.assertEqual(len(g.to_list()), len(set(g.to_list())))
            self.assertEqual(g.to_list(), sorted(g.to_list()))

    def test_return_graph(self):
        self.assertIsInstance(exp.explore_wordnet(self.word_test_fr, "fra", 1), Graph)
        self.assertIsInstance(exp.explore_wordnet(self.word_test_fr, "fra", 0), Graph)

    # TESTS ADDED FROM GRAPHS
    def test_to_text_file(self):
        self.g.to_text_file(self.out_file)
        with open(self.out_file) as f:
            words = sorted([line.strip() for line in f if line.strip()])
        self.assertEqual(words, self.g.to_list())

    def test_add_several_root_words(self):
        self.g.add_root_word("root_word_string_1")
        self.g.add_root_word("root_word_string_2")
        self.g.add_root_word("root_word_string_3")
        self.g.to_text_file(self.out_file)
        with open(self.out_file) as f:
            words = sorted(set([line.strip() for line in f if line.strip()]))
        self.assertEqual(words, self.g.to_list())


class TestWOLF(unittest.TestCase):

    words = ("chien", "livre", "rire")
    path_2_wolf = "/home/k/models/wolf-1.0b4.xml"  # change here if needed

    def test_explore(self):
        for word in self.words:
            g = exp.explore_wolf(word, self.path_2_wolf, 2)

    def test_to_list(self):
        for word in self.words:
            for i in range(3):
                g = exp.explore_wolf(word, self.path_2_wolf, i)
                self.assertEqual(len(g.to_list()), len(set(g.to_list())))
                self.assertEqual(g.to_list(), sorted(g.to_list()))

    def test_return_graph(self):
        for word in self.words:
            self.assertIsInstance(exp.explore_wolf(word, self.path_2_wolf, 1), Graph)
            self.assertIsInstance(exp.explore_wolf(word, self.path_2_wolf, 0), Graph)

    def test_wrong_path(self):
        self.assertRaises(
            FileNotFoundError, exp.explore_wolf, self.words[0], "/wrong/path/2/wolf", 42
        )


unittest.main()
