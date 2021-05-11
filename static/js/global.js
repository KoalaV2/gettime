/*
    global.js 

    Contains all the general functions that all other documents should be able to use.
*/

// Code from https://stackoverflow.com/a/1431113
String.prototype.replaceAt = function(index, replacement) {
	return this.substr(0, index) + replacement + this.substr(index + replacement.length);
}

// Code from https://web.archive.org/web/20070216153346/http://javascript.about.com/library/blweekyear.htm
Date.prototype.getWeek = function(){
	var onejan = new Date(this.getFullYear(), 0, 1);
	return Math.ceil((((this - onejan) / 86400000) + onejan.getDay() + 1) / 7);
}

// Code from https://stackoverflow.com/a/10050831
function range(size, startAt = 0) {
    return [...Array(size).keys()].map(i => i + startAt);
}

// Code from https://tinyurl.com/j7axshp7
async function sleep(milliseconds,_callback){
	const date = Date.now();
	let currentDate = null;
	do{
	  	currentDate = Date.now();
	}while (currentDate - date < milliseconds);
	try{_callback();}catch{}
	return "";
}

// Code from https://tinyurl.com/ttd83xe6
function debounce(func, wait, immediate) {
	var timeout;
	return function() {
		var context = this, args = arguments;
		var later = function() {
			timeout = null;
			if (!immediate) func.apply(context, args);
		};
		var callNow = immediate && !timeout;
		clearTimeout(timeout);
		timeout = setTimeout(later, wait);
		if (callNow) func.apply(context, args);
	};
};

function send_API_request(url){
	var send_API_request_response;

	function reqListener () {
		send_API_request_response = JSON.parse(this.responseText);
	}

	let r = new XMLHttpRequest();
	r.addEventListener("load", reqListener);
	r.open("GET", url, false);
	r.send();

	return send_API_request_response;
}
