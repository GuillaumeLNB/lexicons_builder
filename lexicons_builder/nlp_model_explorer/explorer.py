# -*- coding: utf-8 -*-
"""
NLP model explorer.
Given an language model (.vec or .bin) and a term to look up,
the function, :meth:`nlp_model_explorer.explore`
will look up reccursively for near words close.

Non exaustive languages models could be found:

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
    Returns XXX"""
    try:
        logging.info(f"Trying to load '{model_path}' with KeyedVectors binary=True")
        model = KeyedVectors.load_word2vec_format(
            model_path, binary=True, unicode_errors="ignore"
        )
        logging.info("success")
        return model
    except EOFError:
        # the model is in a text format
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
    containing the close words.

    Starting from a word, it will look for its neighboors,
    And for each of these word, it will look again until
    the depth of recursion is reatched.

    Args:
        word (str): the word
        model_path (str): the path of the nlp model
        current_depth (int): the depth of the reccursion

    Returns:
        a rdflib.Graph object containing the nearests terms
    XXX TODO add example
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
        graph.add_word(new_word, current_depth, "", word, comesFrom=model_path)
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
