# -*- coding: utf-8 -*-
"""
The scrappers package contains the scrappers that are used to retreive synonyms from the web.

Each website has its own scrapper that inherit from the main :obj:`SynonymsGetter`
class. The internal method `_get_results_from_website()` is the only method that is diffrent from each scrapper (since the html page of their website is different).

The :meth:`get_synonyms_from_scrappers` function agregate the results comming from all websites.


See the :doc:`List of dictionnaries section <../list_dictionaries>` for the list of the websites where the synonyms are comming from.

.. note::
    Some websites have locking mechanisms that prevent you from sending them huge amounts of requests. If you are blocked, you might have to wait some time.

.. note::
    This method of scrapping the data should be updated regularly as the html code might change on the websites.

"""


import argparse
import inspect
import logging
import requests
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from requests.utils import quote

import fake_useragent
from bs4 import BeautifulSoup
from touch import touch
from unidecode import unidecode

__author__ = "GLNB"
__copyright__ = "GLNB"
__license__ = "mit"

_logger = logging.getLogger(__name__)
__location__ = os.path.join(
    os.getcwd(), os.path.dirname(inspect.getfile(inspect.currentframe()))
)
sys.path.insert(0, os.path.join(__location__, "..", "graphs"))
from graphs import Graph


class SynonymsGetter:
    """Main class to get synonyms of terms from different websites"""

    # faking the user agent
    _ua = fake_useragent.UserAgent().random
    logging.debug(f"user-Agent is '{_ua}'")

    def __str__(self):
        if hasattr(self, "website"):
            return f"crawler of {self.website}"
        return "SynonymsGetter object"

    def _get_results_from_website(self, word):
        """This method should be implemented differently for every languages
        and every websites (scrapping method different).
        It sould return an iterable of synonyms scrapped from the website"""
        return []

    def explore_reccursively(
        self,
        word: str,
        max_depth: int = 2,
        current_depth=1,
        _previous_graph=None,
    ) -> Graph:
        """Search for terms reccursively from the website

        Args:
            word (str): the word
            max_depth (int): the deepth of the reccursion
        Returns:
            a Graph object with the words that were looked up

        """

        logging.debug(
            f"Exploring with word '{word}' current depth is '{current_depth}'"
        )

        if not isinstance(max_depth, int):
            raise TypeError(f"max_depth type should be int not '{type(max_depth)}'")

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

        else:
            new_words = [w for w in self._get_results_from_website(word) if w]
            logging.info(f"{len(new_words)} found")
            for n_word in new_words:
                n_word = unidecode(n_word.lower())
                if n_word in graph:
                    logging.debug(f"n_word is already in the graph -> skipping it")
                    continue
                graph.add_word(
                    n_word, current_depth, "synonym", word, comesFrom=self.website
                )
                graph = self.explore_reccursively(
                    n_word,
                    current_depth=current_depth + 1,
                    max_depth=max_depth,
                    _previous_graph=graph,
                )
        return graph

    def download_and_parse_page(self, url: str) -> BeautifulSoup:
        """return the Beautiful soup of the page

        If the http response from the page is not ok,
        return an empty BeautifulSoup

        Args:
            url (str): the url of the webpage
        Returns:
            BeautifulSoup: the BeautifulSoup of the page parsed with html.parser
        """
        logging.info(f"getting {url}")
        r = requests.get(url, headers={"User-Agent": self._ua})
        if r.status_code == 429:
            logging.error(f"the website responded to 429 Too Many Requests")
        if not r.ok:
            logging.error(f"request is not ok. Status code is {r.status_code}")
            # returning an empty BautifulSoup Object
            return BeautifulSoup("", "html.parser")
        return BeautifulSoup(r.text, "html.parser")


class SynonymsGetterSynonymesCom(SynonymsGetter):
    """Scrapper of `synonymes.com <http://www.synonymes.com>`_"""

    website = "synonymes.com"
    lang = "fr"

    def _get_results_from_website(self, word):
        word = unidecode(word.lower())
        url = f"https://www.synonymes.com/synonyme.php?mot={word}"
        soup = self.download_and_parse_page(url)
        words = []
        for box in soup.find_all("div", class_="defbox"):
            for word in box.find_all("a", href=True):
                words.append(word.text.strip().lower())
        return words


