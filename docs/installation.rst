Installation
------------

With pip
~~~~~~~~
    .. code:: bash

        $ pip install lexicons-builder


From source
~~~~~~~~~~~
To install the module from source:

    .. code:: bash

        $ pip install git+git://github.com/GuillaumeLNB/lexicons_builder

Download NLP models (optionnal)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Here's a non exhaustive list of websites where you can download NLP models manually.
The models should be in word2vec or fasttext format.

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
| https://github.com/mmihaltz/word2vec-GoogleNews-vectors   | English                |
+-----------------------------------------------------------+------------------------+


Download WOLF (French WordNet) (optionnal)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    .. code:: bash

        $ # download WOLF (French wordnet if needed)
        $ wget https://gforge.inria.fr/frs/download.php/file/33496/wolf-1.0b4.xml.bz2
        $ # (and extract it)
        $ bzip2 -d wolf-1.0b4.xml.bz2