#!/bin/python3
import unittest
import os
import sys
from unittest.mock import patch

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.join("..", "..", "lexicons_builder"))
# sys.path.insert(1, os.path.join("..", "src", "wordnet_explorer"))

# from rdflib import Graph
# logging.getLogger("transformers").setLevel(logging.CRITICAL + 1)

import scrapper.scrappers  # as exp


class TestSynonymsGetter(unittest.TestCase):

    words = ("test", "poireau", "lire")
    wrong_words = ("TedsfdfsSt", "f5sdaf5df5")
    word_test = "livre"

    def setUp(self):
        self.scrapper = scrapper.scrappers.SynonymsGetter()

    def tearDown(self):
        pass

    def test___str__(self):
        self.assertIsInstance(str(self.scrapper), str)

    def test__get_results_from_website(self):
        self.assertIsInstance(
            self.scrapper._get_results_from_website(self.word_test), list
        )

    def test_explore_reccursively(self):
        g = self.scrapper.explore_reccursively(self.word_test)
        self.assertTrue(len(g) == 1)
        # just the root word as the base object cannot
        # get synonyms from websites
        self.assertRaises(
            TypeError, self.scrapper.explore_reccursively, self.word_test, "2"
        )

    def test_download_and_parse_page(self):
        with patch("scrapper.scrappers.requests.get") as mocked_request:
            mocked_request.return_value.ok = False
            self.assertEqual(
                BeautifulSoup("", "html.parser"),
                self.scrapper.download_and_parse_page("fakeurl.com"),
            )

    # with patch("utils.web_utils.requests.get") as mocked_get:
    #     mocked_get.return_value.text = web_page
    #     mocked_get.return_value.ok = True
    #     self.scrapper1.scrap()


class TestSynonymsGetterSynonymesCom(TestSynonymsGetter):
    def setUp(self):
        self.scrapper = scrapper.scrappers.SynonymsGetterSynonymesCom()

    def test_explore_reccursively(self):
        g = self.scrapper.explore_reccursively(self.word_test, max_depth=2)
        self.assertTrue(g)
        self.assertTrue(len(g) > 2)


unittest.main()
