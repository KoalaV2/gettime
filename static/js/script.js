var urlArguments = {};
var week;
var day = initDay;
var darkmode = initDarkMode;
var hideNavbar = initHideNavbar;
var oldURL = "";
var school = initSchool;
  
// Idea from https://tinyurl.com/yhsukrs9

function toggleDarkMode(disableAnimation=false,saveToCookie=true,updateTimeTableAfter=true){
	//This code is messy
	let toggleDarkMode_on = '';
	let toggleDarkModeAll_on = '';
	if (ignorecssmin){
		toggleDarkModeAll_on = '/static/css/darkmode-all.css';

		if (mobileRequest){
			toggleDarkMode_on = '/static/css/darkmode-mobile.css';}
		else{
			toggleDarkMode_on = '/static/css/darkmode-desktop.css';
		}
	}
	else{
		toggleDarkModeAll_on = '/static/css/min/darkmode-all.min.css';

		if (mobileRequest){
			toggleDarkMode_on = '/static/css/min/darkmode-mobile.min.css';
		}
		else{
			toggleDarkMode_on = '/static/css/min/darkmode-desktop.min.css';
		}	
	}

	//Set the dark mode switch first
	darkmode = $('#input-darkmode').prop('checked')

	//Save dark mode option to cookie
	if (saveToCookie){
		createCookie('darkmode',(darkmode ? "1" : "0"),365);
	}

	function doTheThing(){
		var theme = document.getElementById('darkmode');
		var theme2 = document.getElementById('darkmodeAll');

		if (theme.getAttribute('href') == 'off'){
			theme.setAttribute('href', toggleDarkMode_on);
			theme2.setAttribute('href', toggleDarkModeAll_on);
		}
		else{
			theme.setAttribute('href', 'off');
			theme2.setAttribute('href', 'off');
		}
	}
	
	if (disableAnimation){
		doTheThing();
		if (updateTimeTableAfter){
			updateTimetable();
		}
	}
	else{
		$(".loader-main").slideToggle(500,function(){
			doTheThing();
			if (updateTimeTableAfter){
				updateTimetable();
			}
		});

		//Needs better timing (its to fast rn)
		$(".loader-main").slideToggle(500);
	}
}

function inputExceeded(){
	// Modified code from https://stackoverflow.com/a/4836059
	var el = $('#id-input-box');
	var s = $('<span >'+el.val()+'</span>');
	s.css({
	   position: 'absolute',
	   left: -9999,
	   top: -9999,
	   // ensure that the span has same font properties as the element
	   'font-family': el.css('font-family'),
	   'font-size': el.css('font-size'),
	   'font-weight': el.css('font-weight'),
	   'font-style': el.css('font-style')
	});
	$('body').append(s);
	var result = s.width() > el.width();
	//remove the newly created span
	s.remove();
	return result;
}

var lastKnownID = "ඞ";
function checkIfIDTextFits(){
	var el = $('#id-input-box');
	if (el.val() != lastKnownID || inputExceeded()){
		if (inputExceeded()){
			while(inputExceeded()){
				var oldSize = parseInt(el.css("--font-size"),10);
				var newSize = oldSize - 1;
				
				if(newSize < 1){
					break;
				}
	
				el.css({"font-size":"min(" + newSize + "px,24px)","--font-size":newSize + "px"});
			}
		}
		else{
			while(!inputExceeded()){
				var oldSize = parseInt(el.css("--font-size"),10);
				var newSize = oldSize + 1;
				
				if(newSize > 24){
					break;
				}
	
				el.css({"font-size":"min(" + newSize + "px,24px)","--font-size":newSize + "px"});
			}
		}
		lastKnownID = el.val();
	}
	
}

// show and update saved url's
function showSaved(){

	$('#scheduleBox').addClass("menuBgBlur");
	$(".menuIcon").removeClass("fa-bars").addClass("fa-times");

	$(".savedList").empty();
	$(".savedList").append("<li class='savedItems'>Tryck på länkarna för att ta bort dom</li>");
	savedItems = getAllCookieNamesThatStartWith("URL_");

	for (var i = savedItems.length - 1; i >= 0; i--) {
		if (savedItems[i].length > 0){
			$(".savedList").append('<li class="savedItems" onclick="eraseCookie(' + "'" + savedItems[i] + "'" + ');showSaved();">' + savedItems[i].replace('URL_','') + "</li>");				
		};	
	};

	console.log($(".savedList"));

	if ($(".savedItems").length == 1){
		$(".savedList").empty();
		$(".savedList").append("<li class='savedItems'>Du har inte sparat något URL</li>");
	}
	else{
		$(".savedList").append('<button class="clearSavedItems mobileSaved control-container" onclick="deleteAllURLCookies();">Ta bort alla</button>');
	}
	
	$(".savedIDs").fadeIn("fast");

};

