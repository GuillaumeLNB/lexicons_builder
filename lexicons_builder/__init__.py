import logging

logging.basicConfig(
    # level=logging.INFO,
    level=logging.DEBUG,
    format="[%(asctime)s] -[%(name)s] - [%(levelname)s] - %(message)s",
    handlers=[logging.StreamHandler()],
)

from lexicons_builder.nlp_model_explorer.explorer import explore_nlp_model
from lexicons_builder.scrappers.scrappers import get_synonyms_from_scrappers
from lexicons_builder.wordnet_explorer.explorer import explore_wordnet, explore_wolf


def build_lexicon(
    words: list,
    lang: str,
    depth: int,
    nlp_model_paths: list = [],
    wolf_path: str = None,
    wordnet: bool = False,
    web: bool = True,
):
    """This is the main function to build lexicons.

    Args:
      words ([str]): List of words
      lang (str): The language in ISO-639-1 (fr, en, de, ...)
      depth (int): The depth to which it will go
      nlp_model_paths ([str], optional): List of path to the nlp models
      wolf_path (str, optional): The path to WOLF
      wordnet (bool, optional): Retrieve related terms using WordNet
      web (bool, optional): Retrieve related terms looking online

    Returns:
        :obj:`lexicons_builder.Graph`: a :py:meth:`lexicons_builder.Graph` object that contains the results.

    .. code:: python

        >>> from lexicons_builder import build_lexicon
        >>> # search for words related to 'book' and 'read'
        >>> # in WordNet and online
        >>> g = build_lexicon(['book', 'read'], 'en', 1, wordnet=True, web=True)
        >>> print(g)
        @prefix ns1: <http://www.w3.org/2004/02/skos/core#> .
        @prefix ns2: <urn:default:baseUri:#> .
        @prefix ns3: <http://taxref.mnhn.fr/lod/property/> .
        @prefix ns4: <http://www.w3.org/2006/03/wn/wn20/schema/> .
        @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

        ns2:note ns3:isSynonymOf ns2:root_word_uri ;
            ns1:prefLabel "note" ;
            ns2:comesFrom <synonyms.reverso.net> ;
            ns2:depth 1 .

        ns2:learned ns3:isSynonymOf ns2:root_word_uri ;
            ns1:prefLabel "learned" ;
            ns2:comesFrom <synonyms.com> ;
            ns2:depth 1 .
        ...
        >>> g.to_list()
        ['Bible', 'Book', 'Christian_Bible', 'Epistle', 'Good_Book', 'Holy_Scripture', 'Holy_Writ', 'Koran', 'PS', 'Quran', 'Scripture', 'Word', 'Word_of_God', 'accept', 'accommodate', 'according to the rules', 'account book', 'account_book', 'accountability', 'accountancy', 'accountant', 'accounting', 'accounts', 'accumulation', 'accuse', 'acquire', 'act', 'adjudge', 'admit', 'adopt', 'afl', 'aggregation', 'agree', 'aim', "al-Qur'an"
        ...
        >>> print(g.to_text_file())
        book
        read
            Bible
            Book
            Christian_Bible
            Epistle
            Good_Book
            Holy_Scripture
            Holy_Writ
            Koran
            PS
            Quran
        ...

    """

    assert isinstance(words, list)
    graphs = []
    for word in words:
        assert isinstance(word, str)
        if nlp_model_paths:
            for model in nlp_model_paths:
                # looking for words in nlp models
                logging.info(
                    f"exploring model '{model}' with word '{word}' at {depth} depth"
                )
                graphs.append(explore_nlp_model(word, model, depth))
        # looking for words online
        if web:
            logging.info(
                f"looking up synonyms online for word '{word}' at depth {depth}"
            )
            graphs.append(get_synonyms_from_scrappers(word, lang, depth))
        # looking for word with WOLF
        if wolf_path:
            logging.info(
                f"exploring WOLF with word '{word}' at depth {depth} WOLF PATH IS '{wolf_path}'"
            )
            graphs.append(explore_wolf(word, wolf_path, depth, seeds=words))
        # looking for word with WORDNET
        if wordnet:
            logging.info(f"exploring WORNET with word '{word}' at depth {depth}")
            graphs.append(explore_wordnet(word, lang, depth))

    # merging the graphs
    main_graph = graphs[0]
    for g in graphs[1:]:
        main_graph += g
    # setting the root words attributes
    main_graph._set_root_word_attribute()
    main_graph.delete_several_depth()

    return main_graph
