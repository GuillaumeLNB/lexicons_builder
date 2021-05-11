#!/bin/python3
import unittest
import os
import sys

import rdflib
from touch import touch
from unidecode import unidecode
from parameterized import parameterized_class


sys.path.insert(0, os.path.join("..", "..", "lexicons_builder", "graphs"))

from graphs import Graph

assert (
    int(rdflib.__version__.split(".")[0]) >= 5
), "This test script needs a version 5 or later of rdflib. Yours is {rdflib.__version__}"


@parameterized_class(
    ("graph_test_path",),
    [("../data/dummy_graph.ttl",), ("../data/graph_synonymesCom_dep2_w=rire.ttl",)],
)
class TestGraph(unittest.TestCase):

    txt_out_file = "_.txt"
    xlsx_out_file = "_.xlsx"

    def setUp(self):
        self.g = Graph()
        touch(self.txt_out_file)
        touch(self.xlsx_out_file)

    def tearDown(self):
        # return
        os.remove(self.txt_out_file)
        os.remove(self.xlsx_out_file)

    def test_add_word(self):
        self.g.add_word("test", 5, "synonym", "target_word")

    def test___contains(self):
        self.g.add_word("test", 5, "synonym", "target_word")
        self.assertTrue("test" in self.g)
        self.assertFalse("notest" in self.g)

    def test_str(self):
        self.g.add_word("test", 5, "synonym", "target_word")
        self.assertIsInstance(self.g.to_str(), str)
        g2 = rdflib.Graph()
        g2.parse(data=str(self.g), format="ttl")

    def test_word_in_graph(self):
        self.g.add_word("test", 5, "synonym", "target_word")
        self.assertTrue(self.g.word_in_graph("test"))
        self.assertFalse(self.g.word_in_graph("tfdfdfest"))

    def test_to_text_file(self):
        self.g.parse(self.graph_test_path, format="ttl")
        self.g.to_text_file(self.txt_out_file)
        with open(self.txt_out_file) as f:
            words = sorted([line.strip() for line in f if line.strip()])
        self.assertEqual(words, self.g.to_list())

    def test_good_words(self):
        self.g.parse(self.graph_test_path, format="ttl")
        for word in self.g.to_list():
            self.assertTrue(word)  # no empty words
            self.assertTrue(unidecode(word.lower().strip()) == word)  # no

    def test_is_empty(self):
        self.assertTrue(self.g.is_empty())
        self.assertRaises(AssertionError, self.g._set_root_word_attribute)
        rw_strings = ["root_word_string_1", "root_word_string_2", "root_word_string_3"]
        for w in rw_strings:
            self.g.add_root_word(w)
            self.assertTrue(self.g.is_empty())
        self.assertTrue(rw_strings == self.g.to_list())
        self.g._set_root_word_attribute()
        for w in self.g.root_words:
            self.assertTrue(isinstance(w, str))

    def test_add_several_root_words(self):
        self.g.add_root_word("root_word_string_1")
        self.g.add_root_word("root_word_string_2")
        self.g.add_root_word("root_word_string_3")
        self.g.to_text_file(self.txt_out_file)
        with open(self.txt_out_file) as f:
            words = sorted([line.strip() for line in f if line.strip()])
        self.assertEqual(words, self.g.to_list())

    def test_add_several_root_words_with_previous_graph(self):
        self.g.parse(self.graph_test_path, format="ttl")
        self.g.add_root_word("root_word_string_1")
        self.g.add_root_word("root_word_string_2")
        self.g.add_root_word("root_word_string_3")

        self.g.to_text_file(self.txt_out_file)
        with open(self.txt_out_file) as f:
            words = sorted([line.strip() for line in f if line.strip()])
        self.assertEqual(words, self.g.to_list())
        self.test_list_is_sorted()

    def test_list_is_sorted(self):
        self.assertTrue(sorted(self.g.to_list()) == self.g.to_list())

    def test___len__(self):
        self.assertFalse(len(self.g))
        for i in range(1, 10):
            self.g.add_root_word(f"test_{i}")
            self.assertEqual(len(self.g), i)
        self.g.add_word("test", 5, "synonym", "target_word")
        self.assertEqual(len(self.g), i + 1)

    def test_add_relation(self):
        self.g.add_root_word("root_word_string_1")
        self.g.add_word("test", 1, "synonym", "root_word_string_1")
        self.g.add_word("test", 1, "hyponym", "root_word_string_1")
        self.g.add_word("test", 1, "hypernym", "root_word_string_1")
        self.g.add_word("test", 1, "holonym", "root_word_string_1")
        self.assertRaises(
            ValueError,
            self.g.add_word,
            "test",
            1,
            "thing_that_ends_with_nym",
            "root_word_string_1",
        )

    def test_to_xlsx(self):
        self.g.add_root_word("dog")
        self.g.to_xlsx_file(self.xlsx_out_file)


unittest.main()
