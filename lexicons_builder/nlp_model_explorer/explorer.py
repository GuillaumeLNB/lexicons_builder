# -*- coding: utf-8 -*-
"""
The nlp_model_explorer package contains the functions that are used to retreive neighbours from NLP models.
The language model needs to be in .vec or .bin format.
Works with FastText and word2vec.

Like the other packages, it outputs a :obj:`Graph` containing the results.



.. note::
    Note: See the :doc:`installation section <../installation>` for a list of languages models


"""

import argparse
import inspect
import os
import sys
import logging

from gensim.models import KeyedVectors

__location__ = os.path.join(
    os.getcwd(), os.path.dirname(inspect.getfile(inspect.currentframe()))
)
sys.path.insert(0, os.path.join(__location__, "..", "graphs"))
from graphs import Graph


__author__ = "GLNB"
__copyright__ = "GLNB"
__license__ = "mit"


# _logger = logging.getLogger(__name__)


def _load_model(model_path: str):
    """Try different way of loading the model
    Returns the loaded model
    """

    try:
        logging.info(f"Trying to load '{model_path}' with KeyedVectors binary=True")
        model = KeyedVectors.load_word2vec_format(
            model_path, binary=True, unicode_errors="ignore"
        )
        logging.info("success")
        return model
    except EOFError as e:
        # the model is in a text format
        logging.error(e)
        logging.warning(
            f"Cannot load '{model_path}' with KeyedVectors binary=True. Trying another method"
        )
    try:
        logging.info(f"Trying to load '{model_path}' with KeyedVectors binary=False")
        model = KeyedVectors.load_word2vec_format(
            model_path, binary=False, unicode_errors="ignore"
        )
        logging.info("success")
        return model
    except Exception as e:
        raise ValueError(f"Cannot read the model from '{model_path}'")


def explore_nlp_model(
    word: str,
    model_path: str,
    max_depth: int = 5,
    current_depth=1,
    _previous_graph=None,
    _previous_model=None,
):
    """Explore the model reccursively and return a rdf graph
    containing the neighbour words.

    Args:
        word (str): the word
        model_path (str): the path of the nlp model
        current_depth (int): the depth of the reccursion

    Returns:
        a :obj:`Graph` object containing the terms

    .. code:: python

        >>> from lexicons_builder.nlp_model_explorer.explorer import explore_nlp_model
        >>> g = explore_nlp_model('test', '<path/to/model>', 2)
        >>> print(g)
        @prefix ns1: <http://taxref.mnhn.fr/lod/property/> .
        @prefix ns2: <http://www.w3.org/2004/02/skos/core#> .
        @prefix ns3: <urn:default:baseUri:#> .
        @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

        ns3:annale_corriger ns1:isSynonymOf ns3:qcm ;
            ns2:prefLabel "annale_corriger" ;
            ns3:comesFrom </home/k/models/frWac_no_postag_phrase_500_cbow_cut100.bin> ;
            ns3:depth 2 .

        ns3:applicatif ns1:isSynonymOf ns3:test_unitaire ;
            ns2:prefLabel "applicatif" ;
            ns3:comesFrom </home/k/models/frWac_no_postag_phrase_500_cbow_cut100.bin> ;
            ns3:depth 2 .

        ns3:applications ns1:isSynonymOf ns3:tests ;
            ns2:prefLabel "applications" ;
            ns3:comesFrom </home/k/models/frWac_no_postag_phrase_500_cbow_cut100.bin> ;
            ns3:depth 2 .

    """
    logging.debug(
        f"Exploring the model with word '{word}' current depth is '{current_depth}'"
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

    if not _previous_model:
        logging.info(f"loading nlp model from '{model_path}'")
        # to avoid reading the file each time the function is invoked
        _previous_model = _load_model(model_path)

    if word not in _previous_model:
        # the model does not contain the original word
        return graph

    for new_word in [w[0] for w in _previous_model.most_similar(word)]:
        # add_word(self, word, depth, relation, target_word, synset_uri=None):
        if graph.word_in_graph(new_word):
            continue
        assert new_word != word
        graph.add_word(new_word, current_depth, "synonym", word, comesFrom=model_path)
        graph = explore_nlp_model(
            new_word,
            model_path,
            current_depth=current_depth + 1,
            max_depth=max_depth,
            _previous_graph=graph,
            _previous_model=_previous_model,
        )

    return graph


if __name__ == "__main__":
    g = explore_nlp_model(
        "lire",
        "/home/k/models/frWac_non_lem_no_postag_no_phrase_200_skip_cut100.bin",
        max_depth=2,
    )
    print("graph is")
    print(g.serialize(format="ttl").decode())
    print("list is:")
    print(g.to_list())
