#!/bin/python3
"""
will search for synonyms in French and English and assert
there's no duplicate,
graph merging etc


"""
import html
import logging

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] -[%(name)s] - [%(levelname)s] - %(message)s",
    handlers=[logging.StreamHandler()],
)

import re
import pickle
import os
import sys
import unittest
from unittest.mock import patch

from glob import glob
from parameterized import parameterized_class
from touch import touch

sys.path.insert(0, os.path.join("..", ".."))


from lexicons_builder.scrappers.scrappers import get_synonyms_from_scrappers, scrappers

sys.path.insert(0, os.path.join("..", "..", "lexicons_builder", "graphs"))
from graphs import Graph


@parameterized_class(
    ("lang", "depth", "word"),
    [
        # fr
        ("fr", 1, "test"),
        ("fr", 1, "coïncidence"),
        ("fr", 1, "crâne"),
        ("fr", 1, "maître"),
        ("fr", 1, "être"),
        ("fr", 1, "élève"),
        ("fr", 1, "cœur"),
        ("fr", 1, "élégant"),
        # en
        ("en", 1, "test"),
        # es
        ("es", 1, "test"),
        # it
        ("it", 1, "test"),
        # de
        ("de", 1, "Test"),
        # cs
        ("cs", 2, "knížka"),  # book
        ("cs", 2, "sníst"),  # eat
        ("cs", 2, "auto"),  # cat
        ("cs", 2, "jíst"),  # eat
        ("it", 1, "libro"),  # book
        ("ru", 1, "книга"),  # книга
    ],
)
class TestScrapperGraph(unittest.TestCase):

    out_text_file = "_.txt"
    out_ttl_file = "_.ttl"
    out_ttl_file_2 = "_2.ttl"

    @classmethod
    def setUpClass(cls):

        cls.res = get_synonyms_from_scrappers(
            cls.word, cls.lang, cls.depth, merge_graph=False
        )
        cls.scrapper_names = [scr.website for scr in scrappers[cls.lang]]
        # print(cls.word)
        # print(cls.res[0].to_text_file())

    def setUp(self):
        # self.res = get_synonyms_from_scrappers(
        #     "test", self.lang, self.depth, merge_graph=False
        # )
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

    def test_all_scrappers_return_results(self):
        for graph, scrapper_name in zip(self.res, self.scrapper_names):
            with self.subTest():
                self.assertFalse(
                    graph.is_empty(),
                    msg=f"Error with scrapper of '{scrapper_name}'. lang is '{self.lang}'. word is '{self.word}'",
                )
                self.assertTrue(
                    graph.contains_synonyms(),
                    msg=f"Error with scrapper of '{scrapper_name}'. lang is '{self.lang}'. word is '{self.word}'",
                )

    def test_no_W_in_words(self):
        for word in self.merged_graph.to_list():
            with self.subTest(msg=f"test failed with word '{word}'"):
                # no parenthesis
                self.assertFalse(re.search(r"[\(\)]", word))
                # htm escaped
                self.assertTrue(html.unescape(word) == word)
                # no html tag
                self.assertFalse(re.search(r"[<>]", word))
                # no space
                self.assertTrue(word.strip() == word)


# class TestSynonymsGetterSynonymesCom(TestSynonymsGetter):
#     def setUp(self):
#         self.scrapper = scrappers.scrappers.SynonymsGetterSynonymesCom()

#     def test_explore_reccursively(self):
#         g = self.scrapper.explore_reccursively(self.word_test, max_depth=2)
#         self.assertTrue(g)
#         self.assertTrue(len(g) > 2)


unittest.main()