//open textBox
function textBoxOpen(idToOpen){
	hideControls();
	$(idToOpen).fadeIn();
	$('.navbar').fadeOut();
	$('#scheduleBox').fadeOut();
}

//close textBox
function textBoxClose(idToClose){
	$(idToClose).fadeOut();
	$('.navbar').fadeIn();
	$('#scheduleBox').fadeIn();	
};

//save inputed item in box
function savedItemClicked(item){
	$("#id-input-box").val(item.text());
	$(".savedIDs").fadeOut("fast");
	console.log('save inputed item in box');
	updateTimetable();
};

//hide controls menu on mobile
function hideControls(){
	$('.controls').slideUp('fast', function() {
	    if ($(this).is(':visible')){
	        $(this).css('display','flex');
			$('#scheduleBox').addClass("menuBgBlur");
	        $(".menuIcon").removeClass("fa-bars").addClass("fa-times");
	    }else{
			$('#scheduleBox').removeClass("menuBgBlur");
	        $(".menuIcon").removeClass("fa-times").addClass("fa-bars");
	    };
	});
};
function showControls(){
	updateMenuButtonsBasedOnSize();
	$('.controls').slideToggle('fast', function(){
		$('.controls-container').fadeIn(0);
		if ($(this).is(':visible')){
			$(this).css('display','flex');
			$('#scheduleBox').addClass("menuBgBlur");
			$(".menuIcon").removeClass("fa-bars").addClass("fa-times");
		}else{
			$('#scheduleBox').removeClass("menuBgBlur");
			$(".menuIcon").removeClass("fa-times").addClass("fa-bars");
		};
	});
}

//Copies text to users clipboard
function updateClipboard(newClip) {
	navigator.clipboard.writeText(newClip).then(function() {
			/* clipboard successfully set */
			console.log("YES");
		}, function() {
			/* clipboard write failed */
			console.log("NO");
	});
}

//Gets the shareable link
function getShareableURL(){
	return send_API_request(
		requestURL + 'API/SHAREABLE_URL?id=' + $("#id-input-box").val() + "&school=" + encodeURI(school)
	)['result'];
}

function updateMenuButtonsBasedOnSize(){
	if (window.innerWidth < 450){
		$("#button-text-day").html("Visa dag");
		$("#button-text-qr").html("QR kod");
		$("#button-text-private").html("Privat länk");
		$("#button-text-copy").html("Kopiera länk");
		$("#button-text-saved").html("Länkar");
	}else{
		$("#button-text-day").html("Visa bara dag&nbsp;&nbsp;");
		$("#button-text-qr").html("Skapa QR kod&nbsp;&nbsp;");
		$("#button-text-private").html("Skapa privat länk&nbsp;&nbsp;");
		$("#button-text-copy").html("Kopiera privat länk&nbsp;&nbsp;");
		$("#button-text-saved").html("Sparade länkar&nbsp;&nbsp;");
	}
}

function clickOn_QRCODE(){
	$("#button-text-qr").text("Laddar...");
	try {
		window.location.href = requestURL + "API/QR_CODE?id=" + (privateURL ? (getShareableURL()['id'] + "&p=1") : ($("#id-input-box").val() + "&p=0"));
	} catch {
		$("#button-text-qr").text("ERROR!");
	}
}

function clickOn_SAVEDLINKS(){
	showSaved();
	$('.controls-container').fadeOut(0);
}

function f_showNavbar(){
	console.log("Showing navbar");
	hideNavbar = false;
	$('.navbar').show();
	$('#scheduleBox').css({'top':$('.navbar').height()+'px'});
	updateTimetable();
}
function f_hideNavbar(){
	console.log("Hiding navbar");
	hideNavbar = true;
	$('.navbar').hide();
	$('#scheduleBox').css({'top':'0px'});
	updateTimetable();
}

function schoolSelected(schoolName){
	school = schoolName;

	// let tdElement = document.getElementById('schedule');
	// let trElement = tdElement.parentNode;
	// trElement.removeChild(tdElement);
	// trElement.innerHTML = '<svg id="schedule"></svg>' + trElement.innerHTML;

	// $("#id-input-box").val("");
	// $("#id-input-box2").val("");

	createCookie('school',schoolName,365);
	textBoxClose('#text_school_selector');
	updateTimetable();

	$("#background-roller").fadeOut("fast");
}

