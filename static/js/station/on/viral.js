// ---------------------------------------------------------------------------
// VIRAL MANAGER
// ---------------------------------------------------------------------------

function ViralManager(station_client){
	this.station_client = station_client;
	this.listen();
}

ViralManager.prototype = {
	
	listen: function(){
		var that = this;
		
		// Listen to events to bring people inside station (from broadcaster or listener)
		$("#bring-people .btn").click(function(){
			// User must be logged in to share the station
			if(!that.station_client.user){
				FACEBOOK.login()
			}
			else{
				// Display popup
				that.bringPeoplePopup()
			}
			return false;
		});
		
		// Listen to submit events for bringing people inside station
		$("#popup-bring-people form").submit(function(event){
			event.preventDefault();
			
			var message = $("#popup-bring-people textarea").val();
			var link = PHB.site_url + "/" + that.station_client.station.shortname;
			var picture = PHB.site_url + "/" + that.station_client.station.shortname + "/picture";
			var btn = $("#bring-people .btn");
			
			that.bringPeopleSubmit(message, link, picture, function(response){
				that.bringPeopleCallback(btn, response);
			});
		});
					
	},
	
	bringPeoplePopup: function(){
		var popup_content = null
		// If live broadcast
		if(this.station_client.queue_manager.live_item){
			var title = this.station_client.queue_manager.live_item.content.youtube_title;
			var station = this.station_client.station.name;
			var people_listening = this.station_client.presence_manager.getCounter();
			
			// If user is station admin (focus on content)
			if(this.station_client.admin){
				popup_content = "♬ Live broadcasting on Phonoblaster. Come now and enjoy: " + title +"! ♬";
			}
			// If user is basic listener (focus on social)
			else{
				popup_content = "♬ Listening live to " + station + " on Phonoblaster w/ " + people_listening + " other people. ♬"
			}
		}
		else{
			popup_content = ""	
		}
		
		$("#popup-bring-people textarea").val(popup_content);
		
		// Display fancy box
		$.fancybox($("#popup-bring-people"), {
			topRatio: 0.4,
		});		
	},
	
	bringPeopleSubmit: function(message, link, picture, callback){
		var that = this;
		if(this.station_client.admin){
			var page_id = that.station_client.station.key_name;
			FACEBOOK.putPageWallPost(page_id, message, link, picture, callback)
		}
		else{
			FACEBOOK.putWallPost(message, link, picture, callback);
		}
		
		// Remove fancy box
		$.fancybox.close(true)
	},
	
	bringPeopleCallback: function(btn, response){
		var initial_content = btn.html();
	    
		if(response){
			btn.removeClass("primary").addClass("success").html("Post sent")
			setTimeout(function(){
				btn.removeClass("success").addClass("primary").html(initial_content);
			}, 2000)
		}
		else{
			btn.removeClass("primary").addClass("danger").html("Error. Try again.")
			setTimeout(function(){
				btn.removeClass("success").addClass("primary").html(initial_content);
			}, 2000)
		}
		
	},
	
}