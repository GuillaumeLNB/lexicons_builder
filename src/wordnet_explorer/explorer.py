# -*- coding: utf-8 -*-
"""
# Note: This skeleton file can be safely removed if not needed!
It can export the result to a rdf graph
"""

import argparse
import inspect
import logging
import os
import sys
from requests.utils import quote


import rdflib
from nltk.corpus import wordnet as wn

try:
    from ._frenetic import FreNetic  # .
except ImportError:
    from _frenetic import FreNetic  # .


__location__ = os.path.join(
    os.getcwd(), os.path.dirname(inspect.getfile(inspect.currentframe()))
)
sys.path.insert(0, os.path.join(__location__, "..", "graphs"))
# print('SYS PATH', sys.path)
from graphs import Graph


__author__ = "GLNB"
__copyright__ = "GLNB"
__license__ = "mit"

_logger = logging.getLogger(__name__)


def explore_wordnet(
    word: str, lang: str, max_depth: int = 5, current_depth=1, _previous_graph=None
) -> rdflib.Graph:
    """Explore wordnet reccursively and return a rdf graph
    containing the synonyms, hyponyms, hypernyms.

    Starting from a word, it will look for its synonyms,
    hyponyms and hypernyms. And for each of these word, it
    will look again until the depth of recursion is reatched.

    Args:
        word (str): the word
        lang (str): language in ISO 639-2 code (eg: fra for French)
        current_depth (int): the depth of the reccursion

    Returns:
        a rdflib.Graph-ish object containing the nearests terms
    >>> from  wordnet_explorer.explorer import explore_wordnet
    RDFLib Version: 5.0.0
    >>> g = explore_wordnet('book', 'eng', 2)
    >>> g
    XXX to updage here
    <Graph identifier=N27894ef24ed34b348830c045489e44b7 (<class 'wordnet_explorer.Graph'>)>
    >>> print(g.serialize(format="ttl").decode())
    @prefix ns1: <http://www.w3.org/2004/02/skos/core#> .
    @prefix ns2: <urn:default:baseUri:#> .
    @prefix ns3: <http://www.w3.org/2006/03/wn/wn20/schema/> .
    @prefix ns4: <http://taxref.mnhn.fr/lod/property/> .
    @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
    ns2:78 ns1:prefLabel "78" ;
        ns3:hyponymOf ns2:record ;
        ns2:depth 1 ;
        ns2:synsetLink <http://wordnet-rdf.princeton.edu/pwn30/03924069-n> .
    ns2:AFISR ns1:prefLabel "AFISR" ;
        ns3:hyponymOf ns2:authority ;
        ns2:depth 1 ;
        ns2:synsetLink <http://wordnet-rdf.princeton.edu/pwn30/08337324-n> .
    ...
    """
    # print("\t" * (2 - depth) + f"exploring {word}", flush=True)
    if lang not in wn.langs():
        raise ValueError(
            f"Language '{lang}' not implemented. Implemented languages are : {sorted(wn.langs())}"
        )

    if not _previous_graph:
        # initializing the Graph for the 1st time
        graph = Graph()
        # adding the root source
        graph.add_root_word(word)
    else:
        graph = _previous_graph

    if current_depth - 1 == max_depth:
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
            graph.add_word(new_word, current_depth, "", word, ss_uri)
            # exit()
            graph = explore_wordnet(
                new_word,
                lang,
                current_depth=current_depth + 1,
                max_depth=max_depth,
                _previous_graph=graph,
            )
        for hypernyms in synset.hypernyms():
            for new_word in hypernyms.lemma_names(lang):
                if graph.word_in_graph(new_word):
                    continue
                assert new_word != word
                graph.add_word(new_word, current_depth, "hypernym", word, ss_uri)
                graph = explore_wordnet(
                    new_word,
                    lang,
                    current_depth=current_depth + 1,
                    max_depth=max_depth,
                    _previous_graph=graph,
                )
        for hyponyms in synset.hyponyms():
            for new_word in hyponyms.lemma_names(lang):
                if graph.word_in_graph(new_word):
                    continue
                assert new_word != word
                graph.add_word(new_word, current_depth, "hyponym", word, ss_uri)
                graph = explore_wordnet(
                    new_word,
                    lang,
                    current_depth=current_depth + 1,
                    max_depth=max_depth,
                    _previous_graph=graph,
                )
        for holonyms in synset.member_holonyms():
            for new_word in hypernyms.lemma_names(lang):
                if graph.word_in_graph(new_word):
                    continue
                assert new_word != word
                graph.add_word(new_word, current_depth, "holonym", word, ss_uri)
                graph = explore_wordnet(
                    new_word,
                    lang,
                    current_depth=current_depth + 1,
                    max_depth=max_depth,
                    _previous_graph=graph,
                )

    return graph


def explore_wolf(
    french_word: str,
    path_to_wolf: str,
    max_depth: int = 5,
    depth=1,
    _previous_graph=None,
    _wolf_object=None,
):
    """Explore the French wordnet WOLF like the `explore_wordnet()` function

    Searches reccursively and return a rdf graph
    containing the synonyms, hyponyms, hypernyms.

    Starting from a word, it will look for its synonyms,
    hyponyms and hypernyms. And for each of these word, it
    will look again until the depth of recursion is reatched.

    Args:
        word (str): the word
        path_to_wolf (str): "/path/to/wolf.xml"
        depth (int): the depth of the reccursion

    Returns:
        a rdflib.Graph-ish object containing the nearests terms
        """
    # _wolf_object

    if not _previous_graph:
        # initializing the Graph for the 1st time
        graph = Graph()
        # adding the root source
        graph.add_root_word(french_word)
    else:
        graph = _previous_graph

    if depth - 1 == max_depth:
        # reccursion ends
        return graph

    if not _wolf_object:
        # to avoid reading the file each time the function is invoked
        _wolf_object = FreNetic(path_to_wolf)

    for synset in _wolf_object.synsets(french_word):
        # ss_uri = (
        #     "http://wordnet-rdf.princeton.edu/pwn30/"
        #     + str(synset.offset()).zfill(8)
        #     + "-"
        #     + synset.pos()
        # )
        for word in synset.literals():
            word = str(word)
            # print(word)
            if graph.word_in_graph(word):
                continue
            assert word != french_word
            # print(f"newword __explore__ is : '{new_word}', word is '{word}'")
            graph.add_word(word, depth, "", french_word)
            # exit()
            graph = explore_wolf(
                word,
                path_to_wolf,
                _wolf_object=_wolf_object,
                depth=depth + 1,
                max_depth=max_depth,
                _previous_graph=graph,
            )
        for hyp in synset.hypernyms():
            for new_word in hyp.literals():
                new_word = str(new_word)
                if graph.word_in_graph(new_word):
                    continue
                assert new_word != french_word
                graph.add_word(new_word, depth, "hypernym", french_word)
                graph = explore_wolf(
                    word,
                    path_to_wolf,
                    _wolf_object=_wolf_object,
                    depth=depth + 1,
                    max_depth=max_depth,
                    _previous_graph=graph,
                )
    return graph


if __name__ == "__main__":
    g = explore_wordnet("book", "eng", 2)
    print("graph is")
    print(g.serialize(format="ttl").decode())
    print("list is:")
    print(g.to_list())

    g = explore_wolf("livre", "/home/k/models/wolf-1.0b4.xml", 3)
    print("graph is")
    print(g.serialize(format="ttl").decode())
    print("list is:")
    print(g.to_list())
    g.to_text_file("_.txt")
