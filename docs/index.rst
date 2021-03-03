==============================
lexicons_builder documentation
==============================

The **lexicons_builder** package aims to provide a basic API to create lexicons related to specific words.


**Key principle**: Given the input words, the main algorithm will look for synonyms and neighboors in the synonym dictionaries, in the NLP model(s) provided and in WordNet. For each of the new retreiven terms, it will look again for its neighboors or synonyms and so on..

The general method is implemented on 3 different supports:

1) Synonyms dictionaries (See complete list of the dictionaries :doc:`here <list_dictionaries>`)
2) NLP language models (Word2Vec format)
3) `WordNet`_ (or `WOLF`_)


Output can be text file, turtle file or a Graph object. See :doc:`Quickstart <quickstart>` section for examples.


.. note::
    The synonyms comming from the web are retreived by scrapping each webpage.
    Which means that a change in the html might return wrong results.



Contents
========

.. toctree::
   :maxdepth: 2

   License <license>
   Authors <authors>
   Changelog <changelog>
   Installation <installation>
   Quickstart <quickstart>

   Module Reference <api/modules>
   List of dictionaries <list_dictionaries>

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`




.. note::
    If there's an issue, feel free to open a ticket or drop me a line at guillaume.le-noe-bienvenu@irisa.fr


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