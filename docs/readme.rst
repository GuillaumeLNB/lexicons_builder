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

Full documentation available on `readthedocs`_


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
.. _readthedocs: https://lexicons-builder.readthedocs.io/en/latest/index.html
