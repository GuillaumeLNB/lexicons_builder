Installation
------------
From git
~~~~~~~~
To install the module, clone it from gitlab.



    .. code:: bash

        $ git clone git@gitlab.inria.fr:glenoebi/lexicons_builder.git
        $ cd lexicons_builder/

        # download WOLF (French wordnet if needed)
        wget https://gforge.inria.fr/frs/download.php/file/33496/wolf-1.0b4.xml.bz2
        # (and extract it)
        bzip2 -d wolf-1.0b4.xml.bz2

Install the requirements:

    .. code:: bash

        $ pip install -r requirements.txt

With pip
~~~~~~~~
XXX

Download NLP models (optionnal)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Here's a list of models you can download manually. This list is not exhaustive.
The models should be in word2vec format
https://fauconnier.github.io/#data



tested Yes/no
