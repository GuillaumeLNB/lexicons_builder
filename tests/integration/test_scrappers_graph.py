#!/bin/python3
"""
will search for synonyms in French and English and assert
there's no duplicate,
graph merging etc


"""
import logging

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] -[%(name)s] - [%(levelname)s] - %(message)s",
    handlers=[logging.StreamHandler()],
)


import pickle
import os
import sys
import unittest
from unittest.mock import patch

from glob import glob
from parameterized import parameterized_class
from touch import touch

sys.path.insert(0, os.path.join("..", ".."))


from lexicons_builder.scrapper.scrappers import get_synonyms_from_scrappers

sys.path.insert(0, os.path.join("..", "..", "lexicons_builder", "graphs"))
from graphs import Graph


@parameterized_class(
    ("lang", "depth", "word"),
    [
        ("fr", 1, "test"),
        ("en", 1, "test"),
        ("es", 1, "test"),
        ("it", 1, "test"),
        ("de", 1, "Test"),
    ],
)
class TestScrapperGraph(unittest.TestCase):

    out_text_file = "_.txt"
    out_ttl_file = "_.ttl"
    out_ttl_file_2 = "_2.ttl"

    def setUp(self):
        try:
            self.res = get_synonyms_from_scrappers(
                "test", self.lang, self.depth, merge_graph=False
            )
        except Exception as e:
            raise e

        self.merged_graph = Graph()

        for g in self.res:
            self.merged_graph += g
        with open(self.out_ttl_file, "w") as f:
            print(self.merged_graph, file=f)

        self.words = []
        for g in self.res:
            self.words += g.to_list()

        self.words = set(self.words)

        touch(self.out_text_file)
        touch(self.out_ttl_file)
        touch(self.out_ttl_file_2)

    def tearDown(self):
        os.remove(self.out_text_file)
        os.remove(self.out_ttl_file)
        os.remove(self.out_ttl_file_2)
        # return

    def test_same_output(self):
        for word in self.words:
            self.assertTrue(word in self.merged_graph)

    def test_not_loosing_word_in_output(self):
        self.merged_graph.to_text_file(self.out_text_file)
        words_in_file = []
        with open(self.out_text_file) as f:
            for line in f:
                if line.strip():
                    self.assertTrue(
                        line.strip() in self.merged_graph, f"word is: {line.strip()}"
                    )
                    self.assertTrue(line.strip() in self.words)
                    words_in_file.append(line.strip())
        self.assertEqual(len(words_in_file), len(self.words))
        self.assertEqual(len(words_in_file), len(set(words_in_file)))

    def test_delete_several_depth(self):
        self.merged_graph.delete_several_depth()
        self.test_not_loosing_word_in_output()
        self.test_same_output()
        # cheking if there are no tripple with seveal depth
        q = ""
        with open(self.out_ttl_file_2, "w") as f:
            print(self.merged_graph, file=f)

    def test_all_scrappers_return_rest(self):
        for graph in self.res:
            # with self.subTest(graph.)
            self.assertFalse(graph.is_empty())
            self.assertTrue(graph.contains_synonyms())


unittest.main()
