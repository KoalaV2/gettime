# Uses https://javascript-minifier.com/api to minify all JS files in the directory.
# It then places the files in a subfolder called "min".

from os import listdir
from os.path import dirname
from requests import post

directory = dirname(__file__)
fileType = ".js" #.js is the only one implomented at this time.

urlLookupTable = {
    '.js':'https://javascript-minifier.com/raw'
}

for filename in listdir(directory):
    if filename.endswith(fileType):
        print("Minifying",filename)

        with open(f"{directory}\\{filename}","r") as f:
            a = post(url=urlLookupTable[fileType],data={'input':f.read()})
        
        with open(f'{directory}\\min\\{filename[:-len(fileType)]}.min{fileType}',"w") as f:
            f.write(a.text)
input("\nDone!\nPress Enter to exit!\n")