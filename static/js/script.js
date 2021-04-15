var urlArguments = {};
var week;
var day = initDay;
var darkmode = initDarkMode;

// Code from https://tinyurl.com/j7axshp7
function sleep(milliseconds,_callback){
	const date = Date.now();
	let currentDate = null;
	do{
	  	currentDate = Date.now();
	}while (currentDate - date < milliseconds);
	try{_callback();}catch{}
}
  
// Idea from https://tinyurl.com/yhsukrs9
var toggleDarkMode_on = '';
var toggleDarkModeAll_on = '';
var toggleDarkMode_off = 'off';
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
function toggleDarkMode(disableAnimation=false,saveToCookie=true){
	
	//Set the dark mode switch first
	darkmode = $('#input-darkmode').prop('checked')

	//Save dark mode option to cookie
	if (saveToCookie){
		createCookie('darkmode',(darkmode ? "1" : "0"),365);
	}

	function doTheThing(){
		var theme = document.getElementById('darkmode');
		var theme2 = document.getElementById('darkmodeAll');

		if (theme.getAttribute('href') == toggleDarkMode_off){
			theme.setAttribute('href', toggleDarkMode_on);
			theme2.setAttribute('href', toggleDarkModeAll_on);
		}
		else{
			theme.setAttribute('href', toggleDarkMode_off);
			theme2.setAttribute('href', toggleDarkMode_off);
		}
	}
	
	if (disableAnimation){
		doTheThing();
		updateTimetable();
	}
	else{
		$(".loader-main").slideToggle(500,function(){
			doTheThing();
			updateTimetable();
		});

		//Needs better timing (its to fast rn)
		$(".loader-main").slideToggle(500);
	}
}

//get week number function
Date.prototype.getWeek = function(){
	var onejan = new Date(this.getFullYear(), 0, 1);
	return Math.ceil((((this - onejan) / 86400000) + onejan.getDay() + 1) / 7);
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

	$('#schedule').addClass("menuBgBlur");
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
			$('#schedule').addClass("menuBgBlur");
	        $(".menuIcon").removeClass("fa-bars").addClass("fa-times");
	    }else{
			$('#schedule').removeClass("menuBgBlur");
	        $(".menuIcon").removeClass("fa-times").addClass("fa-bars");
	    };
	});
};

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
	var value= $.ajax({ 
	   url: requestURL + 'API/SHAREABLE_URL?id=' + $("#id-input-box").val(), 
	   async: false
	}).responseJSON;
	return value['result'];
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

