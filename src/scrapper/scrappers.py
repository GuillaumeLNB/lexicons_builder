# -*- coding: utf-8 -*-
"""
Each website has its own scrapper that inherit from the main `SynonymsGetter`
class. The `_get_results_from_website()` is the only method that is diffrent
from each scrapper (since the html page of their website is different).

Note: this method of scrapping the data should be updated regularly as
the html code might change on the websites.
Note (2): the database from these websites should be dumped and the results comming from these
dumps instead of sending requests to the websites.
"""

import argparse
import inspect
import logging
import requests
import os
import sys

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
# print('SYS PATH', sys.path)
from graphs import Graph


class SynonymsGetter:
    """Main class to get synonyms of terms from different websites"""

    # faking the user agent
    ua = (
        fake_useragent.UserAgent().random
    )  # TODO remove that thing from sphinx documentation

    def __str__(self):
        if hasattr(self, "website"):
            return f"crawler of {self.website}"
        return "SynonymsGetter object"

    def _get_results_from_website(self, word):
        """This method should be implemented differently for every languages
        and every websites (scrapping method different).
        It sould return an iterable of synonyms scrapped from the website"""
        return set()

    def explore_reccursively(
        # self, term_to_look_up: str, previous_terms: dict, deepth: int = 10
        self,
        word: str,
        max_depth: int = 2,
        current_depth=1,
        _previous_graph=None,
    ):
        """Will search for terms reccursively from the website


        Args:
            term_to_look_up (str): the word
            previous_terms (dict): a dict containing the words that were looked up
                            previously. key=word value=the deepth
            deepth (int): the deepth of the reccursion
        Returns:
            a Graph object with the words that were looked up
        XXX    """
        # print(f"WORD IS '{word}'\tDEPTH IS '{current_depth}'") # XXX

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
            for n_word in new_words:
                n_word = unidecode(n_word.lower())
                if n_word in graph:
                    continue
                graph.add_word(n_word, current_depth, "syn", word)
                graph = self.explore_reccursively(
                    n_word,
                    current_depth=current_depth + 1,
                    max_depth=max_depth,
                    _previous_graph=graph,
                )
        return graph

    # def get_synonyms(
    #     self, word: str, deepth: int, indent: int = 4, out_file: str = None
    # ):
    #     """Get the synomys from a website and print them to a file

    #     Args:
    #         word (str): the word we want synonyms from
    #         deepth (int): the deepth of the reccursion
    #         indent (int): the indentation in the file
    #         out_file (str): the file name were the results will be.
    #                         if None, it will create a new file
    #                         using f"{self.lang}_{domain}_{word}_{deepth}.txt"
    #         """

    #     if not out_file:
    #         # domain = re.search(r'www\.([A-z\-_])\.[A-z]{2,3}', self.website).group(1)
    #         domain = self.website.split(".")[0]
    #         out_file = f"{self.lang}_{domain}_{word}_{deepth}.txt"
    #     self.out_file = out_file
    #     touch(self.out_file)

    #     words = self.explore_reccursively(word, {}, deepth)
    #     # print(words)
    #     with open(self.out_file, "w") as f:
    #         # print(sorted(set([unidecode(w).lower().strip() for w in words])))
    #         # print(words)
    #         print(word, file=f)
    #         for word in sorted(set([unidecode(w).lower().strip() for w in words])):
    #             print(" " * indent * (deepth - words[word]) + word, file=f)
    #             # print(word)
    #             # input()
    #     print(self.out_file)

    def download_and_parse_page(self, url: str):
        """return the Beautiful soup of the page

        If the http response from the page is not ok,
        return an empty list

        Args:
            url: the url of the webpage
        Returns:
            BeautifulSoup: the BS of the page
        """
        logging.info(f"getting {url}")
        r = requests.get(url, headers={"User-Agent": self.ua})
        if not r.ok:
            logging.error(f"request is not ok. Status code is {r.status_code}")
            return []
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


class SynonymsGetterDictionnaireSynonymesCom(SynonymsGetter):
    """Scrapper of `dictionnaire-synonymes.com <https://www.dictionnaire-synonymes.com>`_"""

    website = "dictionnaire-synonymes.com"
    lang = "fr"

    def _get_results_from_website(self, word):
        word = unidecode(word.lower())
        url = f"https://www.dictionnaire-synonymes.com/synonyme.php?mot={word}&OK=OK"
        soup = self.download_and_parse_page(url)
        words = []
        for word in soup.find_all("a", class_="lien3"):
            words.append(word.text.strip().lower())
        for word in soup.find_all("a", class_="lien2"):
            words.append(word.text.strip().lower())
        return list(set(words))


class SynonymsGetterLesSynonymesCom(SynonymsGetter):
    """Scrapper of `les-synonymes.com <http://www.les-synonymes.com>`_"""

    website = "les-synonymes.com"
    lang = "fr"

    def _get_results_from_website(self, word):
        word = unidecode(word.lower())
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
        word = unidecode(word.lower())
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
        word = unidecode(word.lower())
        url = f"https://crisco2.unicaen.fr/des/synonymes/{word}"
        soup = self.download_and_parse_page(url)
        words = []
        for link in soup.find_all("a", href=True):
            if link["href"].startswith("/des/synonymes/"):
                words.append(link.text.strip())
        return list(set(words))


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
        raise ValueError("The scrpping returns bad results")
        word = unidecode(word.lower())
        url = f"https://www.synonyms.com/synonym/{word}"
        soup = self.download_and_parse_page(url)
        words = []
        for link in soup.find_all("a", href=True):
            if not link["href"].startswith("/synonym/") and not link.text.startswith(
                "What are some"
            ):
                words.append(link.text.strip())
        return list(set(words))


if __name__ == "__main__":
    # scrapper = SynonymsGetterSynonymesCom()
    # g = scrapper.explore_reccursively("rire", 2)
    # print(g.to_str(), file=open("test.ttl", "w"))
    # g.to_text_file("_.txt")

    scrapper = SynonymsGetterLexico()
    g = scrapper.explore_reccursively("book", 2)
    print(g, file=open("test.ttl", "w"))
    g.to_text_file("_.txt")
