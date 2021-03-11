# -*- coding: utf-8 -*-
"""
The wordnet_explorer package contains the functions that are used to retreive synonyms from `WordNet <https://wordnet.princeton.edu/>`_  and `WOLF <http://pauillac.inria.fr/~sagot/index.html#wolf>`_.

Like the other packages, it outputs a :obj:`Graph` containing the results.

In addition to synonym relations, hypernym, hyponym, holonym relations are added to the graph

"""

import argparse
import inspect
import logging
import os
import sys
from requests.utils import quote


import rdflib
from languagecodes import iso_639_alpha3
from nltk.corpus import wordnet as wn

try:
    from ._frenetic import FreNetic
except ImportError:
    from _frenetic import FreNetic  # .


__location__ = os.path.join(
    os.getcwd(), os.path.dirname(inspect.getfile(inspect.currentframe()))
)
sys.path.insert(0, os.path.join(__location__, "..", "graphs"))
from graphs import Graph


__author__ = "GLNB"
__copyright__ = "GLNB"
__license__ = "mit"

_logger = logging.getLogger(__name__)


def explore_wordnet(
    word: str, lang: str, max_depth: int = 5, current_depth=1, _previous_graph=None
) -> rdflib.Graph:
    """Explore WordNet reccursively and return a rdf graph
    containing the synonyms, hyponyms, hypernyms.

    Starting from a word, it will look for its synonyms,
    hyponyms and hypernyms. And for each of these word, it
    will look again until the depth of recursion is reatched.

    Args:
        word (str): the word
        lang (str): language in ISO 639-1 code (eg: fr for French)
        current_depth (int): the depth of the reccursion

    Returns:
        a :obj:`Graph` object containing the terms


    .. code:: python

        >>> from wordnet_explorer.explorer import explore_wordnet
        RDFLib Version: 5.0.0
        >>> g = explore_wordnet('book', 'en', 1)
        >>> print(g)
        @prefix ns1: <http://www.w3.org/2004/02/skos/core#> .
        @prefix ns2: <http://www.w3.org/2006/03/wn/wn20/schema/> .
        @prefix ns3: <urn:default:baseUri:#> .
        @prefix ns4: <http://taxref.mnhn.fr/lod/property/> .
        @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

        ns3:brochure ns1:prefLabel "brochure" ;
            ns2:hyponymOf ns3:root_word_uri ;
            ns3:depth 1 ;
            ns3:synsetLink <http://wordnet-rdf.princeton.edu/pwn30/06410904-n> .


        ns3:album ns1:prefLabel "album" ;
            ns2:hyponymOf ns3:root_word_uri ;
            ns3:depth 1 ;
            ns3:synsetLink <http://wordnet-rdf.princeton.edu/pwn30/02870092-n> .

    """
    logging.debug(f"Exploring WORDNET with word '{word}' at depth '{current_depth}'")
    lang = iso_639_alpha3(lang)  # wordnet needs iso-639-2
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
            graph.add_word(
                new_word,
                current_depth,
                "synonym",
                word,
                ss_uri,
                comesFrom="http://wordnet-rdf.princeton.edu/",
            )
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
                graph.add_word(
                    new_word,
                    current_depth,
                    "hypernym",
                    word,
                    ss_uri,
                    comesFrom="http://wordnet-rdf.princeton.edu/",
                )
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
                graph.add_word(
                    new_word,
                    current_depth,
                    "hyponym",
                    word,
                    ss_uri,
                    comesFrom="http://wordnet-rdf.princeton.edu/",
                )
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
                graph.add_word(
                    new_word,
                    current_depth,
                    "holonym",
                    word,
                    ss_uri,
                    comesFrom="http://wordnet-rdf.princeton.edu/",
                )
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
    current_depth=1,
    _previous_graph=None,
    _wolf_object=None,
):
    """Explore the French wordnet WOLF like the `explore_wordnet()` function

    Args:
        word (str): the word
        path_to_wolf (str): "/path/to/wolf.xml"
        depth (int): the depth of the reccursion

    Returns:
        a :obj:`Graph` object containing the terms

    .. code:: python

        >>> from wordnet_explorer.explorer import explore_wolf
        >>> g = explore_wolf('fromage', '/path/to/wolf', 1)
        >>> print(g)
        @prefix ns1: <http://www.w3.org/2004/02/skos/core#> .
        @prefix ns2: <urn:default:baseUri:#> .
        @prefix ns3: <http://www.w3.org/2006/03/wn/wn20/schema/> .
        @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

        ns2:aliment ns1:prefLabel "aliment" ;
            ns3:hypernymOf ns2:root_word_uri ;
            ns2:depth 1 .

        ns2:alimentation ns1:prefLabel "alimentation" ;
            ns3:hypernymOf ns2:root_word_uri ;
            ns2:depth 1 .

        ns2:familier ns1:prefLabel "familier" ;
            ns3:hypernymOf ns2:root_word_uri ;
            ns2:depth 1 .

        ns2:laitage ns1:prefLabel "laitage" ;
            ns3:hypernymOf ns2:root_word_uri ;
            ns2:depth 1 .

    """
    logging.debug(
        f"Exploring WOLF with word '{french_word}' at depth '{current_depth}'"
    )

    if not _previous_graph:
        # initializing the Graph for the 1st time
        graph = Graph()
        # adding the root source
        graph.add_root_word(french_word)
    else:
        graph = _previous_graph

    if current_depth - 1 == max_depth:
        # reccursion ends
        return graph

    if not _wolf_object:
        # to avoid reading the file each time the function is called
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
            if graph.word_in_graph(word):
                continue
            assert word != french_word
            graph.add_word(
                word, current_depth, "synonym", french_word, comesFrom=path_to_wolf
            )
            graph = explore_wolf(
                word,
                path_to_wolf,
                _wolf_object=_wolf_object,
                current_depth=current_depth + 1,
                max_depth=max_depth,
                _previous_graph=graph,
            )
        for hyp in synset.hypernyms():
            for new_word in hyp.literals():
                new_word = str(new_word)
                if graph.word_in_graph(new_word):
                    continue
                assert new_word != french_word
                graph.add_word(
                    new_word,
                    current_depth,
                    "hypernym",
                    french_word,
                    comesFrom=path_to_wolf,
                )
                graph = explore_wolf(
                    word,
                    path_to_wolf,
                    _wolf_object=_wolf_object,
                    current_depth=current_depth + 1,
                    max_depth=max_depth,
                    _previous_graph=graph,
                )
    return graph


if __name__ == "__main__":
    # g = explore_wordnet("book", "eng", 2)
    # print("graph is")
    # print(g.serialize(format="ttl").decode())
    # print("list is:")
    # print(g.to_list())

    g = explore_wolf("livre", "/home/k/models/wolf-1.0b4.xml", 2)
    # print("graph is")
    # print(g.serialize(format="ttl").decode())
    # print("list is:")
    # print(g.to_list())
    # g.to_text_file("_.txt")
    g.to_xlsx_file("_test.xlsx")
