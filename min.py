# Minifies all files in the directory, then places the files in a subfolder called "min".
# Example CMD usage:
# python min.py "\\static\\js" ".js"
# This will go to the folder "static/js" in the root of the file, and minimize all the .js files it can find
# You can also do this:
# python min.py "\\static\\js" ".js" "\\static\\css" ".css"
# So, the formula is:
# python min.py "path to js n" "path to js n+1" "path to js n+2"... ".js"  "path to css n" "path to css n+1" "path to css n+2"... ".css" (and so on)

import os
from sys import argv
from requests import post

# Saves the dir to path of min.py
original_directory = os.path.dirname(os.path.realpath(__file__))

# Contains the link to send the file too for each filetype
urlLookupTable = {
    '.js':'https://javascript-minifier.com/raw',
    '.css':'https://cssminifier.com/raw',
    '.html':'https://html-minifier.com/raw'
}

ignoresNewLine = (
    '.js',
    '.css',
    '.html'
)

def minimize_this(path, fileType):
    """
        Takes a path and a fileType and minimizes the file into a folder called "min".
        Returns the path to the new, minimized file.
    """
    # Fixes the path so that it works
    path = path.replace("\\","/")
    if not path.startswith(original_directory):
        if path.startswith("/"):
            path = original_directory + path
        else:
            path = original_directory + "/" + path
    
    # Changes the working dir to the path with the un-minified files
    os.chdir(path)

    try:os.mkdir("min") # Tries to make a folder, nothing happens if it allready exists
    except:pass

    print(f"\n-- Starting new path: {path}, fileType: {fileType}")
    
    for filename in os.listdir(path):
        if filename.endswith(fileType) and not filename.endswith(f'.min{fileType}'):
            print("- Minifying",filename)
            
            try:
                oldFileName = f"{path}/{filename}"
                newFileName = f'{path}/min/{filename[:-len(fileType)]}.min{fileType}'

                with open(oldFileName, "r", encoding="utf8") as f:
                    file_data = f.read()
                    file_data = file_data.encode("utf-8") # This might be overkill

                a = post(
                    url=urlLookupTable[fileType],
                    data={
                        'input':file_data
                    }
                )
                if a.status_code == 404:
                    print("Statuscode was 404, skipping...")
                    continue

                a = a.text
                if fileType in ignoresNewLine:
                    a = "".join(a.split("\n")) # Removes any new lines if filetype supports it
                
                with open(newFileName, "w", encoding="utf-8") as f:
                    f.write(a)
            
            except Exception as e:
                print(e + ", skipping...")
                continue

    print(f"-- Finished path: {path}, fileType: {fileType}")
    return newFileName

if __name__ == "__main__":
    if len(argv) > 1:
        toMinimize = {}
        currentPaths = [] # Holds the paths untill a filetype is specified
        i=1
        while i < len(argv):
            if argv[i] in urlLookupTable:
                toMinimize[argv[i]] = currentPaths
                currentPaths = []
            else:
                currentPaths.append(argv[i])
            i+=1
    else:
        # Default values
        toMinimize = {
            '.js':[
                "\\static\\js"
            ],
            '.css':[
                "\\static\\css"
            ],
            '.html':[
                "\\templates"
            ]
        }

    for fileType, paths_to_minimize in toMinimize.items():
        for path in paths_to_minimize:
            minimize_this(path=path,fileType=fileType)
