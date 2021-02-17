// SAVES AND LOADS URLS FROM BLOCKS

// KNOWN ISSUES:
// Can not click the text itself (fixable)

// This is run as the new schedule is passed in.
function checkMyUrl(theID,className) {
    var parentBlock = $("#"+theID.toString());
    var cookieLoad = readCookie("URL_" + className);
    
    // Prepares the onclick action
    parentBlock.attr("onclick", "iWasClicked('" + theID + "','" + className + "')");
    
    // If there is a saved URL, it loads it in aswell
    if (cookieLoad != null){
        parentBlock.attr("savedURL", cookieLoad);
    }

}

function iWasClicked(theID,className){
    var parentBlock = $("#"+theID.toString());
    var cookieLoad = readCookie("URL_" + className);
    
    // If there is a saved URL it asks you what you want to save in the block
    if (cookieLoad == null){
        var newURL = prompt("Please enter the url you want to store here", "");
        
        // Checks if the user cancelled the input
        if (newURL != null){
            createCookie("URL_" + className,newURL,365)
            parentBlock.attr("savedURL", newURL);
        }

    }
    // If there IS a cookie saved, it opens that URL
    else{
        window.open(cookieLoad);
    }
    
}

function getAllCookieNamesThatStartWith(shouldStartWith){
    var toReturn = [];

    var cookies = document.cookie.split(";");
    for (var i = 0; i < cookies.length; i++) {
        var cookie = cookies[i];
        var eqPos = cookie.indexOf("=");
        var name = eqPos > -1 ? cookie.substr(0, eqPos) : cookie;

        if (name.trim().startsWith(shouldStartWith)){
            toReturn.push(name.trim());
        }
    }
    return toReturn;
}

function deleteAllURLCookies() {
    getAllCookieNamesThatStartWith("URL_").forEach(element => eraseCookie(element));
    showSaved();

}
