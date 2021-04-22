function updateTimetable(_callback){
	console.log("updateTimetable was excecuted.");

	//If cookie information hasnt been closed then ignore this request.
	if (readCookie("infoClosed") != "closed") {
		console.log("infoClosed was not closed yet! (Cookies not accepted)")
		return;
	}

	//If school is not set, and no school was specified, then bring up the school selector.
	if (isNaN(school) || school == null || school == "" || school == "null"){
		console.log("School not set!")
		textBoxOpen('#text_school_selector');
		return;
	}

	//Prevent XSS
	let bannedCharacters = "<>/!@#$%^&*()=";
	let idnumber = "";
	let idnumberBeforeScan = $("#id-input-box").val();

	for (i in range(idnumberBeforeScan.length)){
		let currentChar = idnumberBeforeScan.charAt(i);
		if (!bannedCharacters.includes(currentChar)){
			idnumber += currentChar;
		}
	}

	//Updates the input boxes with the XSS cleaned input
	$("#id-input-box").val(idnumber);
	//$("#id-input-box2").val(idnumber);

	checkIfIDTextFits();

	width = $(window).width() + 6;
	height = window.innerHeight + 2; // Sets height of schedule to the full screen size...

	height -= $(".navbar").height(); //...minus the navigation bar at the top

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

	let dayTEMP;
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
		return;
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
		][0];

		//Checks if URL has changed
		if (url == oldURL){
			console.log("URL and oldURL matched. Canceling...");
			$('#schedule').fadeIn(500);
			$("#schedule").css({"transform": "none", "opacity": 1});
			return;
		}
		else{
			oldURL = url;
		}

		if (privateURL){
			console.log("Requesting schedule with private ID...")
		}
		else{
			console.log("Requesting schedule with this url : " + url)
		}

		/* This code asks the server to generate a new schedule for you */
		$.getJSON(url, function(data) {

			// Replaces the SVG with the new SVG data
			let tdElement = document.getElementById('schedule');
			let trElement = tdElement.parentNode;
			trElement.removeChild(tdElement);

			if (data['result']['html'] == undefined || data['result']['html'].startsWith("<!-- ERROR -->")){
				if (data['result']['html'] == undefined ){
					var errorMessage = "No response from sever (GetTime eller Skola24 ligger nere)";
				}
				else{
					var errorMessage = data['result']['data']['message'];
					console.log("<!-- ERROR --> Found in response!");
				}
				
				console.log(errorMessage);

				//Stop the loading icon
				$("#background-roller").fadeOut("fast");
				
            	trElement.innerHTML = '<p id="schedule" class="errorMessage">' + errorMessage + "</p>" + trElement.innerHTML;
				$("#scheduleBox").addClass('errorBox');
				$('#schedule').fadeOut(0);
				$('#schedule').fadeIn(500);
			}
			else{
				if (saveIdToCookie){
					//If we got here, that means that the schedule have loaded successfully, and we want to save the ID in the cookie
					createCookie("idnumber", idnumber, 360);
					console.log("Saved ID to cookie");
				}
				else{
					console.log("Did not save ID to cookie, because saveIdToCookie is false")
				}

				trElement.innerHTML = data['result']['html'] + trElement.innerHTML;
				$("#scheduleBox").removeClass('errorBox');

				// Makes sure the schedule is faded out before it fades in (Otherwise it blinks before it fades in)
				$('#schedule').fadeOut(0);
				
				// Fade in the Schedule
				$('#schedule').fadeIn(500);
				$("#schedule").css({"transform": "none", "opacity": 1});
			}
			
			
			
			// toUrl['id'] = idnumber;
			// toUrl['week'] = week;
			// toUrl['day'] = dayTEMP;
			// if (!privateURL){
			// 	UpdateEntryInUrlArguments('id',idnumber);
			// }
			// window.history.pushState("", "", $.param(toUrl));

		})
		// Stops arrows from blinking
		$('.arrow').removeClass('arrow-loading');

		// Updates the button with the right week number
		$(".arrow-center-text").text(week);

	}

	try{_callback();}catch{}
};
