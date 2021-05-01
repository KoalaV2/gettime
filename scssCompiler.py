import os
import sys
import requests
import min


class scss:
    def __init__(self, path, fileName="") -> None:
        self.path = path
        self.fileName = fileName
        self.minimized = ""

        with open(self.path,"r") as f:
            self.code = f.read()

        if self.fileName == "":
            self.fileName = os.path.basename(path)
    def convertToCSS(self,minimize=False):
        self.code = requests.post('https://jsonformatter.org/service/scssTocss',data={'css':self.code}).text
        if minimize:
            self.code = min.minimize_code(self.code,".css")
        return self.code

if __name__ == "__main__":
    os.system("python min.py \"static/css\" \".scss\"")
