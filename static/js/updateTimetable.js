function updateScheduleHTML(newHTML, errorMessage=false, justTheEnd=false){
	if (!justTheEnd){
		let tdElement = document.getElementById('schedule');
		let trElement = tdElement.parentNode;
		trElement.removeChild(tdElement);

		if (errorMessage){
			$("#scheduleBox").addClass('errorBox');
			trElement.innerHTML = '<p id="schedule" class="errorMessage">' + newHTML + "</p>" + trElement.innerHTML;
		}
		else{
			$("#scheduleBox").removeClass('errorBox');
			trElement.innerHTML = newHTML + trElement.innerHTML;
		}
	}

	//Hides the schedule at first, and then fades it in.
	$('#schedule').fadeOut(0);
	$('#schedule').fadeIn(500);

	//Does some shit
	$("#schedule").css({"transform": "none", "opacity": 1});

	//Stops loading animation
	$("#background-roller").fadeOut("fast");

	// Stops arrows from blinking
	$('.arrow').removeClass('arrow-loading');
};

function updateTimetable(_callback, ignoreSameURL=false){
	console.log("updateTimetable was excecuted. " + ignoreSameURL);
	//#region INIT
	//#region fast returns
	//If cookie information hasnt been closed then ignore this request.
	if (readCookie("infoClosed") != "closed") {
		if (ignorecookiepolicy){
			console.log("infoClosed was not closed yet, but ignorecookiepolicy was true.");
		}
		else{
			console.log("infoClosed was not closed yet! (Cookies not accepted)");
			return;
		}
	}

    //If school is not set, and no school was specified, then bring up the school selector.
    console.log("School: " + school);
	if (school == null || school == "" || school == "null"){
		console.log("School not set!")
		textBoxOpen('#text_school_selector');
		return;
	}
	//#endregion
	//#region Prevent XSS
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
	//#endregion

	checkIfIDTextFits();

	width = $(window).width() + 6;
	height = window.innerHeight + 2; // Sets height of schedule to the full screen size...
	if (!hideNavbar){
		height -= $(".navbar").height(); //...minus the navigation bar at the top
	}

	savePosition = $(".savebutton").offset();

	$(".savedIDs").css("left", "auto");
	$(".savedIDs").css("top", "auto");
	if(width > 820){
		$(".savedIDs").css("right", 0);
		$(".savedIDs").css("top", 50);
	}
	$(".savedIDs").css("transform", "none");

	//#region Special cases/Secrets
	if (idnumber.toLowerCase() == "its dangerous to go alone"){
		textBoxOpen('#text_tricks');
		return;
	}

	let easter_eggs = [
		["sus", "ඞ"],
		["ඞ", "ඞ"],

		["avrinning", "?a=ZGbCmXrCgcKjwqJlcsKcwqdqw77Clw=="],
		["biktor", "?a=ZGbCmXrCgsKiwqJpdsKdwqtnw77Clw=="],
		["theo", "?a=ZGbCmXvCgcKlwqFod8Kfwq1pw77Clw=="],
		["isak", "?a=ZGbCmXrCgcKiwqFocsKdwqlkw77Clw=="]
	]

	easter_eggs.forEach(e => {
		if (idnumber.toLowerCase() == e[0]){
			window.location.href = requestURL + e[1]
		}
	})
	//#endregion
	//#endregion
	if (idnumber.length > 0){
		$("#background-roller").fadeIn("fast");
		let url = [
			requestURL +
			'API/GENERATE_HTML?id=' + encodeURI(idnumber) +
			"&day=" + ($("#input-day").is(':checked') ? day : 0) +
			"&week=" + week +
			"&year=" + year +
			"&width=" + width +
			"&height=" + height +
			"&privateID=" + (privateURL ? "1" : "0") +
			"&darkmode=" + (darkmode ? "1" : "0") +
			"&darkmodesetting=" + darkModeSetting +
			"&isMobile=" + (mobileRequest ? "1" : "0") +
			"&school=" + encodeURI(school)
		][0];

		//Checks if URL has changed
		if (!ignoreSameURL){
			if (url == oldURL){
				console.log("URL and oldURL matched. Canceling...");
				$('#schedule').fadeIn(0);
				$("#background-roller").fadeOut(0);
				$('.arrow').removeClass('arrow-loading');
				return;
			}
			else{
				oldURL = url;
			}
		}

		// Updates the button with the right week number
		$(".arrow-center-text").text(week);

		console.log("Requesting schedule with " + ( privateURL ? "private ID..." : "this url : " + url ))
		let data = send_API_request(url); /* This code asks the server to generate a new schedule for you */

		if (data['result']['html'] == undefined || data['result']['html'].startsWith("<!-- ERROR -->")){
			if (data['result']['html'] == undefined){
				var errorMessage = "No response from sever (GetTime eller Skola24 ligger nere)";
			}
			else{
				var errorMessage = data['result']['data']['message'];
				console.log("<!-- ERROR --> Found in response!");
			}

			console.log(errorMessage);
			updateScheduleHTML(errorMessage, errorMessage=true);
		}
		else{

			if (overwrite_saveIdToCookie != null ? overwrite_saveIdToCookie : saveIdToCookie){
				//If we got here, that means that the schedule should have loaded successfully, and we want to save the ID in the cookie
				createCookie("idnumber", idnumber, 360);
				console.log("Saved ID to cookie");
			}
			else{
				console.log("Did not save ID to cookie, because saveIdToCookie is false")
			}

			overwrite_saveIdToCookie = null;

			updateScheduleHTML(data['result']['html']);
		}
	}
	else{
		updateScheduleHTML("Inget ID skrivit", errorMessage=true);
		console.log("updateTimetable did not run (ID was less then 1 lenght)");
	}
	try{_callback();}catch{}
};
