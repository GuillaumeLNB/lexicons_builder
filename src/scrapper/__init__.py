# -*- coding: utf-8 -*-
"""This module contains the scrappers that are used to get synonyms from
scpecific websites.
The :meth:`scrappers.get_synonyms` function agregate the results comming from all websites.


List of the websites where the synonyms are comming from:

**French**

* synonymes.com

* dictionnaire-synonymes.com

* les-synonymes.com

* leconjugueur.lefigaro.fr

* crisco2.unicaen.fr

**English**

* lexico.com

* synonyms.com


"""
# TODO make module appears first in documentation


from pkg_resources import get_distribution, DistributionNotFound

try:
    # Change here if project is renamed and does not equal the package name
    dist_name = __name__
    __version__ = get_distribution(dist_name).version
except DistributionNotFound:
    __version__ = "unknown"
finally:
    del get_distribution, DistributionNotFound
