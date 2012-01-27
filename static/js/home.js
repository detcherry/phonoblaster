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
		$(".contribution a.btn").click(function(){
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
			FACEBOOK.createPhonoblasterTab(that.page_id, callback);
		}
		else{
			callback.call(this, false);
		}
	},
	
	displayFeedback: function(obj, loader, response){

			// Hide loader gif
			obj.prev().css("visibility", "hidden");

			// Build text to display
			var repl = $("<span/>").addClass("btn");
			if(response){
				repl.addClass("success").html("Created!");
			}else{
				repl.addClass("danger").html("Error...");
			}

			// Replace link by text
			obj.replaceWith(repl);

			// Display popup if response positive
			if(response){
				var stationCreationManager = new StationCreationManager(this.page_id, this.page_name);
			}
	},
	
}

function StationCreationManager(page_id, page_name){
	this.page_id = page_id;
	this.page_shortname = "";
	
	this.updatePopupContent(page_name)
	this.displayPopup();
	var that = this;
	this.checkShortname(function(response){
		that.displayAvailability(response);
	});
	this.listen();
}

StationCreationManager.prototype = {
	
	updatePopupContent: function(page_name){
		$("input#page-id").val(this.page_id);
		
		var to_clean = page_name.substr(0,29).toLowerCase().replace(/ /g,'');
		var re = new RegExp("[^a-zA-Z0-9_]","g");
		to_display = to_clean.replace(re,"");
		
		$("input#page-shortname").val(to_display);
	},
	
	displayPopup: function(){		
		// Display fancy box
		$.fancybox($("#popup-contribution"), {
			topRatio: 0.4,
			modal: true,
		});
	},
	
	listen: function(){
		// Attach the input box to 2 event handlers
		var that = this;
		$("input#page-shortname").keydown(function(event){
			that.preventForbiddenCharacters(event)
		});
		$("input#page-shortname").keyup(function(event){
			that.checkShortname(function(response){
				that.displayAvailability(response);
			})
		})
		
		// Attach the form to an event
		$("#address-confirmation form").submit(function(event){
			if($("#shortname-status").html() != "Available"){
				$("#shortname-warning").show();
				event.preventDefault()
			}
		})
	},
	
	preventForbiddenCharacters: function(event){
		var authorized_keycodes = [
			8,  //back
			37, //left arrow
			38, //up arrow
			39, //right arrow
			40, //down arrow
			46, //suppr
			48, //0
			49, 
			50, 
			51, 
			52, 
			53, 
			54, 
			55, 
			56, 
			57, //9
			65, //a
			66, 
			67, 
			68, 
			69, 
			70, 
			71, 
			72, 
			73, 
			74,
			75, 
			76, 
			77, 
			78, 
			79, 
			80, 
			81, 
			82, 
			83, 
			84, 
			85, 
			86, 
			87, 
			88, 
			89, 
			90, //z
		];
		
		var neutral_keycodes = [
			8,  //back
			37, //left arrow
			38, //up arrow
			39, //right arrow
			40, //down arrow
			46, //suppr
		]
		
		if(jQuery.inArray(event.keyCode, authorized_keycodes) == -1){
			// An unauthorized key has been pressed
			event.preventDefault();
		}
		else if(this.page_shortname.length == 30){
			if(jQuery.inArray(event.keyCode, neutral_keycodes) == -1){
				// A non neutral key has been pressed whereas we have reached the limit
				event.preventDefault();
			}
		}
	},
	
	checkShortname: function(callback){
		old_page_shortname = this.page_shortname;
		this.page_shortname = $("input#page-shortname").val();
		
		if(this.page_shortname.length <= 30 && this.page_shortname != old_page_shortname){
			// Display checking message
			$("#shortname-status")
				.removeClass("unavailable")
				.removeClass("available")
				.addClass("checking")
				.html("Checking...");

			var that = this;
			$.ajax({
				url: "/station/check",
				type: "POST",
				dataType: "json",
				timeout: 60000,
				data: {
					page_shortname: that.page_shortname,
				},
				error: function(xhr, status, error) {
					PHB.log('An error occurred: ' + error + '\nPlease retry.');
					callback.call(this, false);
				},
				success: function(json){
					if(json.availability){
						callback.call(this, json.availability)
					}
					else{
						callback.call(this, false);
					}
				},
			});
		}
	},
	
	displayAvailability: function(response){		
		// Display availability status
		if(response){
			$("#shortname-status")
				.removeClass("checking")
				.removeClass("unavailable")
				.addClass("available")
				.html("Available");
		}
		else{
			$("#shortname-status")
				.removeClass("checking")
				.removeClass("available")
				.addClass("unavailable")
				.html("Unavailable");
		}
		
	},	
}








