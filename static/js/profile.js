$(function(){
	PROFILE_MANAGER = new ProfileManager(PROFILES);
})

function ProfileManager(profiles){
	this.profiles = profiles;
	this.choosen = null;
	this.shortname = null;
	this.recommendations = false;
	this.request_counter = 0;
	this.background = null;
	
	this.backgrounds = [{
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
	this.selectListen();
	this.uploadListen();
	this.removeListen();
}

ProfileManager.prototype = {
	
	init: function(){
		
		// Case one profile
		if(this.profiles.length == 1){
			this.choosen = this.profiles[0]
			
			// Automatically fill box with a default username
			this.fillUsername();
		}
		// Case 2+ profiles
		else{
			this.chooseListen();
		}
		
		// Fill thumbnails in background screen
		this.fillThumbnails();
		
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
				$("#username .warning").show();
			}
			
			$(this).blur();
			return false;
		})

		// Background next button
		$("#background a.box-next").click(function(){
			
			if(that.background){
				that.finalize();
			}
			else{
				$("#background .warning").show();
			}
			
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
			}
			// Profile already created, go to station
			else{
				window.location.href = "/profile/switch/" + that.choosen.key_name;
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
	
	fillThumbnails: function(){
		
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

							callback(json.availability);
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
				$("a#right-carousel").css("visibility", "hidden");	
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
				$("a#left-carousel").css("visibility", "hidden");
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
		var newMarginLeft = new_value + "px";
		
		$("#carousel-list").css("marginLeft", newMarginLeft);
	},
	
	browseRight: function(){
		this.browse(-122)
	},
	
	browseLeft: function(){
		this.browse(122)
	},
	
	selectListen: function(){
		
		var that = this;
		$("a.carousel-img").live("click", function(){
			that.selectReset();
			
			var id = $(this).attr("name");
			
			// Find the corresponding background
			for(var i=0, c=that.backgrounds.length; i<c; i++){
				var background = that.backgrounds[i];
				if(id == background.id){
					that.background = background;
					break;
				}
			}
			
			// Put borders in blue
			$(this).css("borderColor","#00BBED");
			
			that.displayBackground();
			
			// Remove warning
			$("#background .warning").hide();
			
			$(this).blur();
			return false;
		})
		
	},
	
	selectReset: function(){
		// No background selected
		this.background = null;
		
		// Empty background
		$("#img").empty();
		
		// Remove blue borders
		$("a.carousel-img").css("borderColor","transparent");
	},
	
	displayBackground: function(){
		// Put big image in the background
		$("<img/>")
			.attr("src", this.background.src_full)
			.addClass("stretch")
			.prependTo($("#img"))
	},
	
	uploadListen: function(){
		var that = this
		
		// We listen to any image upload
		$("input[id='picture']").bind("change", function(event){
			
			// Hide text
			$("#carousel-mine p").css("visibility","hidden")
			
			// Show loader
			$("#carousel-mine img.loader").show();
			
			// Unselect other background
			that.selectReset();
			
			// Submit
			$("form#upload").submit();
		})
		
		// We listen to any form submit event
		$("form#upload").bind("submit",function(){
			$(this).ajaxSubmit({
				success: that.uploadCallback,
				dataType: "json",
				timeout: 60000,
			});
			
			return false;	
		});
	},
	
	uploadCallback: function(responseText, statusText, xhr, form){
		// Remove warning
		$("#background .warning").hide();
		
		// Hide loader
		$("#carousel-mine img.loader").hide();
		
		var json = responseText;
		var response_class = "";
		var response_message = "<span>Your picture</span><br/><span>(.jpg, .png, .gif)</span><br/><span>Max 1 Mo</span>";
				
		try{
			if(json.response){
				
				var blob_full = json.blob_full;
				var blob_thumb = json.blob_thumb;
				var src_full = json.src_full;
				var src_thumb = json.src_thumb;

				var background = {
					"id": 0,
					"src_full": src_full,
					"src_thumb": src_thumb,
				}
				
				PROFILE_MANAGER.background = background;
				PROFILE_MANAGER.backgrounds.push(background);
				
				// Add image in the background (full size)
				PROFILE_MANAGER.displayBackground();
				
				// Add image in the carousel (thumbnail)
				$("#carousel-mine").append(
					$("<a/>")
						.attr("href","#")
						.addClass("carousel-img")
						.attr("name", 0)
						.css("borderColor", "#00BBED")
						.append($("<img/>").addClass("thumb").attr("src", src_thumb))
				)
				.append(
					$("<a/>")
						.attr("href","#")
						.addClass("remove-carousel-img")
						.html("X")
				)			
			}
			else{				
				var response_class = "error";
				// Picture too big
				if(json.error == 1){
					response_message = "Picture too big:<br/> > 1 Mo.<br/>Please retry.";
				}
				// File not a picture
				else if(json.error == 2){
					response_message = "Only .jpeg, .jpg, .png, .gif pictures.<br/>Please retry."
				}
				// No picture
				else{
					response_message = "No picture uploaded.<br/>Please retry."
				}
			}
			// Reinitialize the form destination in case the user would like to change the picture
			$("form#upload").attr("action", json.blobstore_url)
		}
		catch(e){
			var response_class = "error";
			var response_message = "An error occurred. Please reload the page."	
		}
				
		// Display text
		$("#carousel-mine p").removeClass("error").addClass(response_class).css("visibility","visible").html(response_message)
		
	},
	
	removeListen: function(){
		
		var that = this;
		$("a.remove-carousel-img").live("click", function(){
			
			// Remove carousel img
			$("#carousel-mine a.carousel-img").remove();
			
			if(that.background.id == 0){
				// Unselect current background
				that.selectReset();
			}
			
			// Remove background from backgrounds list
			var to_remove = that.backgrounds.pop();
			
			// Remove cross
			$(this).remove();
			
			// Ajax call to remove both full size image and thumbnail
			var blob_full = to_remove.blob_full;
			var blob_thumb = to_remove.blob_thumb;
			that.remove(blob_full);
			that.remove(blob_thumb);
			
			$(this).blur()
			return false;
		})
		
	},
	
	remove: function(blob_key){
		
		var that = this;
		var delete_url = "/picture/" + blob_key + "/delete"
		
		$.ajax({
			url: delete_url,
			type: "DELETE",
			dataType: "json",
			timeout: 60000,
			error: function(xhr, status, error) {
				PHB.log("An error occured " + error)
			},
			success: function(json){
				PHB.log("Blob removed from blobstore")
			},
		});
		
	},
	
	finalize: function(){
		// Show loader
		$("#background .box-footer .loader").show();
		
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
				background: JSON.stringify(that.background),
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