# tough to work with as
# class SynonymsGetterDictionnaireSynonymesCom(SynonymsGetter):
#     """Scrapper of `dictionnaire-synonymes.com <https://www.dictionnaire-synonymes.com>`_"""

#     website = "dictionnaire-synonymes.com"
#     lang = "fr"

#     def _get_results_from_website(self, word):
#         # ISO 8859-1 percentaged encoded
#         word = quote(word, encoding='iso-8859-1')
#         url = f"https://www.dictionnaire-synonymes.com/synonyme.php?mot={word}&OK=OK"
#         soup = self.download_and_parse_page(url)
#         words = []
#         for word in soup.find_all("a", class_="lien3"):
#             words.append(word.text.strip().lower())
#         # lien2 contains the domain of the words eg > nature, animal:
#         # for word in soup.find_all("a", class_="lien2"):
#         #     words.append(word.text.strip().lower())
#         return list(set(words))


class SynonymsGetterLesSynonymesCom(SynonymsGetter):
    """Scrapper of `les-synonymes.com <http://www.les-synonymes.com>`_"""

    website = "les-synonymes.com"
    lang = "fr"

    def _get_results_from_website(self, word):
        # word = unidecode(word.lower())
        url = f"http://www.les-synonymes.com/mot/{word}"
        soup = self.download_and_parse_page(url)
        words = []
        for link in soup.find_all("a", href=True):
            if link["href"].startswith("mot/"):
                words.append(link.text.strip())
        return list(set(words))


class SynonymsGetterLeFigaro(SynonymsGetter):
    """Scrapper of `leconjugueur.lefigaro.fr <https://leconjugueur.lefigaro.fr>`_"""

    website = "leconjugueur.lefigaro.fr"
    lang = "fr"

    def _get_results_from_website(self, word):
        # diacritics are important on that website
        # but œ should be changed
        word = word.replace("œ", "oe")

        url = f"https://leconjugueur.lefigaro.fr/frsynonymes.php?mot={word}"
        soup = self.download_and_parse_page(url)
        words = []
        for link in soup.find_all("a", href=True):
            if link["href"].startswith("/synonyme/") and link["title"].startswith(
                "Synonymes de "
            ):
                words.append(link.text.strip())
        return list(set(words))


class SynonymsGetterCrisco2(SynonymsGetter):
    """Scrapper of `crisco2.unicaen.fr <https://crisco2.unicaen.fr>`_"""

    website = "crisco2.unicaen.fr"
    lang = "fr"

    def _get_results_from_website(self, word):
        # diacritics are important on that website
        # but œ should be remplaced
        word = word.replace("œ", "oe")

        url = f"https://crisco2.unicaen.fr/des/synonymes/{word}"
        soup = self.download_and_parse_page(url)
        words = []
        for link in soup.find_all("a", href=True):
            if link["href"].startswith("/des/synonymes/"):
                words.append(link.text.strip())
        return list(set(words))


class SynonymsGetterReverso(SynonymsGetter):
    """Scrapper of `synonyms.reverso.net <synonyms.reverso.net>`_
    Website includes synonyms in French, English, German, Spanish, Italian"""

    website = "synonyms.reverso.net"
    implemented_languages = {"fr", "en", "es", "it", "de"}

    def __init__(self, lang):
        super().__init__()
        if lang not in self.implemented_languages:
            raise ValueError(f"'{lang}' language not implemented")
        self.lang = lang

    def _get_results_from_website(self, word):
        # diacritics are important on that website
        # but œ should be remplaced
        word = word.replace("œ", "oe")

        url = f"https://synonyms.reverso.net/synonyme/{self.lang}/{word}"
        soup = self.download_and_parse_page(url)
        words = []
        for element in soup.find_all("li", id=True):
            if not element["id"].startswith("synonym-"):
                continue
            words.append(element.text.strip())
        return list(set(words))


