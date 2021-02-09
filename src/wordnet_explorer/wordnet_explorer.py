# -*- coding: utf-8 -*-
"""
# Note: This skeleton file can be safely removed if not needed!
It can export the result to a rdf graph
"""

import argparse
import sys
import logging
from requests.utils import quote

import rdflib

__author__ = "GLNB"
__copyright__ = "GLNB"
__license__ = "mit"

_logger = logging.getLogger(__name__)

from nltk.corpus import wordnet as wn


class _Graph(rdflib.Graph):

    local_namespace = "urn:default:baseUri:#"

    def word_in_graph(self, word):
        """return True if the word is in the graph"""
        # check if the word is already in the graph
        query_check = (
            'ASK {?_ <http://www.w3.org/2004/02/skos/core#prefLabel>  "' + word + '"}'
        )
        # print(f"checking if word '{word}' in graph")
        if [_ for _ in self.query(query_check)][0]:
            # print("it is already")
            return True
        # print("it is not")

    def add_word(self, word, depth, relation, target_word, synset_uri):
        "add the word to the graph"
        # to avoid unvalid URI
        # as some wordnet words do have unwanted characters
        ss_word = quote(word)
        ss_target_word = quote(target_word)
        assert ss_word != ss_target_word
        # print(f"newword is : '{ss_target_word}', word is '{ss_word}'")

        base_local = rdflib.Namespace(self.local_namespace)
        base_wn = rdflib.Namespace("http://www.w3.org/2006/03/wn/wn20/schema/")
        if relation == "hyponym":
            rela = base_wn.hyponymOf
        elif relation == "hypernym":
            rela = base_wn.hypernymOf
        elif relation == "holonym":
            rela = base_wn.holonymOf
        else:
            # word is synonym
            rela = rdflib.URIRef("http://taxref.mnhn.fr/lod/property/isSynonymOf")
        # adding the relation word is synonym/hyponym/... of targhet word
        self.add(
            (
                rdflib.URIRef(self.local_namespace + ss_word),
                rela,
                rdflib.URIRef(self.local_namespace + ss_target_word),
            )
        )
        # adding the depth information
        self.add(
            (
                rdflib.URIRef(self.local_namespace + ss_word),
                base_local.depth,
                rdflib.Literal(depth),
            )
        )
        # adding the preflabel info
        self.add(
            (
                rdflib.URIRef(self.local_namespace + ss_word),
                rdflib.URIRef("http://www.w3.org/2004/02/skos/core#prefLabel"),
                rdflib.Literal(word),
            )
        )
        # adding the synset info
        self.add(
            (
                rdflib.URIRef(self.local_namespace + ss_word),
                base_local.synsetLink,
                rdflib.URIRef(synset_uri),
            )
        )

    def add_root_word(self, word):
        "add the root word to the graph"
        self.add(
            (
                rdflib.URIRef(self.local_namespace) + quote(word),
                rdflib.RDF.type,
                rdflib.URIRef(self.local_namespace + "root_word"),
            )
        )
        self.add(
            (
                rdflib.URIRef(self.local_namespace) + quote(word),
                rdflib.URIRef("http://www.w3.org/2004/02/skos/core#prefLabel"),
                rdflib.Literal(word),
            )
        )


def explore(word: str, lang: str, depth: int = 5, previous_graph=None):
    """Explore wordnet reccursively and return a rdf graph
    containing the synonyms, hyponyms, hypernyms.

    Starting from a word, it will look for its synonyms,
    hyponyms and hypernyms. And for each of these word, it
    will look again until the depth of recursion is reatched.

    Args:
        word (str): the word
        lang (str): language in ISO 639-2 code (eg: fra for French)
        depth (int): the depth of the reccursion

    Returns:
        a rdflib.Graph object containing the nearests terms
    """
    # print("\t" * (2 - depth) + f"exploring {word}", flush=True)
    if lang not in wn.langs():
        raise ValueError(
            f"Language '{lang}' not implemented. Implemented languages are : {sorted(wn.langs())}"
        )

    if not previous_graph:
        # initializing the Graph for the 1st time
        graph = _Graph()
        # adding the root source
        graph.add_root_word(word)
    else:
        graph = previous_graph

    if not depth:
        # reccursion ends
        return graph

    for synset in wn.synsets(word, lang=lang):
        ss_uri = (
            "http://wordnet-rdf.princeton.edu/pwn30/"
            + str(synset.offset()).zfill(8)
            + "-"
            + synset.pos()
        )
        for new_word in synset.lemma_names(lang):
            if graph.word_in_graph(new_word):
                continue
            assert new_word != word
            # print(f"newword __explore__ is : '{new_word}', word is '{word}'")
            graph.add_word(new_word, depth, "", word, ss_uri)
            # exit()
            graph = explore(new_word, lang, depth=depth - 1, previous_graph=graph)
        for hypernyms in synset.hypernyms():
            for new_word in hypernyms.lemma_names(lang):
                if graph.word_in_graph(new_word):
                    continue
                assert new_word != word
                graph.add_word(new_word, depth, "hypernym", word, ss_uri)
                graph = explore(new_word, lang, depth=depth - 1, previous_graph=graph)
        for hyponyms in synset.hyponyms():
            for new_word in hyponyms.lemma_names(lang):
                if graph.word_in_graph(new_word):
                    continue
                assert new_word != word
                graph.add_word(new_word, depth, "hyponym", word, ss_uri)
                graph = explore(new_word, lang, depth=depth - 1, previous_graph=graph)
        for holonyms in synset.member_holonyms():
            for new_word in hypernyms.lemma_names(lang):
                if graph.word_in_graph(new_word):
                    continue
                assert new_word != word
                graph.add_word(new_word, depth, "holonym", word, ss_uri)
                graph = explore(new_word, lang, depth=depth - 1, previous_graph=graph)

    return graph


if __name__ == "__main__":
    g = explore("livre", "fra", 1)
    print("graph is")
    print(g.serialize(format="ttl").decode())
