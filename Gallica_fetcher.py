#! /bin/python
import os
import sys
import getopt
import shutil
import urllib.parse
import http.client
from PIL import Image

SIZE_TILE = 2236


class Gallica():

    def __init__(self, id, out):
        self.x = 0
        self.y = 0
        self.id = id + ".f1"
        self.out = out

    def parse_url(url):
        url = urllib.parse.urlparse(url)
        try:
            id = url.path.split("/")[3].split(".")[0]
        except:
            print("Mauvaise Url")
            sys.exit(2)
        return id

    def fetch(self):
        sys.stdout.write("Downloading")
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
                    y += SIZE_TILE
                    res = self.request(x, y)
                    status_y = res.status
                    if status_y == 200:
                        self.create_image(res, x, y)
            x += SIZE_TILE
        sys.stdout.write("\n")
        self.compose()

    def create_image(self, res, x, y):
        sys.stdout.write(".")
        sys.stdout.flush()
        path = "tmp/"
        if not os.path.exists(path):
            os.mkdir(path)
        filename = path + "{0}_{1}_.jpg".format(x, y)
        f = open(filename, 'wb')
        f.write(res.read())
        f.close()

    def compose(self):
        print("Merging images...")
        imageList = sorted(os.listdir("tmp/"))
        totalWidth = 0
        totalHeigth = 0
        for img in imageList:
            pos = img.split("_")
            img = Image.open("tmp/" + img)
            [x, y] = img.size
            if int(pos[0]) == 0:
                totalWidth += x
            if int(pos[1]) == 0:
                totalHeigth += y

        image = Image.new("RGB", (totalWidth, totalHeigth))
        for img in imageList:
            pos = img.split("_")
            paste = Image.open("tmp/" + img)
            image.paste(paste, (int(pos[1]), int(pos[0])))

        image.save(self.out)

        # Delete temp
        shutil.rmtree('tmp/')

    def request(self, x, y):
        data = {}
        data['method'] = 'R'
        data['ark'] = self.id
        data['l'] = 7
        url_values = urllib.parse.urlencode(data)
        gallica = "gallica.bnf.fr"
        url = "/proxy"
        headers = {"Content-type": "application/x-www-form-urlencoded", "User-Agent":
                   "Mozilla/5.0 (X11; Linux x86_64; rv:24.0) Gecko/20100101 Firefox/24.0"}
        full_url = url + '?' + url_values + "&r=" + \
            "{0},{1},{2},{2}".format(x, y, SIZE_TILE)
        conn = http.client.HTTPConnection(gallica)
        conn.request("GET", full_url, "", headers)
        res = conn.getresponse()
        return res


def usage():
    print("Gallica_fetcher.py -u <url> [-o <outputfile>]")


def main():
    url = ''
    outputfile = "out.jpg"
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hu:o:", ["url=", "ofile="])
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
    if url == '':
        print("URL manquante")
        usage()
        sys.exit(2)
    id = Gallica.parse_url(url)
    gallica = Gallica(id, out=outputfile)
    gallica.fetch()


if __name__ == "__main__":
    main()
