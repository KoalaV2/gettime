import os
import requests

directory = os.path.dirname(__file__)
print(directory)


for filename in os.listdir(directory):
    if filename.endswith(".js"):
        print(filename)
        with open(f"{directory}\\{filename}","r") as f:
            a = requests.post(url='https://javascript-minifier.com/raw',data={'input':f.read()})

        with open(f'{directory}\\min\\{filename[:-3]}.min.js',"w") as f:
            f.write(a.text)
        

# for fileName in ():
#     