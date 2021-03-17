var dateModifier = 0;
var week = 0;
var date = new Date();
var dateDay = date.getDay();
var scheduleAge = 0

//get week number function
Date.prototype.getWeek = function(){
	var onejan = new Date(this.getFullYear(), 0, 1);
	return Math.ceil((((this - onejan) / 86400000) + onejan.getDay() + 1) / 7);
} 

// show and update saved url's
function showSaved(){

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
function getShareableURL() {
	var url = requestURL + 'API/SHAREABLE_URL?id=' + $(".input-idnumber").val();
	$.getJSON(url, function(data){
		updateClipboard(data['result']['url']);
		// alert("Kopierade din privata link");
		window.location.href = data['result']['url'];
	})
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

	//hide controls div before load
	hideControls();

	if (loadAutomaticly){
		//get idnumber cookie and input data
		$(".input-idnumber").val(readCookie("idnumber"));
	}
	
	//hide saved ids div before load
	$(".savedIDs").fadeOut(0);


	//automatically enable day mode for mobile devices
	if($( window ).width() <= 820){
		$('#input-day').prop('checked', true);	
	}

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
	week = (new Date()).getWeek() - 1;
	$(".input-week").val(week);
	$(".arrow-center-text").text(week);
	$(".arrow-center").attr("title", ("Current week (" + week + ")"));

	//load timetable after cookie info get
	if(loadAutomaticly){
		console.log("load timetable after cookie info get")
		updateTimetable();
	}
	else{
		console.log('Did not load automaticly, since "loadAutomaticly" was false');
	}

	// Page finished loading, slide up loader screen
	$(".loader-main").slideToggle();


	// TRIGGERS

	// update timetable to fit new window size
	var update_timetable_to_fit_new_window_size = debounce(function() {
		console.log("update timetable to fit new window size");
		updateTimetable();
	}, 250);
	window.addEventListener('resize', update_timetable_to_fit_new_window_size);

	//blink arrow and go move week on timetable
	$(".arrow-left").on("click", function(){
		$('.arrow-left').addClass('arrow-loading');
		$("#schedule").fadeOut(500, function(){
			$(".input-week").val( parseInt($(".input-week").val()) - 1);
			updateTimetable();
		});
	});

	//blink arrow and go move week on timetable
	$(".arrow-center").on("click", function(){
		$('.arrow-center').addClass('arrow-loading');
		$("#schedule").fadeOut(500, function(){
			$(".input-week").val( new Date().getWeek() - 1);
			updateTimetable();
		});
	});

	//blink arrow and go move week on timetable
	$(".arrow-right").on("click", function(){
		$('.arrow-right').addClass('arrow-loading');
		$("#schedule").fadeOut(500, function(){
			$(".input-week").val( parseInt($(".input-week").val()) + 1);
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

	//create new save item when enter is clicked in input box. 

	//FIX NEEDED: solutions coming soon
	//-create button (preferred)
	//-show label

	$('#saveItem').keypress(function(event){
		var keycode = (event.keyCode ? event.keyCode : event.which);
		if(keycode == '13'){
			savedIDs = readCookie("savedIDs");

			savedIDs +=	($("#saveItem").val() + "|");

			$("#saveItem").val("");

			createCookie("savedIDs", savedIDs, 360);

			showSaved();
		};
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
