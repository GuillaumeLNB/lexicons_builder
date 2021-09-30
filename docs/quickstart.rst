QuickStart
------------

Command line interface (CLI)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To get words from input words through CLI, run


    .. code:: bash

        $ python -m lexicons_builder <words>  \
              --lang <LANG>                 \
              --out-file <OUTFILE>          \
              --format <FORMAT>             \
              --depth <DEPTH>               \
              --nlp-model <NLP_MODEL_PATHS> \
              --web                         \
              --wordnet                     \
              --wolf-path <WOLF_PATH>       \
              --strict

With:
  * ``<words>`` The word(s) we want to get synonyms from
  * ``<LANG>`` The word language (eg: *fr*, *en*, *nl*, ...)
  * ``<DEPTH>`` The depth we want to dig in the models, websites, ...
  * ``<OUTFILE>`` The file where the results will be stored
  * ``<FORMAT>`` The wanted output format (txt with indentation, ttl or xlsx)
At least ONE of the following options is needed:
  * ``--nlp-model <NLP_MODEL_PATHS>`` The path to the nlp model(s)
  * ``--web`` Search online for synonyms
  * ``--wordnet`` Search on WordNet using nltk
  * ``--wolf-path <WOLF_PATH>`` The path to WOLF (French wordnet)
Optional
  * ``--strict`` remove non relevant words

**Eg:** if we want to look for related terms linked to 'eat' and 'drink' on wordnet at a depth of 2, excecute:

    .. code:: bash

        $ python -m lexicons_builder eat drink  \
              --lang        en                  \
              --out-file    test_en.txt         \
              --format      txt                 \
              --depth       1                   \
              --wordnet
        $ Note the indentation is linked to the depth a which the word was found
        $ head test_en.txt
          drink
          eat
            absorb
            ade
            aerophagia
            alcohol
            alcoholic_beverage
            alcoholic_drink
            banquet
            bar_hop
            belt_down
            beverage
            bi
          ...




Python
~~~~~~

To get related terms interactively through Python, run

    .. code:: python

        >>> from lexicons_builder import build_lexicon
        >>> # search for related terms of 'book' and 'read' in English at depth 1 online
        >>> output = build_lexicon(["book", "read"], 'en', 1, web=True)
        ...
        >>> # we then get a graph object
        >>> # output as a list
        >>> output.to_list()
        ['PS', 'accept', 'accommodate', 'according to the rules', 'account book', 'accountability', 'accountancy', 'accountant', 'accounting', 'accounts', 'accuse', 'acquire', 'act', 'adjudge', 'admit', 'adopt', 'afl', 'agree', 'aim', "al-qur'an", 'album', 'allege', 'allocate', 'allow', 'analyse', 'analyze', 'annuaire', 'anthology', 'appear in reading', 'apply', 'appropriate', 'arrange', 'arrange for', 'arrest', 'articulate', 'ascertain' ...
        >>> # output as rdf/turtle
        >>> print(output)
        @prefix ns1: <http://taxref.mnhn.fr/lod/property/> .
        @prefix ns2: <urn:default:baseUri:#> .
        @prefix ns3: <http://www.w3.org/2004/02/skos/core#> .
        @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

        ns2:PS ns1:isSynonymOf ns2:root_word_uri ;
            ns3:prefLabel "PS" ;
            ns2:comesFrom <synonyms.com> ;
            ns2:depth 1 .

        ns2:accept ns1:isSynonymOf ns2:root_word_uri ;
            ns3:prefLabel "accept" ;
            ns2:comesFrom <synonyms.com> ;
            ns2:depth 1 .
        ...

        >>> # output to an indented file
        >>> output.to_text_file("filename.txt")
        >>> with open("filename.txt") as f:
        ...     print(f.read(1000))
        ...
        read
        book
          PS
          accept
          accommodate
          according to the rules
          account book
          accountability
        ...
        >>> # output to xslx file
        >>> output.to_xlsx_file("results.xlsx")

        >>> # full search with 2 nlp models, wordnet and on the web
        >>> # download and extract google word2vec model
        >>> # from https://github.com/mmihaltz/word2vec-GoogleNews-vectors
        >>>
        >>> # download and extract FastText models
        >>> # from https://fasttext.cc/docs/en/english-vectors.html
        >>>
        >>> nlp_models = ["GoogleNews-vectors-negative300.bin", "wiki-news-300d-1M.vec"]
        >>> output = build_lexicon(["book", "letter"], "en", 1, web=True, wordnet=True, nlp_model_paths=nlp_models)
        >>> # can take a while
        >>> len(output.to_list())
        614
        >>> # deleting non relevant words
        >>> output.pop_non_relevant_words()
        >>> len(output.to_list())
        57




.. note::
    If the depth parameter is too high (higher than 3), the words found could seem unrelated to the root words. It can take also a long time to compute too.

.. note::
    The word senses are taken equally, which means that you might get terms you would think are not related to the input word.
    Eg: looking for the word 'test' might give you words linked to Sea urchins, as a 'test' is also a type of shell https://en.wikipedia.org/wiki/Test_(biology).


.. _GitHub: https://github.com/GuillaumeLNB/lexicons_builder/issues