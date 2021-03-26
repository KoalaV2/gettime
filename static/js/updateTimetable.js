//update timetable image

function updateTimetable(){

	idnumber = $(".input-idnumber").val();
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
		
		var url = requestURL + 'API/GENERATE_HTML?id=' + idnumber + "&day=" + dayTEMP + "&week=" + week + "&width=" + width + "&height=" + height + "&privateID=" + (privateURL ? "1" : "0")

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

		/* This code asks the server to generate a new schedule for you */
		$.getJSON(url, function(data) {

			if (data['result']['html'] != "None" && saveIdToCookie && !SUSSY){
				createCookie("idnumber", idnumber, 360);
				console.log("Saved ID to cookie");
			}
			if (data['result']['html'] != "None"){
				// Replaces the SVG with the new SVG data
				var tdElement = document.getElementById('schedule');
				var trElement = tdElement.parentNode;
				trElement.removeChild(tdElement);
				trElement.innerHTML = data['result']['html'] + trElement.innerHTML;
				
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
		$("#background-roller").fadeOut("fast");
		$(".arrow-center-text").text(week);

	}
	
};
