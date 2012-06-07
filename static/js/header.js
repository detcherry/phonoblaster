$(function(){
	
	$("a.dropdown").click(function(){
		var li = $(this).parent();
		if(li.hasClass("show")){
			li.removeClass("show").addClass("hide")
			$("#dropdown-menu").show();
			
			var stations = $("ul#dropdown-stations")
			var number_of_stations = stations.children().length
			var slimscroll = stations.parent().find(".slimScrollBar").length;
						
			if(number_of_stations > 3 && slimscroll == 0){
				stations.slimScroll({
					height: stations.height() + 10,
				})
			}
			
		}
		else{
			li.removeClass("hide").addClass("show")
			$("#dropdown-menu").hide();
		}
		
		$(this).blur();
		return false;
	})
	

	
})