//events on load & event triggers.
$(window).on("load", function(){

	// Code from https://stackoverflow.com/a/15032300
	if (autoReloadSchedule){
		var lastRefresh = new Date(); // If the user just loaded the page you don't want to refresh either
		setInterval(function(){
			//first, check time, if it is 0 AM, reload the page
			var now = new Date();
			if (now.getHours() == 0 && new Date() - lastRefresh > 1000 * 60 * 60 * 1.5) { // If it is between 9 and ten AND the last refresh was longer ago than 1.5 hours refresh the page.
				location.reload();
			}
		},10000);
	}

	//Dark mode
	if (initDarkMode == null){
		if (readCookie('darkmode') == null){
			darkmode = false;
		}
		else{
			darkmode = (readCookie('darkmode') == "1" ? true : false);
		}
	}
	if (!darkmode){ //Dark mode is true by "default", so this will turn it off if dark mode SHOULD be off (confusing as hell but ok)
		toggleDarkMode(disableAnimation=true,saveToCookie=false,updateTimeTableAfter=false);
	}
	$('#input-darkmode').prop('checked', darkmode);

	//Hides the main input if the URL is private
	if (privateURL){
		$('#id-input-box').css("display", "none");
	}
	
	//set school
	if (initSchool == "null"){
		if (!(!ignorecookiepolicy && readCookie("infoClosed") != "closed")){
			textBoxOpen('#text_school_selector');
		}
	}
	else{
		//If school was specified in the URL
		if (initSchool != ""){
			school = initSchool;
		}
		else{
			let schoolNow = readCookie("school");

			if (isNaN(schoolNow) || schoolNow == null){
				if (!(!ignorecookiepolicy && readCookie("infoClosed") != "closed")){
					textBoxOpen('#text_school_selector');
				}
			}
			else{
				school = schoolNow;
			}
		}
	}

	//hide all textboxes
	$('.text_box').hide();

	//hide controls div before load
	hideControls();

	//hide saved ids div before load
	$(".savedIDs").fadeOut(0);

	//enable day mode by default for mobile devices
	$('#input-day').prop('checked', initDayMode);

	//get idnumber from cookie or input data
	$("#id-input-box").val(
		(initID == "" ? readCookie("idnumber") : initID)
	);
	checkIfIDTextFits();

	//get info closed cookie and hide or show info accordingly
	if (!ignorecookiepolicy && readCookie("infoClosed") != "closed"){
		textBoxOpen('#text_cookies_info')
	}

	//get and set current week
	week = initWeek;
	$(".input-week").val(week);
	$(".arrow-center-text").text(week);
	$(".arrow-center").attr("title", ("Current week (" + week + ")"));

	if (showContactOnLoad){
		textBoxOpen('#text_contact_info');
	}

	//load timetable after cookie info get
	if (readCookie("infoClosed") == "closed" || ignorecookiepolicy){
		console.log("load timetable after cookie info get");
		updateTimetable();	
	}
	
	if (hideNavbar){
		f_hideNavbar();
	}

	// Page finished loading, slide up loader screen
	$(".loader-main").slideToggle();

	console.log("script.js is done");
});

// Moves the timetable down so it doesnt overlay the navbar
$(document).ready(function() {
    $("#scheduleBox").css("top", $(".navbar").height());
});

// function is_heightIsMoreThenWidth(){
// 	return $(window).height() > $(window).width();
// }
// var heightIsMoreThenWidth = null;
// function hasMobileBeenRotated(){
// 	if (mobileRequest){
// 		if (heightIsMoreThenWidth == null){
// 			heightIsMoreThenWidth = is_heightIsMoreThenWidth();
// 		}
// 		else{
// 			if (heightIsMoreThenWidth == is_heightIsMoreThenWidth()){
// 				console.log("User did not rotate their screen yet");
// 				return;
// 			}
// 			else{
// 				heightIsMoreThenWidth = is_heightIsMoreThenWidth();
// 			}
// 		}
// 		if (initHideNavbar != true){
// 			hideNavbar = !heightIsMoreThenWidth;

// 			if (hideNavbar){
// 				f_hideNavbar();
// 			}
// 			else{
// 				f_showNavbar();
// 			}
// 		}
// 	}
// }

// if (initID == ""){
// 	$("#id-input-box").val(readCookie("idnumber"));
// }
// else{
// 	$("#id-input-box").val(initID);
// }
