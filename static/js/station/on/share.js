// ---------------------------------------------------------------------------
// SHARE MANAGER
// ---------------------------------------------------------------------------

function ShareManager(station_client){
	this.station_client = station_client;
	this.listen();
}

ShareManager.prototype = {
	
	listen: function(){
		var that = this;
		
		// Listen to events to bring people inside station (from broadcaster or listener)
		$("a#top-right-share").click(function(){
			// User must be logged in to share the station
			if(!that.station_client.user){
				FACEBOOK.login()
			}
			else{
				// Display popup
				that.sharePopup()
			}
			return false;
		});
		
		// Listen to submit events for bringing people inside station
		$("#popup-share form").submit(function(event){
			event.preventDefault();
			
			var message = $("#popup-share textarea").val();
			var link = PHB.site_url + "/" + that.station_client.station.shortname;
			var picture = PHB.site_url + "/" + that.station_client.station.shortname + "/picture";
			var btn = $("a#top-right-share");
			
			that.shareSubmit(message, link, picture, function(response){
				that.shareCallback(btn, response);
			});
		});
					
	},
	
	sharePopup: function(){
		var popup_content = null
		
		// If UI live broadcast
		if(this.station_client.queue_manager.UILive()){
			var title = $("#media-title span.middle").html();
			var station = this.station_client.station.name;
			var people_listening = this.station_client.session_manager.sessions_counter.count;
			
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
		
		$("#popup-share textarea").val(popup_content);
		
		// Display fancy box
		$.fancybox($("#popup-share"), {
			topRatio: 0.4,
		});		
	},
	
	shareSubmit: function(message, link, picture, callback){
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
	
	shareCallback: function(btn, response){
		var initial_content = btn.html();
	    
		if(response){
			btn.html("Post sent")
			setTimeout(function(){
				btn.html(initial_content);
			}, 2000)
		}
		else{
			btn.html("Error. Try again.")
			setTimeout(function(){
				btn.html(initial_content);
			}, 2000)
		}
		
	},
	
}