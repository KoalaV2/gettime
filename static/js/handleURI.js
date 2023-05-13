function fixURLArgumentIcons(urlInput){
	let newURL = urlInput;
	if (newURL.length >= requestURL.length){
		newURL = newURL.replaceAt(requestURL.length,"?");
	}
	return newURL;
}

function readURLArgumentValueFromKey(key,urlInput=null){	
	if (urlInput===null){urlInput = window.location.href;}

	let a = urlInput.split(key + "=")[1] //Contains what is AFTER "key="
	if (a == undefined){
		return null;
	}
	if (a.includes("&")){
		a = a.split("&")[0]; //Now contains what "value" is for "key"
	}
	return a;
}

function removeURLArgument(key,urlInput=null){
	if (urlInput===null){urlInput = window.location.href;}

	let currentURL = urlInput;
	let keyIcon = currentURL[currentURL.indexOf(key)-1]; //Contains what is before the key (& or ?)
	let a = readURLArgumentValueFromKey(key);

	if (currentURL.includes(keyIcon+key+"="+a)){
		currentURL = currentURL.replace(keyIcon+key+"="+a,"");
	}
	else if (currentURL.includes(keyIcon+key)){
		currentURL = currentURL.replace(keyIcon+key,"");
	}
	
	currentURL = fixURLArgumentIcons(currentURL);

	return currentURL;
}

//takes list with 2 strings, and changes the url to match
function addURLArgument(key,value="",urlInput=null){
	// If no url was passed in then it uses the current url instead
	if (urlInput===null){urlInput = window.location.href;}

	let currentURL = urlInput;
	let newURL = currentURL;
	let argument = key + ((value != "") ? ("=" + value) : ("")); //Contains "key=value" (or just "key" if no value was passed)

	// If includes the key, with the same value.
	if (currentURL.includes(argument)){
		return newURL;
		newURL = newURL.replace(newURL[newURL.indexOf(argument)-1] + argument,'');
		newURL = fixURLArgumentIcons(newURL);
	}
	// If includes the key, but not the same value.
	else if (currentURL.includes(key) && value != ""){
		let a = currentURL.split(key + "=")[1]
		if (a.includes("&")){
			a = a.split("&")[0];
		}
		
		newURL = newURL.replace(key + "=" + a, key + "=" + value);
	}
	// If does not include key or value.
	else{
		let argIcon = currentURL.includes(requestURL + "?") ? "&" : "?";
		newURL += argIcon + argument;
	}

	if (decodeURIComponent(readURLArgumentValueFromKey("id",urlInput=newURL)) == 'its dangerous to go alone'){
		newURL = removeURLArgument('id',urlInput=newURL);
	}

	return newURL;
}

var getParams = function (url) {
	var params = {};
	var parser = document.createElement('a');
	parser.href = url;
	var query = parser.search.substring(1);
	var vars = query.split('&');
	for (var i = 0; i < vars.length; i++) {
		var pair = vars[i].split('=');
		params[pair[0]] = decodeURIComponent(pair[1]);
	}
	return params;
};

function UpdateEntryInUrlArguments(key,value,update=false){
	urlArguments[key] = value;
	if (update){
		var a = getParams(window.location.href);
		for (var _key in a){
			if (_key != ""){
				urlArguments[_key] = a[_key];
			}
		}
		window.history.pushState("", "", "?"+$.param(urlArguments));
	}
}

function getLinkForThisSchedule(update=false){
	let a = requestURL;
	
	a = addURLArgument("id",$("#id-input-box").val(),a);
	
	a = addURLArgument("school",school,a);
	
	if ($('#input-day').prop('checked')){
		a = addURLArgument("day",day,a);
	};
	
	a = addURLArgument("week",week,a);
	
	if (update){
		window.history.pushState(null, null, a);
	}
	
	return a;
}
