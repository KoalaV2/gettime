var urlArguments = {};
var week;
var year = initYear;
var day = initDay;
var darkmode = initDarkMode;
var hideNavbar = initHideNavbar;
var oldURL = "";
var school = initSchool;
var screenSize = [0,0];
var overwrite_saveIdToCookie = null;

//#region toggleDarkMode
function toggleDarkMode(disableAnimation=false, saveToCookie=true, updateTimeTableAfter=true){
	// Set the dark mode switch first
	darkmode = $('#input-darkmode').prop('checked')

	// Save dark mode option to cookie
	if (saveToCookie){
		createCookie('darkmode',(darkmode ? "1" : "0"),365);
	}

	function doTheThing(){
		let link = document.getElementById("css-theme");
		let dark_mode_is_currently = link.getAttribute("darkmode") == 1;

		link.setAttribute("darkmode", (dark_mode_is_currently ? 0 : 1))
		link.href = (dark_mode_is_currently ? "" : ("/static/css/darkmode/darkmode-" + (mobileRequest ? "mobile" : "desktop") + ".css"));
		Array.from(document.getElementsByClassName("theme-color-setting")).forEach(e => {
			e.setAttribute('content', (dark_mode_is_currently ? "#4343b2" : "#373737"));
		});
		// document.querySelector("link.favicon").href = '/static/img/' + (dark_mode_is_currently ? "favicon.png" : "favicon_dark.png")
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

		// Needs better timing (its to fast rn)
		$(".loader-main").slideToggle(500);
	}
}
//#endregion

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
var lastKnownScreenSize = screenSize;
function checkIfIDTextFits(){
	let el = $('#id-input-box');
	if (el.val() != lastKnownID || inputExceeded() || screenSize != lastKnownScreenSize){
		if (inputExceeded()){
			while(inputExceeded()){
				let oldSize = parseInt(el.css("--font-size"),10);
				let newSize = oldSize - 1;
				
				if(newSize < 1){
					break;
				}
	
				el.css({"font-size":"min(" + newSize + "px,24px)","--font-size":newSize + "px"});
			}
		}
		else{
			while(!inputExceeded()){
				let oldSize = parseInt(el.css("--font-size"),10);
				let newSize = oldSize + 1;
				
				if(newSize > 24){
					break;
				}
	
				el.css({"font-size":"min(" + newSize + "px,24px)","--font-size":newSize + "px"});
			}
		}
		lastKnownID = el.val();
		lastKnownScreenSize = screenSize;
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
			$('#scheduleBLUR').addClass("menuBgBlur");
	        $(".menuIcon").removeClass("fa-bars").addClass("fa-times");
	    }else{
			$('#scheduleBLUR').removeClass("menuBgBlur");
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
			$('#scheduleBLUR').addClass("menuBgBlur");
			$(".menuIcon").removeClass("fa-bars").addClass("fa-times");
		}else{
			$('#scheduleBLUR').removeClass("menuBgBlur");
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

//Gets the "moreData"
function getMoreData(){
	return send_API_request(
		requestURL + 'API/MORE_DATA?school=' + encodeURI(school)
	);
}

function updateMenuButtonsBasedOnSize(){
	let t = $('.menu-option-text');
	$('.menu-option-text').attr(((window.innerWidth < 450) ? "shortText" : "longText"), function(i, x){
		if (x != undefined){
			t[i].innerHTML = x;
		}
	});
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



function update_dropdowns(){
	let new_data = getMoreData();

	console.log(new_data)

	let a = [
		["teachers", "Byt Lärare", "id", "fullName"],
		["classes", "Byt klass", "groupName", "groupName"]
	].forEach(current => {
		let x = new_data['data'][current[0]]
		if (x.length == 0){
			$(`.${current[0]}-select-box`).hide()
		}
		else{
			let dest = document.querySelector(`.${current[0]}-select-box`)
			
			
			dest.innerHTML = `<option value="" selected disabled hidden>${current[1]}</option>`;
	
			x.forEach(i =>{
				let option = document.createElement("option")
	
				option.value = i[current[2]]
				option.innerHTML = i[current[3]]
	
				dest.appendChild(option)
			});
	
			$(`.${current[0]}-select-box`).show()
		};
	});
}




function schoolSelected(schoolName){
	school = schoolName;
	createCookie('school',schoolName,365);
	textBoxClose('#text_school_selector');
	$('.school-select-box').val(school);
	
	$("#background-roller").fadeIn("fast", function(){
		updateTimetable();
	});
	

	update_dropdowns();

	// $("#background-roller").fadeOut("fast");
}

// Start Service worker
if ('serviceWorker' in navigator) {
	window.addEventListener('load', function() {
		navigator.serviceWorker.register('service-worker.js').then(function(registration) {
			// Registration was successful
			console.log('Registered!');
		}, function(err) {
			// registration failed :(
			console.log('ServiceWorker registration failed: ', err);
		}).catch(function(err) {
			console.log(err);
		});
	});
} else {
	console.log('service worker is not supported');
}

window.addEventListener('beforeinstallprompt', e => {
	console.log('beforeinstallprompt Event fired');
	e.preventDefault();

	// Stash the event so it can be triggered later.
	window.deferredPrompt = e;

	if (document.querySelector(".controls-container button.install-app-button") == null){
		let button = document.createElement("button")
		let button_text = document.createElement("span")
		let button_icon = document.createElement("i")

		button.onclick = install;
		button.classList.add("control", "control-container", "install-app-button")

		button_text.text = "GetTime App"
		button_text.innerHTML = "GetTime App"
		button_text.classList.add("menu-option-text")
		button.appendChild(button_text)

		button_icon.classList.add("fab", "fa-app-store-ios", "control-right")
		
		button.appendChild(button_icon)
		document.getElementsByClassName("controls-container")[0].appendChild(button)
	}
	
	return false;
});

function install(){
	// When you want to trigger prompt:
	window.deferredPrompt.prompt();
	window.deferredPrompt.userChoice.then(choice => {
		console.log(choice);

		// If user installed the app, then this will launch the PWA link after install
		if (choice.outcome == "accepted"){
			$.getJSON(window.location.pathname + "static/manifest.webmanifest", function(data) {
				window.location.href = data.start_url;
			});
		}
	});
	window.deferredPrompt = null;	
}

function update_timetable_to_fit_new_window_size_function(do_updateTimetable=true){
	console.log("update timetable to fit new window size");
	screenSize = [$(window).width(),$(window).height()];

	
	updateMenuButtonsBasedOnSize();
	if (do_updateTimetable){
		$("#schedule").fadeOut(500);
		updateTimetable();
	}
	
	checkIfIDTextFits();

	$(".dropdown-container").show()
	if (document.querySelector(".navbar").scrollWidth > window.width){
		$(".dropdown-container").hide()
	}
}

//events on load & event triggers.
$(window).on("load", function(){
	//#region Dark mode
	if (initDarkMode == null){
		if (readCookie('darkmode') == null){
			darkmode = false;
		}
		else{
			darkmode = (readCookie('darkmode') == "1" ? true : false);
		}
	}
	
	$('#input-darkmode').prop('checked', darkmode);
	if (darkmode){ // Dark mode is true by "default", so this will turn it off if dark mode SHOULD be off (confusing as hell but ok)
		toggleDarkMode(disableAnimation=true, saveToCookie=false, updateTimeTableAfter=false);
	}
	//#endregion	
	//#region School
	if (initSchool != ""){ //If school was specified in the URL:
		school = initSchool;
		$('.school-select-box').val(school);
	}
	else{
		let schoolNow = readCookie("school");

		if (isNaN(schoolNow) || schoolNow == null){ //if cookie did not contain a number, or nothing at all:
			if (!(!ignorecookiepolicy && readCookie("infoClosed") != "closed")){
				textBoxOpen('#text_school_selector');
			}
		}
		else{
			school = schoolNow;
			$('.school-select-box').val(school);
		}
	}
	//#endregion 

	if (school != ""){
		update_dropdowns();
	}
	
	//Hides the main input if the URL is private
	if (privateURL){
		$('#id-input-box').css("display", "none");
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

	// update_dropdowns();
    update_timetable_to_fit_new_window_size_function(false)


	// Page finished loading, slide up loader screen
	$(".loader-main").slideToggle();

	console.log("script.js is done");
});

$(document).ready(function() {
	//Updates the width of the input box so that it will fit with the school select box.
	// if (!mobileRequest){
	// 	$('.input-idnumber').width(`calc(calc(100vw - 215px) - ${$('.school-select-box').width()}px)`);
	// }
	if (mobileRequest){
		$('.input-idnumber').width(`calc(calc(100vw - 17px) - ${$('.arrows-container').width()}px)`);
	}
	

	// Moves the timetable down so it doesnt overlay the navbar
	if (!hideNavbar){
		$("#scheduleBox").css("top", "50px");
	}

	screenSize = [$(window).width(),$(window).height()];
});

// // Code from https://stackoverflow.com/a/15032300
// if (autoReloadSchedule){
// 	var lastRefresh = new Date(); // If the user just loaded the page you don't want to refresh either
// 	setInterval(function(){
// 		//first, check time, if it is 0 AM, reload the page
// 		var now = new Date();
// 		if (now.getHours() == 0 && new Date() - lastRefresh > 1000 * 60 * 60 * 1.5) { // If it is between 9 and ten AND the last refresh was longer ago than 1.5 hours refresh the page.
// 			location.reload();
// 		}
// 	},10000);
// }

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
