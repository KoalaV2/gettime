function updateTimetable(_callback){
	console.log("updateTimetable was excecuted.");

	if (readCookie("infoClosed") != "closed") {
		return;
	}

	if (school == null || school == "" || school == "null"){
		if (readCookie("infoClosed") == "closed"){
			textBoxOpen('#text_school_selector');
		}	
		return;
	}

	//Code from https://portswigger.net/web-security/cross-site-scripting/preventing#how-to-prevent-xss-client-side-in-javascript:~:text=function%20htmlEncode(str)%7B,%7D
	function htmlEncode(str){
		return String(str).replace(/[^\w. ]/gi, function(c){
		   return '&#'+c.charCodeAt(0)+';';
		});
	}

	//Code from https://portswigger.net/web-security/cross-site-scripting/preventing#how-to-prevent-xss-client-side-in-javascript:~:text=function%20jsEscape(str)%7B,%7D
	function jsEscape(str){
		return String(str).replace(/[^\w. ]/gi, function(c){
		   return '\\u'+('0000'+c.charCodeAt(0).toString(16)).slice(-4);
		});
	}

	var bannedCharacters = "<>/!@#$%^&*()=";
	var idnumber = "";
	var idnumberBeforeScan = $("#id-input-box").val();

	console.log("Before : " + idnumberBeforeScan);
	for (i in range(idnumberBeforeScan.length)){
		let currentChar = idnumberBeforeScan.charAt(i);
		console.log(i + " : " + currentChar);
		if (!bannedCharacters.includes(currentChar)){
			idnumber += currentChar;
		}
	}
	console.log("After : " + idnumber);
	$("#id-input-box").val(idnumber);
	//var idnumber = jsEscape($("#id-input-box").val());

		
	checkIfIDTextFits();

	width = $(window).width() + 6;
	height = window.innerHeight + 1; // Sets height of schedule to the full screen size...

	height -= $(".navbar").height() //...minus the navigation bar at the top

	dayOnly = $("#input-day").is(':checked');

	if (idnumber.length > 0){
		$("#background-roller").fadeIn("fast");
	}

	savePosition = $(".savebutton").offset();

	if(width > 820){
		$(".savedIDs").css("right", 0);
		$(".savedIDs").css("top", 50);
		$(".savedIDs").css("transform", "none");
	}
	else{
		$(".savedIDs").css("left", "auto");
		$(".savedIDs").css("top", "auto");
		$(".savedIDs").css("transform", "none");
	}

	var dayTEMP;
    if(dayOnly){
    	$("#input-day-label").text("Show week");
		dayTEMP = day;
	}
	else{
    	$("#input-day-label").text("Show day");
	    dayTEMP = 0;
	}

	if (idnumber.toLowerCase() == "its dangerous to go alone"){
		textBoxOpen('#text_tricks');
	}

	let SUSSY = idnumber.toLowerCase() == "sus" || idnumber.toLowerCase() == "ඞ";
	if (SUSSY){
		window.location.href = requestURL + "ඞ";
	}

	if (idnumber.length > 0){
		
		let url = [
			requestURL + 
			'API/GENERATE_HTML?id=' + encodeURI(idnumber) + 
			"&day=" + dayTEMP + 
			"&week=" + week + 
			"&width=" + width + 
			"&height=" + height + 
			"&privateID=" + (privateURL ? "1" : "0") + 
			"&darkmode=" + (darkmode ? "1" : "0") + 
			"&darkmodesetting=" + darkModeSetting + 
			"&isMobile=" + (mobileRequest ? "1" : "0") +
			"&school=" + encodeURI(school)
		][0]
		console.log(url);

		if (url == oldURL){
			console.log("URL and oldURL matched. Canceling...");
			$('#schedule').fadeIn(500);
			$("#schedule").css({"transform": "none", "opacity": 1});
			return;
		}
		else{
			oldURL = url;
		}

		// If the schedule is supposed to be blurred, the new request will return with the blur class allready applied
		try{
			if (document.getElementById('schedule').classList.contains('menuBgBlur')){
				url += '&classes=menuBgBlur';
			}
		}catch(error){
			console.error(error);
		}

		if (!privateURL){
			console.log("Requesting schedule with this url : " + url)
		}
		else{
			console.log("Requesting schedule...")
		}

		/* This code asks the server to generate a new schedule for you */
		$.getJSON(url, function(data) {

			if (!data['result']['html'].startsWith("<!-- ERROR -->") && saveIdToCookie && !SUSSY){
				createCookie("idnumber", idnumber, 360);
				console.log("Saved ID to cookie");
			}

			if (data['result']['html'].startsWith("<!-- ERROR -->")){
				console.log("<!-- ERROR --> Found in response!");
				let errorMessage = data['result']['data']['data']['validation'][0]['message'];
				console.log(errorMessage);
				$("#background-roller").fadeOut("fast");

            //	trElement.innerHTML = errorMessage + trElement.innerHTML;
			}
			else{
	        // Replaces the SVG with the new SVG data
			let tdElement = document.getElementById('schedule');
			let trElement = tdElement.parentNode;
			trElement.removeChild(tdElement);
			trElement.innerHTML = data['result']['html'] + trElement.innerHTML;
			}
			

			$('#schedule').fadeOut(0);
			
			// Run the URL scripts
			// try{eval($('#scheduleScript').attr('script'));
			// }catch(error){console.error(error);}
			
			// Fade in the Schedule
			$('#schedule').fadeIn(500);
			$("#schedule").css({"transform": "none", "opacity": 1});
			
			// toUrl['id'] = idnumber;
			// toUrl['week'] = week;
			// toUrl['day'] = dayTEMP;
			// if (!privateURL){
			// 	UpdateEntryInUrlArguments('id',idnumber);
			// }
			// window.history.pushState("", "", $.param(toUrl));

		})

		$('.arrow').removeClass('arrow-loading');

		//This needs to be timed so that it happens AFTER the schedule fades in
		//$("#background-roller").fadeOut("fast");
		$(".arrow-center-text").text(week);

	}

	try{_callback();}catch{}
};
