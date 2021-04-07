#!/bin/python3
import unittest
import os
import re
import sys
from unittest.mock import patch

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.join("..", "..", "lexicons_builder"))

import scrappers.scrappers  # as exp


class TestSynonymsGetter(unittest.TestCase):

    words = ("test", "poireau", "lire")
    wrong_words = ("TedsfdfsSt", "f5sdaf5df5")
    word_test = "livre"

    def setUp(self):
        self.scrapper = scrappers.scrappers.SynonymsGetter()

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
        with patch("scrappers.scrappers.requests.get") as mocked_request:
            mocked_request.return_value.ok = False
            self.assertEqual(
                BeautifulSoup("", "html.parser"),
                self.scrapper.download_and_parse_page("fakeurl.com"),
            )


unittest.main()