//events on load & event triggers.
$(window).on("load", function(){

	// debounce
	//Code from https://tinyurl.com/ttd83xe6
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

	//Code from https://stackoverflow.com/a/15032300
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
			darkmode = readCookie('darkmode') == "1" ? true : false;
		}
	}
	//Dark mode is true by "default", so this will turn it off if dark mode SHOULD be off (confusing as hell but ok)
	if (darkmode == false){
		toggleDarkMode(disableAnimation=true,saveToCookie=false);
	}
	$('#input-darkmode').prop('checked', darkmode);

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
	if (initID == ""){
		$("#id-input-box").val(readCookie("idnumber"));
	}
	else{
		$("#id-input-box").val(initID);
	}

	//get info closed cookie and hide or show info accordingly
	if (!ignorecookiepolicy){
		if (readCookie("infoClosed") != "closed") {
			textBoxOpen('#text_cookies_info')
		}
	}

	//get and set current week
	week = initWeek;
	$(".input-week").val(week);
	$(".arrow-center-text").text(week);
	$(".arrow-center").attr("title", ("Current week (" + week + ")"));

	//load timetable after cookie info get
	if (readCookie("infoClosed") == "closed" || ignorecookiepolicy){
		console.log("load timetable after cookie info get");
		updateTimetable();	
	}

	updateMenuButtonsBasedOnSize();
	checkIfIDTextFits();

	// TRIGGERS
	//update timetable to fit new window size
	var update_timetable_to_fit_new_window_size = debounce(function() {
		console.log("update timetable to fit new window size");
		$("#schedule").fadeOut(500);
		updateMenuButtonsBasedOnSize();
		updateTimetable();
		checkIfIDTextFits();
	}, 250);
	window.addEventListener('resize', update_timetable_to_fit_new_window_size);

	//blink arrow and go move week on timetable
	$(".arrow-left").on("click", function(){
		$('.arrow-left').addClass('arrow-loading');
		$("#schedule").fadeOut(500, function(){
			if ($("#input-day").is(':checked')){
				day -= 1;
				if (day < 1){
					week -= 1;
					day = 5;
					//UpdateEntryInUrlArguments('week',week);
				}
				//UpdateEntryInUrlArguments('day',day);
			}
			else{
				week -= 1;
				//UpdateEntryInUrlArguments('week',week);
			}
			$(".input-week").val(week);
			updateTimetable();
		});
	});

	//blink arrow and go move week on timetable
	$(".arrow-center").on("click", function(){
		$('.arrow-center').addClass('arrow-loading');
		$("#schedule").fadeOut(500, function(){
			if ($("#input-day").is(':checked')){
				$('#input-day').prop('checked', false);
			}
			week = initWeek;
			$(".input-week").val(initWeek);
			updateTimetable();
		});
	});

	//blink arrow and go move week on timetable
	$(".arrow-right").on("click", function(){
		$('.arrow-right').addClass('arrow-loading');
		$("#schedule").fadeOut(500, function(){
			if ($("#input-day").is(':checked')){
				day += 1;
				if (day > 5){
					week += 1;
					day = 1;
					//UpdateEntryInUrlArguments('week',week);
				}
				//UpdateEntryInUrlArguments('day',day);
			}
			else{
				week += 1;
				//UpdateEntryInUrlArguments('week',week);
			}
			$(".input-week").val(week);
			updateTimetable();			
		});
	});

	//update timetable on related input
	var update_timetable_on_related_input = debounce(function() {
		$("#schedule").fadeOut(500, function(){
			console.log('update timetable on related input (AFTER DEBOUNCE)');
			updateTimetable();
		});
	}, 350);
	$('#id-input-box').on('input', update_timetable_on_related_input)

	//If private ID, then this textbox shows up, so that the user can change the ID
	var update_timetable_on_related_input = debounce(function() {
		$("#schedule").fadeOut(500, function(){
			$('#id-input-box').val($('#id-input-box2').val());

			//Sets value back to the private ID if input is empty
			if ($('#id-input-box').val() == ""){
				if (initID == ""){
					$("#id-input-box").val(readCookie("idnumber"));
				}
				else{
					$("#id-input-box").val(initID);
				}
			}
			updateTimetable();
		});
	}, 350);
	$('#id-input-box2').on('input', update_timetable_on_related_input)

	//unreliable fix, need more investigation on why input week arrows dont work.
	$(".input-week-container").on("click", function(){
		$(".input-week").focus();
	});

	//unreliable fix, need more investigation on why input week arrows dont work.
	$(".input-week").on("click", function(){
		$(".input-week").focus();
	});

	//update timetable on related input
	$('.input-week').on('input', function() {
		console.log('update timetable on related input 2');
		updateTimetable();
	});

	//update timetable on related button click
	$('#input-day').on('click', function() {
		console.log('update timetable on related button click');
		// if ($("#input-day").is(':checked')){
		// 	day = initDay;
		// 	week = initWeek;
		// }
		updateTimetable();
	});

	//update timetable on related button click
	$('#roundedMode').on('click', function() {
		console.log('update timetable on related button click 2');
		updateTimetable();
	});

	//handles menu button clicking
	$('.menuButton').on('click', function(){
		$('.controls').slideToggle('fast', function(){
			$('.controls-container').fadeIn(0);
			if ($(this).is(':visible')){
				$(this).css('display','flex');
				$('#schedule').addClass("menuBgBlur");
				$(".menuIcon").removeClass("fa-bars").addClass("fa-times");
			}else{
				$('#schedule').removeClass("menuBgBlur");
				$(".menuIcon").removeClass("fa-times").addClass("fa-bars");
			};
		});
	});

	// hide divs and remove focus from inputs when timetable is clicked
	$('#schedule').on('click', function(){
		hideControls();
		$(".input-idnumber").blur();
		$(".savedIDs").fadeOut("fast");
		checkIfIDTextFits();
	});

	// remove focus from input when enter is clicked for cleaner ux
	$('.input-idnumber').keypress(function(event){
		var keycode = (event.keyCode ? event.keyCode : event.which);
		if(keycode == '13'){
			hideControls();
			$(".input-idnumber").blur();
		};
	});

	//hide controls if enter is clicked in week input
	$('.input-week').keypress(function(event){
		var keycode = (event.keyCode ? event.keyCode : event.which);
		if(keycode == '13'){
			hideControls();
		};
	});

	// hide controls when save button is clicked
	$('.savebutton').on("click", function(){
		hideControls();
	});

	// close saveIDs if clicked outside of div
	$(document).mouseup(function(e){
	var container = $(".savedIDs");

		// if the target of the click isn't the container nor a descendant of the container
		if (!container.is(e.target) && container.has(e.target).length === 0) 
		{
		    container.fadeOut("fast");
		}
	});

	// Moves the timetable down so it doesnt overlay the navbar
	$(document).ready(function() {
		$("#scheduleBox").css("top", $(".navbar").height());
	});

	if (showContactOnLoad){
		textBoxOpen('#text_contact_info');
		//contacttextBoxOpen('#text_cookies_info');
	}

	// Page finished loading, slide up loader screen
	$(".loader-main").slideToggle();

	console.log("script.js is loaded");
});
