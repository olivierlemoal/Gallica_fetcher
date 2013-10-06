Gallica_fetcher
===========
Gallica_fetcher is a python 3 script to fetch high definition scans from the National Library of France
(on the [Gallica](http://gallica.bnf.fr/) website). Indeed, the website only provide low definition copy to download.

Requirement
----------
- [Pillow](https://pypi.python.org/pypi/Pillow)

Installation
------------

    pip install pillow
    git clone https://github.com/olivierlemoal/Gallica_fetcher.git
    cd Gallica_fetcher

Usage
-----

    gallica_fetcher.py -u <url> [-o <outputfile>]
    
The url you must provide is the one you get when you select a result from a search, for instance :

        http://gallica.bnf.fr/ark:/12148/btv1b84925175.r=carte+nantes.langFR
is a valid link.


Français
======



Gallica_fetcher est un script python3 pour récupérer les versions haute définition des images numérisées de la 
Bibliothèque nationale de France (sur la plateforme [Gallica](http://gallica.bnf.fr/)). En effet le site ne propose que des
versions base définition en téléchargement.

Dépendance
-----------

- [Pillow](https://pypi.python.org/pypi/Pillow)

Installation
------------

    pip install pillow
    git clone https://github.com/olivierlemoal/Gallica_fetcher.git
    cd Gallica_fetcher

Utilisation
-----------

    gallica_fetcher.py -u <url> [-o <outputfile>]
    
Le lien à fournir est celui d'un résultat lors d'une recherche, par exemple:

    http://gallica.bnf.fr/ark:/12148/btv1b84925175.r=carte+nantes.langFR
est un lien valide.
