Installation
------------
From source
~~~~~~~~~~~
To install the module from github:


    .. code:: bash

        $ pip install git+git://github.com/GuillaumeLNB/lexicons_builder

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