/*
    triggers.js 

    Contains all the triggers. They get their own file because it was too messy in the scripts.js file
*/

$(window).on("load", function(){

    //update timetable to fit new window size
    var update_timetable_to_fit_new_window_size = debounce(function() {
        console.log("update timetable to fit new window size");
        $("#schedule").fadeOut(500);
        updateMenuButtonsBasedOnSize();
        updateTimetable();
        checkIfIDTextFits();
    }, 250);
    window.addEventListener('resize', update_timetable_to_fit_new_window_size);

    //update timetable on related input
    var update_timetable_on_related_input = debounce(function() {
        $("#schedule").fadeOut(500, function(){
            console.log('update timetable on related input (AFTER DEBOUNCE)');
            updateTimetable();
        });
    }, 450);
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
    }, 450);
    $('#id-input-box2').on('input', update_timetable_on_related_input)

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

    //handles menu button clicking
    $('.menuButton').on('click', function(){
        showControls();
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

    $("#school-select-box").change(function(){
        schoolSelected(document.getElementById("school-select-box").value);
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
});



// //update timetable on related button click
// $('#roundedMode').on('click', function() {
// 	console.log('update timetable on related button click 2');
// 	updateTimetable();
// });

// //Code from https://stackoverflow.com/a/1846733
// document.onkeypress = function(evt) {
// 	if (mobileRequest || document.activeElement == document.getElementById('id-input-box') || document.activeElement == document.getElementById('id-input-box2')){
// 		return;
// 	}
// 	else
// 	{
// 		evt = evt || window.event;
// 		var charCode = evt.keyCode || evt.which;
// 		var charStr = String.fromCharCode(charCode);

// 		if (charStr.toLowerCase() == "f"){
// 			if (hideNavbar){
// 				f_showNavbar();
// 			}
// 			else{
// 				f_hideNavbar();
// 			}
// 		}
// 	}
// };
