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
        ("fra", 2, "test"),
        ("eng", 1, "test"),
    ],
)
class TestExplorer(unittest.TestCase):

    wrong_langs = ("frgg", "enrr", "depp", "nlhh", "itff")
    word_test_fr = "chaussette"
    word_test_en = "make"
    out_file = "_test"
    out_file_xlsx = "_test.xlsx"

    @classmethod
    def setUpClass(cls):
        cls.g = exp.explore_wordnet(cls.word, cls.lang, cls.depth)

    def setUp(self):
        touch(self.out_file)
        touch(self.out_file_xlsx)

    def tearDown(self):
        os.remove(self.out_file)
        os.remove(self.out_file_xlsx)

    def test_to_list(self):
        for i in range(0, 1):
            g = exp.explore_wordnet(self.word_test_en, "eng", i)
            self.assertEqual(len(g.to_list()), len(set(g.to_list())))
            self.assertEqual(g.to_list(), sorted(g.to_list()))
            if i:
                self.assertTrue(len(g.to_list()) > 2)

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

    @unittest.skip("skipping because the xlsx should be tested in integration")
    def test_to_xlsx(self):
        self.g.to_xlsx_file(self.out_file_xlsx)


class TestWOLF(unittest.TestCase):

    words = ("chien",)  # "livre", "rire")
    path_2_wolf = "/home/k/models/wolf-1.0b4.xml"  # change here if needed
    fake_word = "adsfadsfasdfdsf"

    def test_explore(self):
        for word in self.words:
            g = exp.explore_wolf(word, self.path_2_wolf, 2)
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

    def test_fake_word(self):
        self.assertTrue(
            exp.explore_wolf(self.fake_word, self.path_2_wolf, 42).is_empty()
        )


unittest.main()
