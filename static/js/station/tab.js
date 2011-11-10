$(function(){
	var aTabController = new tabController();
	aTabController.init();
});

function tabController(){
}

tabController.prototype = {
	
	init: function(){
		
		// Reveal initial content area(s).
	 	//$("#tab_content_wrap")
		//	.each(function(){
		//		$(this).find(".tab_content:first").show();
		//	});
		
		//Find the tab that is current
		// Unlike the previous code, this code is valid only if there is one tab system per page
		current_tab = $("#tabs a.current").attr("href");
		$(current_tab).show();
		
		// Listen for click on tabs.
	 	$("#tabs a").bind("click",function() {
			// If not current tab. 
			if (!$(this).hasClass("current")) {
				// Change the current indicator.
				 $(this)
					.addClass("current")
					.parent("li")
					.siblings("li")
					.find("a.current")
					.removeClass("current");
				
				// Show target, hide others.
				 $($(this).attr('href'))
					.show()
					.siblings(".tab_content")
					.hide();
			}
			
			// Nofollow.
			 this.blur();
			 return false;
		});
		
	},
	
}