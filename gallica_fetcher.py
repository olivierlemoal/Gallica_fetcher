#! /bin/python
import os
import sys
import getopt
import shutil
import urllib.parse
import http.client
import tempfile
from PIL import Image


class PageException(Exception):

    def __init__(self, value):
        print(value)


class Gallica:

    SIZE_TILE = 2236
    TEMP = tempfile.mkdtemp() + "/"

    def __init__(self, id, out, pageMin, pageMax):
        self.x = 0
        self.y = 0
        self.id = id
        self.page = pageMin
        self.pageMax = pageMax
        self.out = out

    @staticmethod
    def parse_url(url):
        url = urllib.parse.urlparse(url)
        try:
            id = url.path.split("/")[3].split(".")[0]
        except:
            print("Mauvaise Url")
            sys.exit(2)
        return id

    def fetch_all(self):
        while self.page <= self.pageMax:
            self.fetch()
            self.page += 1

    def fetch(self):
        sys.stdout.write("Téléchargement de la page {0}".format(self.page))
        sys.stdout.flush()
        x = 0
        status_x = 200
        while status_x == 200:
            y = 0
            res = self.request(x, y)
            status_x = res.status
            if status_x == 200:
                self.create_image(res, x, y)
                status_y = 200
                while status_y == 200:
                    y += self.SIZE_TILE
                    res = self.request(x, y)
                    status_y = res.status
                    if status_y == 200:
                        self.create_image(res, x, y)
            x += self.SIZE_TILE
        sys.stdout.write("\n")
        try:
            self.compose()
        except PageException:
            sys.exit(2)

    def create_image(self, res, x, y):
        sys.stdout.write(".")
        sys.stdout.flush()
        path = self.TEMP
        if not os.path.exists(path):
            os.mkdir(path)
        filename = path + "{0}_{1}_.jpg".format(x, y)
        f = open(filename, 'wb')
        f.write(res.read())
        f.close()

    def compose(self):
        print("Composition de l'image...")
        imageList = sorted(os.listdir(self.TEMP))
        if not imageList:
            raise PageException("Page non existante")
        totalWidth = 0
        totalHeigth = 0
        for img in imageList:
            pos = img.split("_")
            img = Image.open(self.TEMP + img)
            [x, y] = img.size
            if int(pos[0]) == 0:
                totalWidth += x
            if int(pos[1]) == 0:
                totalHeigth += y

        image = Image.new("RGB", (totalWidth, totalHeigth))
        for img in imageList:
            pos = img.split("_")
            paste = Image.open(self.TEMP + img)
            image.paste(paste, (int(pos[1]), int(pos[0])))

        saveName = "{0}_{1}.jpg".format(self.out, self.page)
        image.save(saveName)
        print("Image sauvegardée : {0}".format(saveName))

        # Delete temp
        shutil.rmtree(self.TEMP)

    def request(self, x, y):
        data = {}
        data['method'] = 'R'
        data['ark'] = "{0}.f{1}".format(self.id, self.page)
        data['l'] = 7
        url_values = urllib.parse.urlencode(data)
        gallica = "gallica.bnf.fr"
        url = "/proxy"
        headers = {"Content-type": "application/x-www-form-urlencoded", "User-Agent":
                   "Mozilla/5.0 (X11; Linux x86_64; rv:24.0) Gecko/20100101 Firefox/24.0"}
        full_url = url + '?' + url_values + "&r=" + \
            "{0},{1},{2},{2}".format(x, y, self.SIZE_TILE)
        conn = http.client.HTTPConnection(gallica)
        conn.request("GET", full_url, "", headers)
        res = conn.getresponse()
        return res


def usage():
    print(
        "gallica_fetcher.py -u <url> [-o <outputfile>] [-p <firstPage>[-<lastPage>]]")
    print("Exemples :")
    print("gallica_fetcher.py -u <url> -p 1-12 -o extrait")
    print("gallica_fetcher.py -u <url> -p 13")
    print("gallica_fetcher.py -u <url>")


def main():
    url = ''
    outputfile = "gallica"
    pageMin, pageMax = (1, 1)
    try:
        opts, args = getopt.getopt(
            sys.argv[1:], "hu:o:p:", ["url=", "ofile=", "pages="])
    except getopt.GetoptError as err:
        print(err)
        usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            usage()
            sys.exit()
        elif opt in ("-u", "--url"):
            url = arg
        elif opt in ("-o", "--ofile"):
            outputfile = arg
        elif opt in ("-p", "--pages"):
            try:
                if "-" in arg:
                    pageMin, pageMax = arg.split("-")
                    pageMin = int(pageMin)
                    pageMax = int(pageMax)
                else:
                    pageMin = int(arg)
                    pageMax = pageMin
                if pageMax < pageMin:
                    raise ValueError
                if pageMin == 0:
                    print("La numérotation des pages commence à 1")
                    raise ValueError
            except ValueError:
                print("Syntaxe des pages invalide")
                usage()
                sys.exit(2)
    if url == '':
        print("URL manquante")
        usage()
        sys.exit(2)
    id = Gallica.parse_url(url)
    gallica = Gallica(id, out=outputfile, pageMin=pageMin, pageMax=pageMax)
    gallica.fetch_all()


if __name__ == "__main__":
    main()
