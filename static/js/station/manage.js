$(function(){
	var tabCreationManager = new TabCreationManager();
});

function TabCreationManager(){
	this.page_id = null;
	this.page_name = null;
	this.listen();
}

TabCreationManager.prototype = {
	
	listen: function(){
		var that = this;
		$(".station a.btn").click(function(){
			var obj = $(this);
			that.page_id = $(this).attr("id");
			that.page_name = $(this).parent().prev().children().first().html();

			// Display loader gif
			var loader = $(this).prev()
			loader.css("visibility", "visible")
						
			that.createTab(function(response){
				that.displayFeedback(obj, loader, response);
			});
			
			return false;
		});
	},
	
	createTab: function(callback){
		var that = this;
		// Make sure facebook.js has been loaded
		if(FACEBOOK){
			FACEBOOK.putTab(that.page_id, callback)
		}
		else{
			callback(false)
		}
	},
	
	displayFeedback: function(obj, loader, response){

			// Hide loader gif
			obj.prev().css("visibility", "hidden");
			
			if(response){
				obj.addClass("success").html("Installed")
			}
			else{
				obj.addClass("danger").html("Error...")
			}
	},
	
}




