#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import getopt
import shutil
import urllib.parse
import http.client
import tempfile
from PIL import Image


class PageException(Exception):
    """
        Exception used for non-existent pages
    """

    def __init__(self, value):
        print(value, file=sys.stderr)


class Gallica:
    """
        A Gallica object (map, book...) identified by his id. The object can have multiple pages.
    """

    SIZE_TILE = 2236  # max square tile size allowed to be requested by the server
    TEMP = tempfile.mkdtemp() + "/"

    def __init__(self, id, output_filename, page_min, page_max):
        """
            :param id: id of the object to fetch on the server
            :param output_filename: name of the resulting file without extension
            :param page_min: page where the fetching starts
            :param page_max: page where the fetching stops
        """
        self.x = 0
        self.y = 0
        self.id = id
        self.page = page_min
        self.page_max = page_max
        self.output_filename = output_filename

    @staticmethod
    def parse_url(url):
        """
            Parse the url provided with -u to extract the id of the object.
        """
        url = urllib.parse.urlparse(url)
        try:
            id = url.path.split("/")[3].split(".")[0]
        except:
            print("Invalid Url", file=sys.stderr)
            sys.exit(2)
        return id

    def fetch_all(self):
        """
            Fetch all the pages requested by the user.
        """
        while self.page <= self.page_max:
            self.fetch()
            self.page += 1

    def fetch(self):
        """
            Fetch the tiles for a page of the object.
        """
        sys.stdout.write("Downloading page {0}".format(self.page))
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
        """
            Save the tile in a temporary directory.
        """
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
        """
            Assemble all the tiles together and save the final picture.
        """
        print("Assembling picture...")
        imageList = sorted(os.listdir(self.TEMP))
        if not imageList:
            # If imageList is empty, no tiles were fetched so the page doesn't exist
            raise PageException("The page doesn't exist")
        total_width = 0
        total_heigth = 0
        for img in imageList:
            pos = img.split("_")
            img = Image.open(self.TEMP + img)
            [x, y] = img.size
            if int(pos[0]) == 0:
                total_width += x
            if int(pos[1]) == 0:
                total_heigth += y

        image = Image.new("RGB", (total_width, total_heigth))
        for img in imageList:
            pos = img.split("_")
            paste = Image.open(self.TEMP + img)
            image.paste(paste, (int(pos[1]), int(pos[0])))

        save_name = "{0}_{1}.jpg".format(self.output_filename, self.page)
        image.save(save_name)
        print("Picture saved : {0}".format(save_name))

        # Delete temp
        shutil.rmtree(self.TEMP)

    def request(self, x, y):
        """
            Create a request to get the tile on the Gallica server.
        """
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
        conn = http.client.HTTPSConnection(gallica)
        conn.request("GET", full_url, "", headers)
        res = conn.getresponse()
        return res


def usage():
    """
        Print the usage on the stdout.
    """
    print(
        "Usage : gallica_fetcher -u <url> [-o <output_filename>] [-p <firstPage>[-<lastPage>]]")
    print("Exemples :")
    print("gallica_fetcher.py -u <url> -p 1-12 -o extract")
    print("gallica_fetcher.py -u <url> -p 13")
    print("gallica_fetcher.py -u <url>")


def main():
    """
        Parse arguments and start fetching.
    """
    url = ''
    output_filename = "gallica"
    page_min, page_max = (1, 1)
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
            output_filename = arg
        elif opt in ("-p", "--pages"):
            try:
                if "-" in arg:
                    page_min, page_max = arg.split("-")
                    page_min = int(page_min)
                    page_max = int(page_max)
                else:
                    page_min = int(arg)
                    page_max = page_min
                if page_max < page_min:
                    raise ValueError
                if page_min == 0:
                    print("First page must be at least 1", file=sys.stderr)
                    raise ValueError
            except ValueError:
                print("Invalid page syntax", file=sys.stderr)
                usage()
                sys.exit(2)
    if not url:
        print("Missing Url", file=sys.stderr)
        usage()
        sys.exit(2)
    id = Gallica.parse_url(url)
    gallica = Gallica(id, output_filename=output_filename, page_min=page_min, page_max=page_max)
    gallica.fetch_all()


if __name__ == "__main__":
    main()
