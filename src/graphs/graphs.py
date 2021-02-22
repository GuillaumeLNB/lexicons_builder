#!/usr/bin/env python3
import logging
from requests.utils import quote

import rdflib
from rdflib.plugins.sparql.parser import parseQuery
from touch import touch


class Graph(rdflib.Graph):
    """same as a rdflib.Graph object https://rdflib.readthedocs.io/en/stable/intro_to_creating_rdf.html, but with a few additional methods XXX"""

    local_namespace = "urn:default:baseUri:#"
    base_local = rdflib.Namespace(local_namespace)
    root_words = []
    root_word_uri = f"{local_namespace}root_word_uri"

    def __contains__(self, word):
        """quick check to see if there's a word with a prefLabel predicate
        that is the same as the word
        >>> "book" in g
        True"""

        return self.word_in_graph(word)

    def __str__(self):
        """quick way of serializing the graph to ttl"""
        return self.to_str()

    def __len__(self):
        "return the number of words in the graph"
        return len(self.to_list())

    def word_in_graph(self, word):
        """return True if the word is in the graph"""
        # checks if the word is already in the graph
        assert isinstance(word, str), f"word is not str it is {type(word)}"
        query_check = (
            'ASK {?_ <http://www.w3.org/2004/02/skos/core#prefLabel>  "' + word + '"}'
        )
        try:
            parseQuery(query_check)
        except Exception as e:
            logging.error(f"Error while checking if the word '{word}' is in the graph")
            logging.error(
                f"the query '''{query_check}''' is could be badly formated OR you're using threads"
            )
            # the parseQuery function from rdflib could raise errors
            # if used with threads
            # see https://github.com/RDFLib/rdflib/issues/765
            raise e

        # print(f"checking if word '{word}' in graph")
        if [_ for _ in self.query(query_check)][0]:
            # print("it is already")
            return True
        # print("it is not")

    def _check_word_type(self, word):
        "raise a TypeError if type(word)!=str"
        if not isinstance(word, str):
            raise TypeError(
                f"the word you're adding to the graph is not a string instance. It has a '{type(word)}' type"
            )

    def add_word(
        self, word, depth, relation, target_word, synset_uri=None, comesFrom=None
    ):
        "add the word to the graph XXX"
        self._check_word_type(word)
        # to avoid unvalid URI
        # as some wordnet words do have unwanted characters
        ss_word = quote(word)
        ss_target_word = quote(target_word)
        assert ss_word != ss_target_word

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

        if depth == 1:
            # the relation is linked to the root word
            target = rdflib.URIRef(self.root_word_uri)
        else:
            target = rdflib.URIRef(self.local_namespace + ss_target_word)
        # adding the relation word is synonym/hyponym/... of target word
        self.add((rdflib.URIRef(self.local_namespace + ss_word), rela, target,))
        # adding the depth information
        self.add(
            (
                rdflib.URIRef(self.local_namespace + ss_word),
                self.base_local.depth,
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
        if synset_uri:
            self.add(
                (
                    rdflib.URIRef(self.local_namespace + ss_word),
                    self.base_local.synsetLink,
                    rdflib.URIRef(synset_uri),
                )
            )
        # adding the website the data is comming from
        if comesFrom:
            self.add(
                (
                    rdflib.URIRef(self.local_namespace + ss_word),
                    self.base_local.comesFrom,
                    rdflib.URIRef(comesFrom),
                )
            )
            assert (
                "<file:///home/k/Documents/lexicons_builder/"
                not in self.serialize(format="ttl").decode()
            )

    def add_root_word(self, word):
        "add the root word to the graph"
        # self.root_word = word
        # self.root_words.append(word)
        # self.root_word_uri = f"{self.local_namespace}root_word"
        # self.root_word_uri = f"{self.local_namespace}{self.root_word}"
        self._check_word_type(word)

        self.add(
            (
                rdflib.URIRef(self.root_word_uri),
                rdflib.RDF.type,
                rdflib.URIRef(self.local_namespace + "root_word"),
            )
        )
        self.add(
            (
                rdflib.URIRef(self.root_word_uri),
                rdflib.URIRef("http://www.w3.org/2004/02/skos/core#prefLabel"),
                rdflib.Literal(word),
            )
        )
        self._set_root_word_attribute()

    def is_empty(self):
        """return True if the graph is empty (contain no tripples)"""
        for s, o, p in self:
            break
        else:
            return True

    def contains_synonyms(self):
        """return True if the graph contains at least one synonym"""
        q_check = "ASK {?_ <http://taxref.mnhn.fr/lod/property/isSynonymOf> ?_2}"
        return [r for r in self.query(q_check)][0]

    def _set_root_word_attribute(self):
        """set the root_word and root_word_uri attributes
        by looking at the self.graph"""
        self.root_words = []
        if self.is_empty():
            raise ValueError(f"graph is empty")

        q_root = (
            "SELECT ?uri ?pref WHERE {?uri a <"
            + self.local_namespace
            + """root_word> ;
        <http://www.w3.org/2004/02/skos/core#prefLabel>  ?pref  }"""
        )
        res = [r for r in self.query(q_root)]
        assert res, "The query to get the root word returned no results."
        for i, (uri, pref) in enumerate(res):
            # self.root_word_uri = str(uri)
            # self.root_word = str(pref)
            self.root_words.append(pref)
        if i:
            logging.warning(
                f"The query to retrive the root word returned several results"
            )
            logging.warning(f"The root words are: {self.root_words}")

    def delete_several_depth(self, method="MIN"):
        """When a word has several depth, this method deletes
        the depths XXX """
        # XXX should be implemented using one sparql query

        q_words = """SELECT ?uri ( COUNT(?depth) AS  ?c )
        WHERE {?uri <urn:default:baseUri:#depth> ?depth}
        GROUP BY ?uri
        ORDER BY ASC (?uri)"""

        for uri, depth in self.query(q_words):
            if int(depth) < 2:
                # skipping the uri that do not have several
                # depth properties
                continue
            q_d = (
                "SELECT (MIN(?o) AS ?int) WHERE { <"
                + str(uri)
                + """> <urn:default:baseUri:#depth> ?o } """
            )
            cur_dep = [int(dep) for dep, in self.query(q_d)][0]
            q_all_depth = (
                "SELECT ?unwanted_depth WHERE { <"
                + str(uri)
                + "> <urn:default:baseUri:#depth> ?unwanted_depth }"
            )
            for (unwanted_tripple,) in self.query(q_all_depth):
                if int(unwanted_tripple) == cur_dep:
                    continue
                self.remove(
                    (uri, self.base_local.depth, rdflib.Literal(int(unwanted_tripple)))
                )

    def to_list(self):
        """returns all of the terms contained in the graph to a list"""
        # getting the maximum depth of the graph
        # q_depth = 'SELECT ?de WHERE { ?_ <urn:default:baseUri:#depth>  ?de} ORDER BY DESC(?de) LIMIT 1'
        q_words = "SELECT ?word WHERE { ?_ <http://www.w3.org/2004/02/skos/core#prefLabel> ?word} ORDER BY ASC (?word)"
        # max_ = [int(x) for x, in self.query(q_depth)][0]
        return [str(w) for w, in self.query(q_words)]
        # note that even that's less elegant, python's sorted function
        # works faster that asking sparql engine's ORDER BY
        # q_words = "SELECT ?word WHERE { ?_ <http://www.w3.org/2004/02/skos/core#prefLabel> ?word}"
        # return sorted([str(w) for w, in self.query(q_words)])

    def to_str(self) -> str:
        """return a ttl serialize graph
        if during the serialization, some items have a file:///
        string in their properties, it means the main graph has been merged
        from different graph files"""
        str_ = self.serialize(format="ttl").decode()
        return str_

    def to_text_file(self, out_file=None):
        """return the text with tab indentation
        book
            according to the rules
            account book
            accounts
            arrange
                adapt
                classify
                make arrangements for
                marshal
                organize
                put in order
                settle on
                triage
            bag
                backpack
                bumbag
                carrier bag
                carryall
                catch

        XXX """

        touch(out_file)  # None can be touch ! ??

        def rec_search(uri, str_=None, dep=None, uri_used=[]):
            # print(f"LOOKING FOR {uri} DEP IS {dep} STR STARTSWITH {str(str_)[:10]}") # XXX
            q_words = (
                """SELECT ?uri ?pref ?dep WHERE {
            ?uri <http://www.w3.org/2004/02/skos/core#prefLabel>  ?pref ;
                 <urn:default:baseUri:#depth> ?dep    .
            ?uri ?relation <"""
                + uri
                + "> } ORDER BY ASC (?pref) "
            )
            if not str_:
                str_ = ""
            res = [r for r in self.query(q_words)]
            for new_uri, word, dep in res:
                new_uri = str(new_uri)
                word = str(word)
                dep = int(dep)
                assert type(dep) == int
                assert type(word) == type(new_uri) == str
                if new_uri in uri_used:
                    continue
                uri_used.append(new_uri)

                str_ += "\t" * dep + word + "\n"
                str_ = rec_search(new_uri, str_, dep, uri_used=uri_used)
            return str_

        if not hasattr(self, "root_words") or not getattr(self, "root_words"):
            self._set_root_word_attribute()

        text = rec_search(self.root_word_uri, "\n".join(self.root_words) + "\n")
        if out_file:
            with open(out_file, "w") as f:
                print(text, file=f)
        else:
            return text
        logging.info(f"out file is: '{out_file}'")


if __name__ == "__main__":
    pass
