#!/bin/python3
import unittest
import os
import sys

sys.path.insert(0, os.path.join("..", ".."))

import lexicons_builder.nlp_model_explorer.explorer as exp


class TestExplorer(unittest.TestCase):

    words = ("test", "poireau", "lire")
    wrong_words = ("TedsfdfsSt", "f5sdaf5df5")
    wrong_types = (0, type, str)
    model_paths = [
        "~/models/frWac_non_lem_no_postag_no_phrase_200_skip_cut100.bin",  # smallest
        # "~/models/frWac_no_postag_phrase_500_cbow_cut100.bin",
        # "~/models/cz_law.word2vec.model.txt",
        # "~/models/nlwiki_20180420_100d.txt",
    ]

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_loading_model(self):
        for model in self.model_paths:
            # not looking deep, just to check the model is loading
            g1 = exp.explore_nlp_model(self.words[0], model, 1)
            self.assertTrue(len(g1) > 2)

    def test_wrong_word(self):
        for wrong_w in self.wrong_types:
            self.assertRaises(
                TypeError, exp.explore_nlp_model, wrong_w, self.model_paths[0], 2
            )

    def test_list_uniq(self):
        word = "news"
        g1 = exp.explore_nlp_model(word, self.model_paths[0], 2)
        self.assertEqual(len(g1.to_list()), len(set(g1.to_list())))

    def test_graph_is_empty(self):
        for word in self.wrong_words:
            # the graph contains only the root word -> 2 rdf triplets
            self.assertEqual(1, len(exp.explore_nlp_model(word, self.model_paths[0])))


unittest.main()
