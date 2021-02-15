#!/bin/python3
import unittest
import os
import sys

import rdflib
from touch import touch
from unidecode import unidecode


sys.path.insert(0, os.path.join("..", "src", "graphs"))
from graphs import Graph


class TestGraph(unittest.TestCase):

    words = ("test", "poireau", "lire")
    wrong_words = ("TedsfdfsSt", "f5sdaf5df5")
    out_file = "_.txt"

    def setUp(self):
        touch(self.out_file)

    def tearDown(self):
        os.remove(self.out_file)

    def test_add_word(self):
        g = Graph()
        g.add_word("test", 5, "relation1", "target_word")

    def test___contains(self):
        g = Graph()
        g.add_word("test", 5, "relation1", "target_word")
        self.assertTrue("test" in g)
        self.assertFalse("notest" in g)

    def test_str(self):
        g = Graph()
        g.add_word("test", 5, "relation1", "target_word")
        self.assertIsInstance(g.to_str(), str)
        g2 = rdflib.Graph()
        g2.parse(data=str(g), format="ttl")

    def test_word_in_graph(self):
        g = Graph()
        g.add_word("test", 5, "relation1", "target_word")
        self.assertTrue(g.word_in_graph("test"))
        self.assertFalse(g.word_in_graph("tfdfdfest"))

    def test_to_text_file(self):
        g = Graph()
        graph_path = "graph_synonymsCom_dep=2_w=rire.ttl"
        g.parse(graph_path, format="ttl")
        g.to_text_file(self.out_file)
        with open(self.out_file) as f:
            words = sorted([line.strip() for line in f if line.strip()])
        self.assertEqual(words, g.to_list())

    def test_good_words(self):
        g = Graph()
        graph_path = "graph_synonymsCom_dep=2_w=rire.ttl"
        g.parse(graph_path, format="ttl")
        for word in g.to_list():
            self.assertTrue(word)  # no empty words
            self.assertTrue(unidecode(word.lower()) == word)  # no


unittest.main()
