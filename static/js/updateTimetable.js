function updateTimetable(_callback){
	if (readCookie("infoClosed") != "closed") {
		return
	}
	console.log("updateTimetable was excecuted.");

	idnumber = $("#id-input-box").val();
	checkIfIDTextFits();
	width = $(window).width() + 6;
	height = (window.innerHeight - $(".navbar").height() + 1); // Sets height of schedule to the full screen size, minus the navigation bar at the top

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

	var SUSSY = idnumber.toLowerCase() == "sus" || idnumber.toLowerCase() == "ඞ";
	if (SUSSY){
		window.location.href = requestURL + "ඞ";
	}

	if (idnumber.length > 0){
		
		var url = [
			requestURL + 
			'API/GENERATE_HTML?id=' + idnumber + 
			"&day=" + dayTEMP + 
			"&week=" + week + 
			"&width=" + width + 
			"&height=" + height + 
			"&privateID=" + (privateURL ? "1" : "0") + 
			"&darkmode=" + (darkmode ? "1" : "0") + 
			"&darkmodesetting=1" + 
			"&isMobile=" + (mobileRequest ? "1" : "0")
		][0]

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

			if (!data['result']['html'].startsWith("<!-- ERROR -->")){

				// Replaces the SVG with the new SVG data
				var tdElement = document.getElementById('schedule');
				var trElement = tdElement.parentNode;
				trElement.removeChild(tdElement);
				trElement.innerHTML = data['result']['html'] + trElement.innerHTML;

				$('#schedule').fadeOut(0);
				
				// Run the URL scripts
				try{eval($('#scheduleScript').attr('script'));
				}catch(error){console.error(error);}
				
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
			}

		})

		$('.arrow').removeClass('arrow-loading');

		//This needs to be timed so that it happens AFTER the schedule fades in
		//$("#background-roller").fadeOut("fast");
		$(".arrow-center-text").text(week);

	}

	try{_callback();}catch{}
};
