#!/usr/bin/env python3
from requests.utils import quote

import rdflib
from touch import touch


class Graph(rdflib.Graph):
    """same as rdflib.Graph object, but with a few additional methods"""

    local_namespace = "urn:default:baseUri:#"

    def __contains__(self, word):
        return self.word_in_graph(word)

    def __str__(self):
        # quick way of serializing the graph to ttl
        return self.to_str()

    def word_in_graph(self, word):
        """return True if the word is in the graph"""
        # checks if the word is already in the graph
        query_check = (
            'ASK {?_ <http://www.w3.org/2004/02/skos/core#prefLabel>  "' + word + '"}'
        )
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

    def add_word(self, word, depth, relation, target_word, synset_uri=None):
        "add the word to the graph"
        self._check_word_type(word)
        # to avoid unvalid URI
        # as some wordnet words do have unwanted characters
        ss_word = quote(word)
        ss_target_word = quote(target_word)
        assert ss_word != ss_target_word

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

        # adding the relation word is synonym/hyponym/... of target word
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
        if synset_uri:
            self.add(
                (
                    rdflib.URIRef(self.local_namespace + ss_word),
                    base_local.synsetLink,
                    rdflib.URIRef(synset_uri),
                )
            )

    def add_root_word(self, word):
        "add the root word to the graph"
        self.root_word = word
        self.root_word_uri = f"{self.local_namespace}{self.root_word}"
        self._check_word_type(word)

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

    def _set_root_word(self):
        """set the root_word and root_word_uri attributes
        by looking at the self.graph"""
        q_root = (
            "SELECT ?uri ?pref WHERE {?uri a <"
            + self.local_namespace
            + """root_word> ;
        <http://www.w3.org/2004/02/skos/core#prefLabel>  ?pref  }"""
        )

        for uri, pref in self.query(q_root):
            self.root_word_uri = str(uri)
            self.root_word = str(pref)
            break
        else:
            raise ValueError(
                "The query to retrive the root word returned several results"
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
        "return a ttl serialize graph"
        return self.serialize(format="ttl").decode()

    def to_text_file(self, out_file):
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

        touch(out_file)

        def rec_search(uri, str_=None):
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
            for new_uri, word, dep in self.query(q_words):
                new_uri = str(new_uri)
                word = str(word)
                dep = int(dep)
                assert type(dep) == int
                assert type(word) == type(new_uri) == str
                str_ += "\t" * dep + word + "\n"
                str_ = rec_search(new_uri, str_)
            return str_

        if not hasattr(self, "root_word"):
            self._set_root_word()
        text = rec_search(self.root_word_uri, self.root_word + "\n")
        with open(out_file, "w") as f:
            print(text, file=f)
        print(out_file)


if __name__ == "__main__":
    pass
