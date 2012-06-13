$(function(){
	PROFILE_MANAGER = new ProfileManager(PROFILES);
})

function ProfileManager(profiles){
	this.profiles = profiles;
	this.choosen = null;
	this.shortname = null;
	this.recommendations = false;
	this.request_counter = 0;
	this.backgrounds = [];
	this.background = null;
	
	this.default_backgrounds = [{
		"id": 1,
		"blob_full": null,
		"blob_thumb": null,
		"src_full": "/static/images/backgrounds/full/sea.jpg",
		"src_thumb": "/static/images/backgrounds/thumb/sea.jpg",
	},{
		"id": 2,
		"blob_full": null,
		"blob_thumb": null,
		"src_full": "/static/images/backgrounds/full/legs.jpg",
		"src_thumb": "/static/images/backgrounds/thumb/legs.jpg",
	},{
		"id": 3,
		"blob_full": null,
		"blob_thumb": null,
		"src_full": "/static/images/backgrounds/full/pool.jpg",
		"src_thumb": "/static/images/backgrounds/thumb/pool.jpg",
	},{
		"id": 4,
		"blob_full": null,
		"blob_thumb": null,
		"src_full": "/static/images/backgrounds/full/river.jpg",
		"src_thumb": "/static/images/backgrounds/thumb/river.jpg",
	},{
		"id": 5,
		"blob_full": null,
		"blob_thumb": null,
		"src_full": "/static/images/backgrounds/full/egg.jpg",
		"src_thumb": "/static/images/backgrounds/thumb/egg.jpg",
	},{
		"id": 6,
		"blob_full": null,
		"blob_thumb": null,
		"src_full": "/static/images/backgrounds/full/road.jpg",
		"src_thumb": "/static/images/backgrounds/thumb/road.jpg",
	},{
		"id": 7,
		"blob_full": null,
		"blob_thumb": null,
		"src_full": "/static/images/backgrounds/full/statue.jpg",
		"src_thumb": "/static/images/backgrounds/thumb/statue.jpg",
	},{
		"id": 8,
		"blob_full": null,
		"blob_thumb": null,
		"src_full": "/static/images/backgrounds/full/tower.jpg",
		"src_thumb": "/static/images/backgrounds/thumb/tower.jpg",
	},{
		"id": 9,
		"blob_full": null,
		"blob_thumb": null,
		"src_full": "/static/images/backgrounds/full/wheat.jpg",
		"src_thumb": "/static/images/backgrounds/thumb/wheat.jpg",
	},{
		"id": 10,
		"blob_full": null,
		"blob_thumb": null,
		"src_full": "/static/images/backgrounds/full/skate.jpg",
		"src_thumb": "/static/images/backgrounds/thumb/skate.jpg",
	},{
		"id": 11,
		"blob_full": null,
		"blob_thumb": null,
		"src_full": "/static/images/backgrounds/full/deers.jpg",
		"src_thumb": "/static/images/backgrounds/thumb/deers.jpg",
	}]
	
	this.init();
	this.previousListen();
	this.typeListen();
	this.nextListen();
	this.browseListen();
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

		// Username next button
		$("#username a.box-next").click(function(){
			
			var status = $(".status").html();
			if(status == "Available"){
				// Reset the carousel position
				that.browseReset();
				
				// Move to the background screen
				that.moveRight();
			}
			else{
				$(".warning").show();
			}
			
			$(this).blur();
			return false;
		})

		// Background next button
		$("#background a.box-next").click(function(){
			
			alert("Finalize!")
			
			// Later on 
			// that.finalize();
			
			$(this).blur();
			return false;
		})
		
	},
	
	chooseListen: function(){
		
		var that = this;
		$("a.item").click(function(){
			
			// Find the item clicked by the user
			var id = $(this).attr("id");
			for(var i=0, c=that.profiles.length; i<c; i++){
				var profile = that.profiles[i]
				if(id == profile.key_name){
					that.choosen = profile;
				}
			}
			
			// Profile not created already, go to username screen
			if(!that.choosen.shortname){	
				// Automatically fill box with a default username
				that.fillUsername();

				// Move to the username screen
				that.moveRight();
				
				// Automatically fill backgrounds in the backgrounds screen
				that.retrieveBackgrounds();
			}
			// Profile already created, go to station
			else{
				window.location.href = "/" + that.choosen.shortname;
			}
			
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
		$("#username .picture").empty().append($("<img/>").attr("src", src));
		
		var name = this.choosen.name.substr(0,29).toLowerCase().replace(/ /g,'');
		var re = new RegExp("[^a-zA-Z0-9_]","g");
		var shortname = name.replace(re,"");
		$("#username input").val(shortname);
		
		var that = this;
		that.checkShortname(function(response){
			that.displayAvailability(response);
		});
	},
	
	retrieveBackgrounds: function(){
		this.backgrounds = [];
		
		var that = this
		if(this.choosen.type == "page"){
			// Fetch photos from Facebook
			FACEBOOK.retrievePagePhotos(this.choosen.key_name, function(urls){
				// If at least 5 pictures in page photos
				if(urls.length > 5){
					var max = 50;
					if(urls.length < max){
						max = urls.length
					}

					for(var i=0, c=max; i<c; i++){
						var src_big = urls[i].src_big;
						var src_big_width = urls[i].src_big_width;
						var src_big_height = urls[i].src_big_height;
						if(src_big && src_big.length > 0 && src_big_width >= src_big_height){
							that.backgrounds.push({
								"id": i,
								"blob_full": null,
								"blob_thumb": null,
								"src_full": src_big,
								"src_thumb": src_big,
							})
						}
					}
				}
				// If less than 5 pictures, default backgrounds are proposed
				else{
					that.backgrounds = that.default_backgrounds;
				}
				
				that.fillThumbnails();
				
			});
		}
		else{
			// Propose default backgrounds
			this.backgrounds = this.default_backgrounds;
			this.fillThumbnails();
		}
		
		
	},
	
	fillThumbnails: function(){
		// Empty list and fill it with new photos
		$("#carousel-list").empty();
		
		for(var i=0, c=this.backgrounds.length; i<c; i++){
			var background = this.backgrounds[i];
			
			$("#carousel-list").append(
				$("<a/>")
					.attr("href","#")
					.attr("name", background.id)
					.addClass("carousel-img")
					.append(
						$("<img/>").attr("src", background.src_thumb)
					)
			)
		}
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
					
				$(".warning").hide();
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
	
	browseListen: function(){
		
		var that = this;
		$("a#right-carousel").click(function(){
			// Display left carousel
			$("a#left-carousel").css("visibility","visible");
			
			// Hide right icon if no photo anymore
			var marginLeft = $("#carousel-list").css("marginLeft");
			var re = new RegExp("px","g");
			var value = parseInt(marginLeft.replace(re, ""),10);
			if(value < -122*(that.backgrounds.length-5)){
				$("a#right-carousel").css("visibility", "hidden")	
			}
			
			// Browse in the right direction
			that.browseRight();
			
			$(this).blur();
			return false;
		})
		
		$("a#left-carousel").click(function(){
			// Display right carousel
			$("a#right-carousel").css("visibility","visible");
			
			// Hide left icon if no photo anymore
			var marginLeft = $("#carousel-list").css("marginLeft");
			var re = new RegExp("px","g");
			var value = parseInt(marginLeft.replace(re, ""),10);
			if(value > -122){
				$("a#left-carousel").css("visibility", "hidden")
			}
			
			// Browse in the right direction
			that.browseLeft();
			
			$(this).blur();
			return false;
		})
		
	},
	
	browseReset: function(){
		$("a#left-carousel").css("visibility","hidden");
		$("#carousel-list").css("marginLeft","122px");
	},
	
	browse: function(offset){
		
		var marginLeft = $("#carousel-list").css("marginLeft");
		var re = new RegExp("px","g");
		var value = parseInt(marginLeft.replace(re, ""),10);
		var new_value = value + offset;
		var newMarginLeft = new_value + "px"
		
		$("#carousel-list").animate({
			"marginLeft": newMarginLeft,
		})
	},
	
	browseRight: function(){
		this.browse(-122)
	},
	
	browseLeft: function(){
		this.browse(122)
	},
	
	finalize: function(){
		// Show loader
		$("#username .loader").show();
		
		// Prevent any typing events
		$("#username input").keydown(function(event){
			event.preventDefault();
		})
		
		// Prevent any back events
		$("a.box-previous").unbind("click");
		$("a.box-previous").click(function(){
			$(this).blur();
			return false;
		});
		
		var that = this;
		$.ajax({
			url: "/profile/init",
			type: "POST",
			dataType: "json",
			timeout: 60000,
			data: {
				key_name: that.choosen.key_name,
				shortname: that.shortname,
			},
			error: function(xhr, status, error) {
				PHB.log('An error occurred: ' + error + '\nPlease retry.');
			},
			success: function(json){				
				if(json.response){
					// Create application if Facebook page
					if(that.choosen.type == "page"){
						FACEBOOK.putTab(that.choosen.key_name, function(response){
							// Redirect user to his new station
							window.location.href = PHB.site_url + "/" + that.shortname;
						})
					}
					else{
						// Redirect user to his new station
						window.location.href = PHB.site_url + "/" + that.shortname;
					}
				}
				else{
					PHB.error("Your station could not be created. Please reload this page.")
				}
			},
		});
		
	},
}