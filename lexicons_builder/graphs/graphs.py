#!/usr/bin/env python3
"""The Graph package contains the Graph class
that carries the results from scrapping/exploring nlp models etc...
The class inherit from :obj:`rdflib.Graph`.
"""


import logging
from requests.utils import quote

import rdflib
import xlsxwriter
from rdflib.plugins.sparql.parser import parseQuery
from touch import touch


class Graph(rdflib.Graph):
    """same as a :obj:`rdflib.Graph` object (see https://rdflib.readthedocs.io/en/stable/intro_to_creating_rdf.html), but with a few additional methods

    .. code:: python

        >>> from lexicons_builder.graphs.graphs import Graph
        RDFLib Version: 5.0.0
        >>> g = Graph()
        >>> # the graph has a __str__ method that serialize itself to ttl
        >>> print(g)
        @prefix ns1: <http://www.w3.org/2004/02/skos/core#> .
        @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

        <urn:default:baseUri:#holonym> a rdfs:Class ;
            ns1:definition "A term that denotes a whole, a part of which is denoted by a second term. The word \"face\" is a holonym of the word \"eye\"." .

        <urn:default:baseUri:#hypernym> a rdfs:Class ;
            ns1:definition "a word with a broad meaning constituting a category into which words with more specific meanings fall; a superordinate. For example, colour is a hypernym of red." .
        ...

    """

    local_namespace = "urn:default:baseUri:#"
    root_words = []
    root_word_uriref = rdflib.URIRef(f"{local_namespace}root_word")
    base_local = rdflib.Namespace(local_namespace)
    root_word_uri = f"{local_namespace}root_word_uri"

    def __init__(
        self, store="default", identifier=None, namespace_manager=None, base=None
    ):
        super().__init__(
            store=store,
            identifier=identifier,
            namespace_manager=namespace_manager,
            base=base,
        )

        # add the root word,
        self.add(
            (
                self.root_word_uriref,
                rdflib.namespace.RDF.type,
                rdflib.namespace.RDFS.Class,
            )
        )
        self.add(
            (
                self.root_word_uriref,
                rdflib.namespace.SKOS.definition,
                rdflib.Literal(
                    "A root word is the term from which all of the words are fetched"
                ),
            )
        )

        # hyponym
        self.add(
            (
                self.base_local.hyponym,
                rdflib.namespace.RDF.type,
                rdflib.namespace.RDFS.Class,
            )
        )
        self.add(
            (
                self.base_local.hyponym,
                rdflib.namespace.SKOS.definition,
                rdflib.Literal(
                    "Hyponymy is the converse of hypernymy. For example, red is a hyponym of color."
                ),
            )
        )

        # hypernym
        self.add(
            (
                self.base_local.hypernym,
                rdflib.namespace.RDF.type,
                rdflib.namespace.RDFS.Class,
            )
        )
        self.add(
            (
                self.base_local.hypernym,
                rdflib.namespace.SKOS.definition,
                rdflib.Literal(
                    "a word with a broad meaning constituting a category into which words with more specific meanings fall; a superordinate. For example, colour is a hypernym of red."
                ),
            )
        )

        # holonym
        self.add(
            (
                self.base_local.holonym,
                rdflib.namespace.RDF.type,
                rdflib.namespace.RDFS.Class,
            )
        )
        self.add(
            (
                self.base_local.holonym,
                rdflib.namespace.SKOS.definition,
                rdflib.Literal(
                    """A term that denotes a whole, a part of which is denoted by a second term. The word "face" is a holonym of the word "eye"."""
                ),
            )
        )

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

    def word_in_graph(self, word: str) -> bool:
        """return :obj:`True` if the word is in the graph

        .. code:: python

            >>> g = Graph()
            >>> g.add_root_word('dog')
            >>> g.add_word('hound', 1, 'synonym', 'dog', comesFrom='http://example/com')
            >>> g.word_in_graph('cat')
            False
            >>> g.word_in_graph('dog')
            True
            >>> # could be invoked with the in keyword
            >>> 'dog' in g
            True

        """
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
        else:
            # print("it is not")
            return False

    def _check_word_type(self, word):
        "raise a TypeError if type(word)!=str"
        if not isinstance(word, str):
            raise TypeError(
                f"the word you're adding to the graph is not a string instance. It has a '{type(word)}' type"
            )

    def add_word(
        self, word, depth, relation, target_word, synset_uri=None, comesFrom=None
    ):
        """Add some tripples to the graph that contains the relation between the word and its target.

        Args:
            word (str): The word to add to the graph
            deepth (int): The deepth of the reccursion
            relation (str): The relation of the word to the target word.
                            Could be "hyponym", "hypernym", "holonym" or "synonym"
            target_word (str): The word

        .. code:: python

            >>> g = Graph()
            >>> g.add_root_word('car')
            >>> print(g)
            @prefix ns1: <http://www.w3.org/2004/02/skos/core#> .

            <urn:default:baseUri:#root_word_uri> a <urn:default:baseUri:#root_word> ;
                ns1:prefLabel "car" .

            >>> g.add_word('bus', 1, 'synonym', 'car', comesFrom='http://example.com')
            >>> print(g)
            @prefix ns1: <http://www.w3.org/2004/02/skos/core#> .
            @prefix ns2: <urn:default:baseUri:#> .
            @prefix ns3: <http://taxref.mnhn.fr/lod/property/> .
            @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

            ns2:bus ns3:isSynonymOf ns2:root_word_uri ;
                ns1:prefLabel "bus" ;
                ns2:comesFrom <http://example.com> ;
                ns2:depth 1 .

            ns2:root_word_uri a ns2:root_word ;
                ns1:prefLabel "car" .

        """
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
        elif relation == "synonym":
            # word is synonym
            rela = rdflib.URIRef("http://taxref.mnhn.fr/lod/property/isSynonymOf")
        else:
            raise ValueError(
                f"The relation '{relation}' is not implemented in the graph"
            )

        if depth == 1:
            # the relation is linked to the root word
            target = rdflib.URIRef(self.root_word_uri)
        else:
            target = rdflib.URIRef(self.local_namespace + ss_target_word)
        # adding the relation word is synonym/hyponym/... of target word
        self.add(
            (
                rdflib.URIRef(self.local_namespace + ss_word),
                rela,
                target,
            )
        )
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

    def add_root_word(self, word: str):
        """Before searching for related terms, the root word
        from which all synonyms come from should be added to the graph. This method creates rdf tripples for the root word

        Args:
          word (str): The root word to add to the graph

        .. code:: python

            >>> g = Graph()
            >>> g.add_root_word("computer")
            >>> print(g)
            @prefix ns1: <http://www.w3.org/2004/02/skos/core#> .

            <urn:default:baseUri:#root_word_uri> a <urn:default:baseUri:#root_word> ;
                ns1:prefLabel "computer" .

        """
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

    def is_empty(self) -> bool:
        """return :obj:`True` if the graph does not contain synonyms, hyponyms, etc

        If the graph contains only root word(s) or no words, return :obj:`False`
        Note the graph contains some definitions by default

        .. code:: python

            >>> g = Graph()
            >>> g.is_empty()
            True
            >>> g.add_root_word("new")
            >>> g.is_empty()
            True
            >>> g.add_word("young", 1, "synonym", "new")
            >>> g.is_empty()
            False

        """

        for _, p, _ in self:
            if str(p) in (
                "http://taxref.mnhn.fr/lod/property/isSynonymOf",
                "http://www.w3.org/2006/03/wn/wn20/schema/hyponymOf",
                "http://www.w3.org/2006/03/wn/wn20/schema/hypernymOf",
                "http://www.w3.org/2006/03/wn/wn20/schema/holonymOf",
            ):
                return False
        else:
            return True

        # for s, o, p in self:
        #     break
        # else:
        #     return True

    def contains_synonyms(self) -> bool:
        """return :obj:`True` if the graph contains at least one synonym

        .. code:: python

            >>> g = Graph()
            >>> g.add_root_word("new")
            >>> g.contains_synonyms()
            False
            >>> g.add_word("young", 1, "synonym", "new")
            >>> g.contains_synonyms()
            True
        """

        q_check = "ASK {?_ <http://taxref.mnhn.fr/lod/property/isSynonymOf> ?_2}"
        return [r for r in self.query(q_check)][0]

    def _set_root_word_attribute(self):
        """set the root_word and root_word_uri attributes
        by looking at the self.graph"""
        self.root_words = []

        q_root = (
            "SELECT ?uri ?pref WHERE {?uri a <"
            + self.local_namespace
            + """root_word> ;
        <http://www.w3.org/2004/02/skos/core#prefLabel>  ?pref  }"""
        )
        res = [r for r in self.query(q_root)]
        assert res, "The query to get the root word returned no results."
        contains_root_word = False
        for i, (uri, pref) in enumerate(res):
            # self.root_word_uri = str(uri)
            # self.root_word = str(pref)
            self.root_words.append(str(pref))
            contains_root_word = True
        if not contains_root_word:
            raise ValueError(f"The graph does not contain any root word")

        if i:
            logging.warning(
                f"The query to retrive the root word returned several results"
            )
            logging.warning(f"The root words are: {self.root_words}")

    def delete_several_depth(self, method="MIN"):
        """Deletes words with several depths

        Args:
            word (str): The word to add to the graph

        .. code:: python

            >>> g = Graph()
            >>> g.add_root_word('car')
            >>> g.add_word('bus', 1, 'synonym', 'car', comesFrom='http://example/com')
            >>> g.add_word('bus', 2, 'synonym', 'car', comesFrom='http://example/com')
            >>> print(g)
            @prefix ns1: <urn:default:baseUri:#> .
            @prefix ns2: <http://taxref.mnhn.fr/lod/property/> .
            @prefix ns3: <http://www.w3.org/2004/02/skos/core#> .
            @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

            ns1:bus ns2:isSynonymOf ns1:car,
                    ns1:root_word_uri ;
                ns3:prefLabel "bus" ;
                ns1:comesFrom <http://example/com> ;
                ns1:depth 1,
                    2 .

            ns1:root_word_uri a ns1:root_word ;
                ns3:prefLabel "car" .

            >>> g.delete_several_depth()
            >>> print(g)
            @prefix ns1: <urn:default:baseUri:#> .
            @prefix ns2: <http://taxref.mnhn.fr/lod/property/> .
            @prefix ns3: <http://www.w3.org/2004/02/skos/core#> .
            @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

            ns1:bus ns2:isSynonymOf ns1:car,
                    ns1:root_word_uri ;
                ns3:prefLabel "bus" ;
                ns1:comesFrom <http://example/com> ;
                ns1:depth 1 .

            ns1:root_word_uri a ns1:root_word ;
                ns3:prefLabel "car" .

        """
        # TODO should be implemented using one sparql query

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

    def to_list(self) -> list:
        """return a list of all the prefLabels in the graph

        >>> g = Graph()
        >>> g.add_root_word('car')
        >>> g.add_word('bus', 1, 'synonym', 'car', comesFrom='http://example/com')
        >>> g.add_word('truck', 1, 'synonym', 'car', comesFrom='http://example/com')
        >>> g.add_word('vehicle', 1, 'synonym', 'car', comesFrom='http://example/com')
        >>> g.to_list()
        ['bus', 'car', 'truck', 'vehicle']

        """
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
        """return a string containing the serialized graph in the turtle format

        Note that during the serialization, some items might get a file:///
        string in their properties, it means the main graph has been merged
        from different graph files

        >>> g = Graph()
        >>> g.add_root_word('dog')
        >>> str(g)
        '@prefix ns1: <http://www.w3.org/2004/02/skos/core#> .\\n\\n<urn:default:baseUri:#root_word_uri> a <urn:default:baseUri:#root_word> ;\\n    ns1:prefLabel "dog" .\\n\\n'

        """
        str_ = self.serialize(format="ttl").decode()
        return str_

    def to_text_file(self, out_file=None):
        """write the graph to the path provided.

        Args:
            out_file (str, optional): The outfile path. If None, returns the string

        Example of file:

        .. code:: python

            book                    # the root word
                Bible               # a 1st rank synonym, linked to 'book'
                    Holy_Writ       # a 2nd rank synonym, linked to 'Bible'
                    Scripture       # a 2nd rank synonym, linked to 'Bible'
                    Word            # a 2nd rank synonym, linked to 'Bible'
                 Epistle            # a 1st rank synonym, linked to 'book'
                     letter         # a 2nd rank synonym, linked to 'Epistle'
                     missive        # a 2nd rank synonym, linked to 'Epistle'
        """

        touch(out_file)  # None can be touch ! ??

        def rec_search(uri, str_=None, dep=None, uri_used=[]):
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

    def to_xlsx_file(self, out_file: str):
        """Save the graph to an excel file

        Args:
            out_file (str): The outfile path

        """

        self._set_root_word_attribute()
        workbook = xlsxwriter.Workbook(out_file)
        worksheet = workbook.add_worksheet()
        worksheet.write(0, 0, "root word(s)")
        worksheet.write(0, 1, ", ".join(self.root_words))

        # ?origin
        # <urn:default:baseUri:#comesFrom> ?origin ;

        q_words_depth = """SELECT ?word ?depth
                    WHERE { ?_ <http://www.w3.org/2004/02/skos/core#prefLabel> ?word ;
                    <urn:default:baseUri:#depth> ?depth ;
                    }
                    ORDER BY ASC (?word)"""
        for i, (word, depth,) in enumerate(
            self.query(q_words_depth), start=2
        ):  # origin
            worksheet.write(i, 0, word)
            worksheet.write(i, 1, depth)
            # worksheet.write(i, 2, origin)
        workbook.close()
        logging.info(f"out file is: '{out_file}'")


if __name__ == "__main__":
    pass
