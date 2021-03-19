var week;
var day = initDay;

//get week number function
Date.prototype.getWeek = function(){
	var onejan = new Date(this.getFullYear(), 0, 1);
	return Math.ceil((((this - onejan) / 86400000) + onejan.getDay() + 1) / 7);
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
	if (el.val() != lastKnownID){
		if (inputExceeded()){
			while(inputExceeded()){
				var oldSize = parseInt(el.css("--font-size"),10);
				console.log(oldSize);
				var newSize = oldSize - 1;
				console.log(newSize);
				
				if(newSize < 1){
					break;
				}
	
				el.css({
					"font-size":"min( " + newSize + "px,24px)",
					"--font-size":newSize + "px"
				});
			}
		}
		else{
			while(!inputExceeded()){
				var oldSize = parseInt(el.css("--font-size"),10);
				console.log(oldSize);
				var newSize = oldSize + 1;
				console.log(newSize);
				
				if(newSize > 24){
					break;
				}
	
				el.css({
					"font-size":"min( " + newSize + "px,24px)",
					"--font-size":newSize + "px"
				});
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
		$(".savedList").append("<li class='savedItems'>You have no saved URL's</li>");
	}
	else{
		$(".savedList").append('<button class="clearSavedItems mobileSaved control-container" onclick="deleteAllURLCookies();">Ta bort alla</button>');
	}
	
	$(".savedIDs").fadeIn("fast");

};

//accept cookie policy
function infoClose(){
	createCookie("infoClosed", "closed", 360);
	$('.navbar').removeClass("infoBgBlur");
	$('.info').fadeOut("fast");
	$( ".input-idnumber" ).focus();
};

//dismiss changelog
function newsClose(){
	createCookie("newsClosed", "closed", 360);
	$('.news').hide();
	$( ".input-idnumber" ).focus();	
};

//save inputed item in box
function savedItemClicked(item){
	$(".input-idnumber").val(item.text());
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
	   url: requestURL + 'API/SHAREABLE_URL?id=' + $(".input-idnumber").val(), 
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

//events on load & event triggers.
$(window).on("load", function(){

	// debounce
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

	if (privateURL){
		$('#id-input-box').css("display", "none");
	}


	//hide controls div before load
	hideControls();

	//get idnumber cookie and input data
	if (initID == ""){
		$(".input-idnumber").val(readCookie("idnumber"));
	}
	else{
		$(".input-idnumber").val(initID);
	}
	
	//hide saved ids div before load
	$(".savedIDs").fadeOut(0);

	//enable day mode by default for mobile devices
	$('#input-day').prop('checked', initDayMode);
	
	//get info closed cookie and hide or show info accordingly
	if(readCookie("infoClosed") == "closed"){
		$('.info').hide();
		$('.navbar').removeClass("infoBgBlur");
	}else{
		$('.info').fadeIn();
		$('.navbar').addClass("infoBgBlur");
	}

	//get news closed info (deprecated, to be updated and readded.)
	if(readCookie("newsClosed") == "closed"){
		$('.news').hide();
	}else{
		$('.news').show();
	}

	//get rounded mode cookie for rounded screen devices
	if(readCookie("roundedMode") == "rounded"){
		$('#roundedMode').prop('checked', true);
	}else{
		$('#roundedMode').prop('checked', false);
	}

	//get and set current week
	week = initWeek;
	$(".input-week").val(week);
	$(".arrow-center-text").text(week);
	$(".arrow-center").attr("title", ("Current week (" + week + ")"));

	//load timetable after cookie info get
	console.log("load timetable after cookie info get")
	updateTimetable();
	updateMenuButtonsBasedOnSize();
	checkIfIDTextFits();

	// Page finished loading, slide up loader screen
	$(".loader-main").slideToggle();

	// TRIGGERS
	// update timetable to fit new window size
	var update_timetable_to_fit_new_window_size = debounce(function() {
		console.log("update timetable to fit new window size");
		checkIfIDTextFits();
		updateMenuButtonsBasedOnSize();
		updateTimetable();
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
				}
			}
			else{
				week -= 1;
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
				}
			}
			else{
				week += 1;
			}
			$(".input-week").val(week);
			updateTimetable();			
		});
	});

	//update timetable on related input
	var update_timetable_on_related_input = debounce(function() {
		console.log('update timetable on related input (AFTER DEBOUNCE)');
		updateTimetable();
	}, 350);
	$('.input-idnumber').on('input', update_timetable_on_related_input)

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
		$('.controls').slideToggle('fast', function() {
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

	console.log("script.js is loaded");

});
