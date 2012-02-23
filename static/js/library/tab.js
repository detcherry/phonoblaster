$(function(){
	var tab = new Tab();
});

function Tab(){
	this.init()
}

Tab.prototype = {
	
	init: function(){
		
		//Find the tab that is current
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
					.siblings(".tab-content")
					.hide();
			}
			
			// Nofollow.
			 this.blur();
			 return false;
		});
		
	},
	
}