R implementation
================

R
~

It is possible to call this package from R using the `reticulate`_ librairy

    .. code:: R

        > library(reticulate)
        > lexicons_builder <- import('lexicons_builder')
        > test <-lexicons_builder$build_lexicon(list('manger'), 'fr', as.integer(1))
        >  test$to_list()
        [1] "absorber"            "agapes"              "aliment"
        [4] "alimentation"        "alimenter"           "allaiter"
        [7] "aneantir"            "annihiler"           "attaquer"
        [10] "avaler"              "bafrer"              "banquet"
        [13] "becqueter"           "bouffe"              "bouffer"
        [16] "boulotter"           "boustifailler"       "bredouiller"
        [19] "brichetonner"        "briffer"             "brouter"
        [22] "broyer"              "bruler"              "casser la croute"
        ...
        > test$to_text_file('test.txt')



.. _reticulate: https://cran.r-project.org/web/packages/reticulate/vignettes/calling_python.html