# English scrappers
class SynonymsGetterLexico(SynonymsGetter):

    """Scrapper of `lexico.com <https://www.lexico.com>`_"""

    website = "lexico.com"
    lang = "en"

    def _get_results_from_website(self, word):
        word = unidecode(word.lower())
        url = f"https://www.lexico.com/synonyms/{word}"
        soup = self.download_and_parse_page(url)
        words = []
        for word in soup.find_all("strong", class_="syn"):
            words.append(word.text.strip())
        for word in soup.find_all("span", class_="syn"):
            for element in word.text.split(", "):
                if not element:
                    words.append(element)
        return list(set(words))


class SynonymsGetterSynonymsCom(SynonymsGetter):
    """Scrapper of `synonyms.com <https://www.synonyms.com>`_"""

    website = "synonyms.com"
    lang = "en"

    def _get_results_from_website(self, word):
        word = unidecode(word.lower())
        url = f"https://www.synonyms.com/synonym/{word}"
        soup = self.download_and_parse_page(url)
        words = []
        for p in soup.find_all("p", class_="syns"):
            for link in p.find_all("a", href=True):
                if not link["href"].startswith("/synonym/"):
                    continue
                words.append(link.text.strip())
        return list(set(words))


# http://www.synonymy.com/


scrappers = {
    "en": [
        SynonymsGetterLexico(),
        SynonymsGetterSynonymsCom(),
        SynonymsGetterReverso("en"),
    ],
    "fr": [
        SynonymsGetterSynonymesCom(),
        # SynonymsGetterDictionnaireSynonymesCom(),
        SynonymsGetterLesSynonymesCom(),
        SynonymsGetterLeFigaro(),
        SynonymsGetterCrisco2(),
        SynonymsGetterReverso("fr"),
    ],
    "es": [SynonymsGetterReverso("es")],
    "it": [SynonymsGetterReverso("it")],
    "de": [SynonymsGetterReverso("de")],
}


def get_synonyms_from_scrappers(word, lang, depth, merge_graph=True) -> Graph:
    """Scrap the websites recursively given the input word

    Args:
        word (str): The word that will be looked up
        lang (str): The language of the word
        deepth (int): The deepth of the reccursion
        merge_graph (bool, optional): by default, returns a merged graph. If set to :obj:`False`, return a list of :obj:`Graph`

    Returns:
        :obj:`Graph` : the graph containing the synonyms

    .. code:: python

        >>> from lexicons_builder.scrapper.scrappers import get_synonyms_from_scrappers
        >>> g = get_synonyms_from_scrappers('flute', 'en', 1)
        >>> g.to_list()
        ['champagne flute', 'channel', 'corrugation', 'cuss', 'damn', 'dizi', 'fl', 'flauta', 'flautist', 'flute', 'flute glass', 'fluting', 'flutist', 'gosh', 'groove', 'pipe', 'piper', 'recorder', 'rifling', 'tik', 'tin whistle', 'transverse flute']

    """
    if lang not in scrappers:
        raise ValueError(f"lang '{lang}' not implemented yet.")

    # WARNING: using the scrapping with threads might not work as
    # the rdflib.plugins.sparql.parser.parseQuery function is not thread safe
    # https://github.com/RDFLib/rdflib/issues/765

    # executor = ThreadPoolExecutor()
    # threads = [
    #     executor.submit(scrapper.explore_reccursively, word, depth)
    #     for scrapper in scrappers
    # ]
    # res = [t.result() for t in threads]

    # thread safe version. Takes a while but it works
    res = []
    for scrapper in scrappers[lang]:
        logging.info(f"scrapping '{scrapper.website}' lang is '{lang}'")
        res.append(scrapper.explore_reccursively(word, depth))
    if merge_graph:
        main_graph = Graph()
        for graph in res:
            main_graph += graph
        return main_graph
    return res


if __name__ == "__main__":
    # scrapper = SynonymsGetterSynonymesCom()
    # g = scrapper.explore_reccursively("rire", 2)
    # print(g.to_str(), file=open("test.ttl", "w"))
    # g.to_text_file("_.txt")

    scrapper = SynonymsGetterLexico()
    g = scrapper.explore_reccursively("book", 2)
    print(g, file=open("_test.ttl", "w"))
    g.to_text_file("_.txt")
