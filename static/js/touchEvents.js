// Touchswipe library custom events.

$(window).on("load", function(){

	$(function() {
	      //Enable swiping...
      $("#schedule").swipe( {
        //Single swipe handler for left swipes
        swipeLeft:function(event, direction, distance, duration, fingerCount) {

        	if($(window).width() <= 820){

        		//hide timetable
				$("#schedule").css({"transform": "translateX(-100%) scale(0.8)"});

				setTimeout(hideAndMoveLeft, 100);
				function hideAndMoveLeft() {

	        		if ($("#input-day").is(':checked')){

		        		if (dateDay + dateModifier == 0){
		        			dateModifier = 0;
		        		} else if (dateDay + dateModifier == 6){
		        			dateModifier = 0;
		        		} else {
		        			dateModifier += 1;
		        		};

	        		} else {
	        			week = parseInt(week) + parseInt(1);
	        			$(".input-week").val(week);
	    			}

		        	updateTimetable();

					// show timetable again	
					$("#schedule").css({"transform": "translateX(100%) scale(0.8)", "opacity": 0});
				}
			}

        },
        swipeRight:function(event, direction, distance, duration, fingerCount) {

        	if($(window).width() <= 820){


				//hide timetable
				$("#schedule").css({"transform": "translateX(100%) scale(0.8)"});

				setTimeout(hideAndMoveRight, 100);
				function hideAndMoveRight() {

					if ($("#input-day").is(':checked')){

		        		if (dateDay + dateModifier == 0){
		        			dateModifier = 0;
		        		} else if (dateDay + dateModifier == 6){
		        			dateModifier = 0;
		        		} else {
		        			dateModifier -= 1;
		        		};

	        		} else {
	        			week -= parseInt(1);
	        			$(".input-week").val(week);
	    			}
	        		updateTimetable();

	    			// show timetable again
					$("#schedule").css({"transform": "translateX(-100%) scale(0.8)", "opacity": 0});

				}
			}
	        

        },
        swipeUp:function(event, direction, distance, duration, fingerCount) {

        	if($(window).width() <= 820){

        		//hide timetable
				$("#schedule").css({"transform": "translateY(-100%) scale(0.8)"});

				setTimeout(hideAndMoveUp, 100);
				function hideAndMoveUp() {
	        		week = (new Date()).getWeek();
		        	dateModifier = 0;
					$(".input-week").val((new Date()).getWeek() - 1);
		        	updateTimetable();

		        	//show timetable again
					$("#schedule").css({"transform": "translateY(100%) scale(0.8)", "opacity": 0});
				}
			}

        },
        swipeDown:function(event, direction, distance, duration, fingerCount) {

        	if($(window).width() <= 820){

        		$(".menuButton").click();
			}

        },
        threshold:30
      });
    });

    $(function() {
      //Enable swiping...
      $(".controls").swipe( {
        //Single swipe handler for left swipes
        swipeUp:function(event, direction, distance, duration, fingerCount) {
        	hideControls();
        },
        threshold:30
      });
    });
});