$(function(){
	PROFILE_MANAGER = new ProfileManager(PROFILES);
})

function ProfileManager(profiles){
	this.profiles = profiles;
	this.choosen = null;
	this.shortname = null;
	this.recommendations = false;
	this.request_counter = 0;
	
	this.init();
	this.previousListen();
	this.typeListen();
	this.nextListen();
}

ProfileManager.prototype = {
	
	init: function(){
		
		// Case one profile
		if(this.profiles.length == 1){
			this.choosen = this.profiles[0]
			this.fillUsername();
		}
		// Case 2+ profiles
		else{
			this.chooseListen();
		}
	},
	
	previousListen: function(){
		
		var that = this;
		$("a.box-previous").click(function(){
			that.moveLeft();		
			
			$(this).blur();
			return false;
		})
		
	},
	
	nextListen: function(){
		
		var that = this;
		
		$("a.box-next").click(function(){
			that.finalize();
			
			$(this).blur();
			return false;
		})
		
	},
	
	chooseListen: function(){
		
		var that = this;
		$("a.item").click(function(){
			
			var id = $(this).attr("id");
			for(var i=0, c=that.profiles.length; i<c; i++){
				var profile = that.profiles[i]
				if(id == profile.key_name){
					that.choosen = profile;
				}
			}
			
			that.fillUsername();
			
			that.moveRight();
			
			$(this).blur();
			return false;
		})
		
	},

	move: function(offset){
		
		var marginLeft = $("#steps-wrapper").css("marginLeft");
		var re = new RegExp("px","g");
		var value = parseInt(marginLeft.replace(re, ""),10);
		var new_value = value + offset;
		var newMarginLeft = new_value + "px"
		
		$("#steps-wrapper").animate({
			"marginLeft": newMarginLeft,
		})
		
		$(window).scrollTop(0)
	},

	moveRight: function(){
		this.move(-600)
	},
	
	moveLeft: function(){
		this.move(600)
	},
	
	fillUsername: function(){
		var src = "https://graph.facebook.com/" + this.choosen.key_name + "/picture?type=square"
		$("#username .picture")
			.empty()
			.append($("<img/>").attr("src", src));
		
		var name = this.choosen.name.substr(0,29).toLowerCase().replace(/ /g,'');
		var re = new RegExp("[^a-zA-Z0-9_]","g");
		var shortname = name.replace(re,"");
		$("#username input").val(shortname);
		
		var that = this;
		that.checkShortname(function(response){
			that.displayAvailability(response);
		});
	},
	
	checkShortname: function(callback){
		old_shortname = this.shortname;
		this.shortname = $("#username input").val();
		
		var re = new RegExp("[^a-zA-Z0-9_]","g");
		if(re.test(this.shortname)){
			// Incorrect characters
			$("#username .status")
				.addClass("error")
				.removeClass("available")
				.removeClass("checking")
				.html("Incorrect");
		}
		else{
			if(this.shortname.length < 4){
				// Display checking message
				$("#username .status")
					.addClass("error")
					.removeClass("available")
					.removeClass("checking")
					.html("Too short");
			}
			else{
				if(this.shortname.length <= 30 && this.shortname != old_shortname){
					// Display checking message
					$("#username .status")
						.removeClass("error")
						.removeClass("available")
						.addClass("checking")
						.html("Checking...");

					this.request_counter++

					var that = this;
					$.ajax({
						url: "/station/check",
						type: "POST",
						dataType: "json",
						timeout: 60000,
						data: {
							shortname: that.shortname,
						},
						error: function(xhr, status, error) {
							PHB.log('An error occurred: ' + error + '\nPlease retry.');
							callback(false);
						},
						success: function(json){
							that.request_counter--;

							callback(json.availability)
						},
					});
				}
			}
		}
	
	},
	
	displayAvailability: function(response){
		if(this.request_counter == 0 && $("#username .status").html() == "Checking..."){
			// Display availability status
			if(response){
				$("#username .status")
					.removeClass("checking")
					.removeClass("unavailable")
					.addClass("available")
					.html("Available");
			}
			else{
				$("#username .status")
					.removeClass("checking")
					.removeClass("available")
					.addClass("unavailable")
					.html("Unavailable");
			}
		}
	},
	
	typeListen: function(){
		
		// Attach the input box to 2 event handlers
		var that = this;
		$("#username input").keyup(function(event){
			that.checkShortname(function(response){
				that.displayAvailability(response);
			})
		})
		
	},
	
	finalize: function(){
		PHB.log("I have to finalize")
	},
}