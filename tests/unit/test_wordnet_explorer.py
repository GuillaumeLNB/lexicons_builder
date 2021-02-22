#!/bin/python3
import unittest
import os
import sys

sys.path.insert(0, os.path.join("..", "..", "src"))
sys.path.insert(1, os.path.join("..", "..", "src", "wordnet_explorer"))

# from rdflib import Graph
# logging.getLogger("transformers").setLevel(logging.CRITICAL + 1)

import wordnet_explorer.explorer as exp

sys.path.insert(0, os.path.join("..", "..", "src", "graphs"))
from graphs import Graph


class TestExplorer(unittest.TestCase):

    langs = ("eng", "fra")
    words = ("test", "poireau")
    wrong_langs = ("fr", "en", "de", "nl", "it")
    word_test_fr = "chaussette"

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_explore(self):
        for good_lang, word in zip(self.langs, self.words):
            g = exp.explore_wordnet(word, good_lang, 2)

    def test_wrong_languages(self):
        for wl in self.wrong_langs:
            self.assertRaises(ValueError, exp.explore_wordnet, self.word_test_fr, wl)

    def test_to_list(self):
        for i in range(5):
            g = exp.explore_wordnet(self.word_test_fr, "fra", i)
            self.assertEqual(len(g.to_list()), len(set(g.to_list())))
            self.assertEqual(g.to_list(), sorted(g.to_list()))

    def test_return_graph(self):
        self.assertIsInstance(exp.explore_wordnet(self.word_test_fr, "fra", 1), Graph)
        self.assertIsInstance(exp.explore_wordnet(self.word_test_fr, "fra", 0), Graph)


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
