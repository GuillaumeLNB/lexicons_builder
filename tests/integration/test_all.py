#!/bin/python3
import unittest
import os
import sys

import rdflib
from touch import touch
from parameterized import parameterized_class

sys.path.insert(0, os.path.join("..", ".."))

import lexicons_builder


@parameterized_class(
    ("lang", "depth", "word"),
    [
        ("fr", "1", "test", "ttl"),
        ("nl", "1", "test", "ttl"),
        # ("de", "1", "test", "ttl"),
        # ("cs", "1", "test", "ttl"),
    ],
)
class TestLexiconBuilder(unittest.TestCase):

    out_file_txt = "_test.txt"
    out_file_ttl = "_test.ttl"
    # print(self.lang)

    @classmethod
    def setUpClass(cls):

        cls.args = {
            "word": cls.word,
            "depth": int(cls.depth),
            "format": "ttl",
            "outfile": cls.out_file_ttl,
            "lang": cls.lang,
        }

        nlp_model_path = (
            "~/models/frWac_non_lem_no_postag_no_phrase_200_skip_cut100.bin"  # smallest
        )
        wolf_path = "/home/k/models/wolf-1.0b4.xml"

        cls.graph = lexicons_builder.build_lexicon(
            words=[cls.args["word"]],
            lang=cls.args["lang"],
            depth=cls.args["depth"],
            nlp_model_paths=[nlp_model_path],
            wolf_path=wolf_path,
            wordnet=True,
            web=True,
        )
        cls.graph._set_root_word_attribute()

    def test___contains(self):
        self.assertTrue("test" in self.graph)
        self.assertFalse("notest" in self.graph)

    def test_str(self):
        self.assertIsInstance(self.graph.to_str(), str)
        g2 = rdflib.Graph()
        g2.parse(data=str(self.graph), format="ttl")

    def test___len__(self):
        # we want more than 10 words
        self.assertTrue(len(self.graph) > 10)

    def test_list_words(self):
        "test all words are in the graph, have a depth and a comes from properties"
        for word in self.graph.to_list():
            if word in self.graph.root_words:
                continue
            with self.subTest(msg=f"test with '{word}'"):
                query = (
                    '''SELECT ?depth ?from
                WHERE {?_ <http://www.w3.org/2004/02/skos/core#prefLabel> "'''
                    + word
                    + """" ; <urn:default:baseUri:#depth>  ?depth ; <urn:default:baseUri:#comesFrom>
                ?from }"""
                )
                self.assertTrue([_ for _ in self.graph.query(query)][0])

    def test_set_root_word(self):
        for w in self.graph.root_words:
            self.assertTrue(isinstance(w, str))
        self.graph._set_root_word_attribute()
        for w in self.graph.root_words:
            self.assertTrue(isinstance(w, str))

    # def test_to_text_file(self):
    #     self.graph.parse(self.graph_test_path, format="ttl")
    #     self.g.to_text_file(self.out_file)
    #     with open(self.out_file) as f:
    #         words = sorted([line.strip() for line in f if line.strip()])
    #     self.assertEqual(words, self.g.to_list())

    # def test_good_words(self):
    #     self.graph.parse(self.graph_test_path, format="ttl")
    #     for word in self.g.to_list():
    #         self.assertTrue(word)  # no empty words
    #         self.assertTrue(unidecode(word.lower().strip()) == word)  # no

    # def test_is_empty(self):
    #     self.assertTrue(self.g.is_empty())
    #     self.assertRaises(ValueError, self.g._set_root_word_attribute)
    #     rw_strings = ["root_word_string_1", "root_word_string_2", "root_word_string_3"]
    #     for w in rw_strings:
    #         self.g.add_root_word(w)
    #         self.assertFalse(self.g.is_empty())
    #     self.assertTrue(rw_strings == self.g.to_list())

    # def test_add_several_root_words(self):
    #     self.g.add_root_word("root_word_string_1")
    #     self.g.add_root_word("root_word_string_2")
    #     self.g.add_root_word("root_word_string_3")
    #     self.g.to_text_file(self.out_file)
    #     with open(self.out_file) as f:
    #         words = sorted([line.strip() for line in f if line.strip()])
    #     self.assertEqual(words, self.g.to_list())

    # def test_add_several_root_words_with_previous_graph(self):
    #     self.g.parse(self.graph_test_path, format="ttl")
    #     self.g.add_root_word("root_word_string_1")
    #     self.g.add_root_word("root_word_string_2")
    #     self.g.add_root_word("root_word_string_3")

    #     self.g.to_text_file(self.out_file)
    #     with open(self.out_file) as f:
    #         words = sorted([line.strip() for line in f if line.strip()])
    #     self.assertEqual(words, self.g.to_list())
    #     self.test_list_is_sorted()

    def test_list_is_sorted(self):
        self.assertTrue(sorted(set(self.graph.to_list())) == self.graph.to_list())


unittest.main()
