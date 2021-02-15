//update timetable image

function updateTimetable(){

	idnumber = $(".input-idnumber").val();
	width = $( window ).width() + 6;
	height = (window.innerHeight - $(".navbar").height() + 1);

	if ($("#roundedMode").is(':checked')){
		height -= 25;
		createCookie("roundedMode", "rounded", 360);
	}else{
		createCookie("roundedMode", "straight", 360);
	}

	week = $(".input-week").val();
	if (week == ""){
		console.log("Date hasnt been set yet. Setting now.")
		week = (new Date()).getWeek() - 1;
		$(".input-week").val(week);
		$(".arrow-center-text").text(week);
		$(".arrow-center").attr("title", ("Current week (" + week + ")"));
	}

	dayOnly = $("#input-day").is(':checked');

	if (idnumber.length > 0){
		$("#background-roller").fadeIn("fast");
	}

	savePosition = $(".savebutton").offset();

	if(width > 820){
	$(".savedIDs").css("right", 0);
	$(".savedIDs").css("top", 50);
	$(".savedIDs").css("transform", "none");
	}else{
		$(".savedIDs").css("left", "auto");
		$(".savedIDs").css("top", "auto");
		$(".savedIDs").css("transform", "none");
	}

	currentDay = dateDay + dateModifier;

    if(dayOnly) {

    	$("#input-day-label").text("Show week");

		if (currentDay >= 1 && currentDay <= 5){
			day = currentDay;
		}
		else{
			day = 0;
		}
	    // switch(currentDay){
	    // 	case 1:
	    // 		day = 1;
	    // 		break;
	    // 	case 2:
	    // 		day = 2;
	    // 		break;
	    // 	case 3:
	    // 		day = 3;
	    // 		break;
	    // 	case 4:
	    // 		day = 4;
	    // 		break;
	    // 	case 5:
	    // 		day = 5;
	    // 		break;
	    // 	default:
	    // 		day = 0;
    	// }

	} else {

    	$("#input-day-label").text("Show day");
	    day = 0;
	}

	createCookie("idnumber", idnumber, 360);
	
	if (idnumber.length > 0){
		
		var url = 'https://www.gettime.ga/script/_getTime?id=' + idnumber + "&day=" + day + "&week=" + week + "&width=" + width + "&height=" + height

		if (document.getElementById('schedule').classList.contains('menuBgBlur')){
			url += '&classes=menuBgBlur'
			console.log("yess")
		}
		

		//var url = 'https://www.gettime.ga/script/_getTime/' + idnumber + "/" + day + "/" + week + "/" + width + "/" + height


		/* This code asks the server to generate a new schedule for you */
		console.log("Requesting schedule with url : " + url)
		jQuery.getJSON(url, function(data) {

			/* Saves the included timestamp (age) of the returned schedule */
			/* This is because if you resize the window alot in a short period of time, it will send many requests to the server,
			   and they will return at odd timings, so this TRIES to make sure that if you get a old schedule after a while,
			   it wont update to that one. */
			var newtimestamp = parseFloat(data['result']['timestamp']);
			
			if ( newtimestamp > scheduleAge){
				scheduleAge = newtimestamp

				var tdElement = document.getElementById('schedule');
				var trElement = tdElement.parentNode;
				trElement.removeChild(tdElement);
				trElement.innerHTML = data['result']['html'] + trElement.innerHTML;
				
				$('.arrow').removeClass('arrow-loading');
				$('#schedule').fadeIn(500);
				$("#schedule").css({"transform": "none", "opacity": 1});
				$("#background-roller").fadeOut("fast");
				$(".arrow-center-text").text(week);
			}
		
		})

	}
	
};