================
lexicons_builder
================


The **lexicons_builder** package aims to provide a basic API to create lexicons related to specific words.


**Key principle**: Given the input words, it will look for synonyms or neighboors in the dictionnaries or in the NLP model. For each of the new retreiven terms, it will look again for its neighboors or synonyms and so on..

The general method is implemented on 3 different supports:

1) Synonyms dictionnaries (See list of the dictionnaries : ref:`here <list_dictionnaries.rst>`)
2) NLP language models
3) `WordNet`_ (or `WOLF`_)


Output can be text file, turtle file or a Graph object. See <Quickstart> section for examples.


Note
====

Feel free to raise an issue or drop me a line at guillaume.le-noe-bienvenu@irisa.fr if something isn't working for you.


.. _toctree: http://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html
.. _reStructuredText: http://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html
.. _references: http://www.sphinx-doc.org/en/stable/markup/inline.html
.. _Python domain syntax: http://sphinx-doc.org/domains.html#the-python-domain
.. _Sphinx: http://www.sphinx-doc.org/
.. _Python: http://docs.python.org/
.. _Numpy: http://docs.scipy.org/doc/numpy
.. _SciPy: http://docs.scipy.org/doc/scipy/reference/
.. _matplotlib: https://matplotlib.org/contents.html#
.. _Pandas: http://pandas.pydata.org/pandas-docs/stable
.. _Scikit-Learn: http://scikit-learn.org/stable
.. _autodoc: http://www.sphinx-doc.org/en/stable/ext/autodoc.html
.. _WordNet: https://wordnet.princeton.edu/
.. _WOLF: http://alpage.inria.fr/~sagot/

Installation
------------
From source
~~~~~~~~~~~
To install the module, clone it from gitlab.



    .. code:: bash

        $ git clone git@github.com:GuillaumeLNB/lexicons_builder.git
        $ cd lexicons_builder/
        $ pip install .


With pip
~~~~~~~~
Coming soon XXX

Download NLP models (optionnal)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Here's a non exhaustive list of models you can download manually.
The models should be in word2vec format.

+-----------------------------------------------------------+------------------------+
| Link                                                      | Language(s)            |
+===========================================================+========================+
| https://fauconnier.github.io/#data                        | French                 |
+-----------------------------------------------------------+------------------------+
| https://wikipedia2vec.github.io/wikipedia2vec/pretrained/ | Multilingual           |
+-----------------------------------------------------------+------------------------+
| http://vectors.nlpl.eu/repository/                        | Multilingual           |
+-----------------------------------------------------------+------------------------+
| https://github.com/alexandres/lexvec#pre-trained-vectors  | Multilingual           |
+-----------------------------------------------------------+------------------------+
| https://fasttext.cc/docs/en/english-vectors.html          | English / Multilingual |
+-----------------------------------------------------------+------------------------+

Download WOLF (French WordNet) (optionnal)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    .. code:: bash

        $ # download WOLF (French wordnet if needed)
        $ wget https://gforge.inria.fr/frs/download.php/file/33496/wolf-1.0b4.xml.bz2
        $ # (and extract it)
        $ bzip2 -d wolf-1.0b4.xml.bz2

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
              --wolf-path <WOLF_PATH>

With:
  * ``<words>`` The word(s) we want to get synonyms from
  * ``<LANG>`` The word language (eg: *fr*, *en*, *nl*, ...)
  * ``<DEPTH>`` The depth we want to dig in the models, websites, ...
  * ``<OUTFILE>`` The file where the results will be stored
  * ``<FORMAT>`` The wanted output format (txt with indentation or ttl)
At least ONE of the following options is needed:
  * ``--nlp-model <NLP_MODEL_PATHS>`` The path to the nlp model(s)
  * ``--web`` Search online for synonyms
  * ``--wordnet`` Search on WordNet using nltk
  * ``--wolf-path <WOLF_PATH>`` The path to WOLF (French wordnet)

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
        >>> output = build_lexicon(['book', 'read'], 'en', 1, web=True)
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

        >>> # Output to an indented file
        >>> output.to_text_file('filename.txt')
        >>> with open('filename.txt') as f:
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



.. note::
    If the depth parameter is too high (higher than 3), the words found could seem unrelated to the root words. It can take also a long time to compute too.

.. note::
    The word senses are taken equally, which means that you might get terms you would think are not related to the input word.
    Eg: looking for the word 'test' might give you words linked to Sea urchins, as a 'test' is also a type of shell https://en.wikipedia.org/wiki/Test_(biology)