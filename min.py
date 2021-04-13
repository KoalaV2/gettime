# Minifies all files in the directory, then places the files in a subfolder called "min".

from os import listdir
from os import getcwd
from os import mkdir
from requests import post
from sys import argv

directory = getcwd()
fileType = ".js" if len(argv) < 2 else argv[1]

urlLookupTable = {
    '.js':'https://javascript-minifier.com/raw',
    '.css':'https://cssminifier.com/raw',
    '.html':'https://html-minifier.com/raw'
}

try:mkdir("min")
except:pass
for filename in listdir(directory):
    if filename.endswith(fileType) and not filename.endswith(f'.min{fileType}'):
        print("Minifying",filename)

        with open(f"{directory}\\{filename}","r", encoding="utf8") as f:
            a = post(url=urlLookupTable[fileType],data={'input':f.read().encode("utf-8")})
        
        with open(f'{directory}\\min\\{filename[:-len(fileType)]}.min{fileType}',"w", encoding="utf-8") as f:
            f.write("".join(a.text.split("\n")))
print("Done!")