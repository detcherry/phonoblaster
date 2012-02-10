// ---------------------------------------------------------------------------
// RECOMMANDATION MANAGER
// ---------------------------------------------------------------------------

RecommandationManager.prototype = new ScrollTabManager();
RecommandationManager.prototype.constructor = RecommandationManager;

function RecommandationManager(station_client){
	ScrollTabManager.call(this, station_client);
	
	// Settings
	this.url = "api/tracks"
	this.data_type = "json"
	
	// UI Settings
	this.selector = "#recommandations-zone"
	
	// Init Method
	this.dispatch();
	this.processListen();
	this.closeListen();
}

RecommandationManager.prototype.dispatch = function(){
	var number_of_broadcasts = this.station_client.broadcasts_counter.count;
	if(number_of_broadcasts == 0){		
		// Call Facebook API to know which tracks the user has posted on his wall
		var that = this;
		FACEBOOK.retrieveWallLinks(function(items){
			that.filterFacebook(items);
		})
	}
	else{		
		// Call history API to get the latest tracks broacast in the station
		this.get();
	}
}

RecommandationManager.prototype.filterFacebook = function(items){
	var youtube_ids = []
	$.each(items, function(i, item){
		var re = RegExp("http://www.youtube.com/watch\\?v=([\\w_]+)","g")
		var m = re.exec(item.link)		
		if(m!= null){
			youtube_ids.push(m[1])
		}
	})
	
	this.filterYoutube(youtube_ids)
}

RecommandationManager.prototype.filterYoutube = function(youtube_ids){
	var url = "https://gdata.youtube.com/feeds/api/videos"
	var data_type = "jsonp";
	var q = youtube_ids.join("|");	
 	var data = {
		"q": q,
		"format": 5,
		"v": 2,
		"alt": "jsonc",
	}
	
	var that = this;
	$.ajax({
		url: url,
		dataType: data_type,
		timeout: 60000,
		data: data,
		error: function(xhr, status, error) {
			PHB.log('An error occurred: ' + error + '\nPlease retry.');
		},
		success: function(json){			
			var items = json.data.items; 
			if(items && items.length > 0){
				// Update recommandation popup and display it
				$("#popup-recommandation h3 strong").html("Facebook")
				that.displayPopup();
				
				// Remove volume
				$("#volume a").trigger("click");
				
				// Filter music videos only
				var music_videos = [];
				$.each(items, function(i, item){
					if(item.category == "Music"){
						music_videos.push(item)
					}
				})
				
				// Add and display music videos
				that.empty(function(){
					that.getCallback(music_videos);
				})
			}
		},
	})
	
}

// Collect the data necessary to GET items from the server
RecommandationManager.prototype.getData = function(){
	var shortname = this.station_client.station.shortname;
	var offset = PHB.now();
	var data = {
		shortname: shortname,
		offset: offset,
	}
	return data
}

RecommandationManager.prototype.get = function(){	
	var that = this;	
	var data = this.getData();
	
	// GET items
	$.ajax({
		url: that.url,
		type: "GET",
		dataType: that.data_type,
		timeout: 60000,
		data: data,
		error: function(xhr, status, error) {
			PHB.log('An error occurred: ' + error + '\nPlease retry.');
		},
		success: function(json){
			if(json.length > 0){
				// Update recommandation popup and display it
				$("#popup-recommandation h3 strong").html("Phonoblaster")
				that.displayPopup();
				
				// Remove volume
				$("#volume a").trigger("click");
				
				that.empty(function(){
					that.getCallback(json);
				})
			}
		},
	});	
}

RecommandationManager.prototype.displayPopup = function(){
	$.fancybox($("#popup-recommandation"), {
		topRatio: 0.4,
		modal: true,
	});
}

RecommandationManager.prototype.closeListen = function(){
	var that = this
	$("#popup-recommandation a.primary").click(function(){
		// Close popup
		$.fancybox.close(true);
		
		// Put volume back
		$("#volume a").trigger("click");
		
		if(that.station_client.queue_manager.UILive()){
			// Popup to bring people delayed after 1 sec
			setTimeout(function(){
				$("#bring-people .btn").trigger("click");
			}, 5000)
		}
	})
}

RecommandationManager.prototype.serverToLocalItem = function(content){	
	// Tracks fetched from Phonoblaster
	if(content.track_id){
		new_track = content;
		new_track["type"] = "track";
		new_track["track_admin"] = true;
		new_track["track_submitter_key_name"] = this.station_client.station.key_name;
		new_track["track_submitter_name"] = this.station_client.station.name;
		new_track["track_submitter_url"] = "/" + this.station_client.station.shortname;
	
		var item = {
			id: new_track.track_id,
			created: new_track.created,
			content: new_track,
		}
	}
	// Tracks fetched from Facebook + Youtube
	else{
		new_track = {
			"type": "track",
			"youtube_id": content.id, 
			"youtube_title": content.title, 
			"youtube_duration": content.duration,
			"track_id": null,
			"track_created": null,
			"track_admin": true,
			"track_submitter_key_name": this.station_client.station.key_name,
			"track_submitter_name": this.station_client.station.name,
			"track_submitter_url": "/" + this.station_client.station.shortname,
		};
		
		var item = {
			id: new_track.youtube_id,
			created: new_track.created,
			content: new_track,
		}
	}
	
	return item;	
}

RecommandationManager.prototype.UIBuild = function(item){
	var id = item.id;
	var content = item.content;
	
	var youtube_id = content.youtube_id;
	var youtube_title = content.youtube_title;
	var youtube_duration = PHB.convertDuration(content.youtube_duration)
	var youtube_thumbnail = "http://i.ytimg.com/vi/" + youtube_id + "/default.jpg";
	
	var process_action = "Queue!"
	
	var div = $("<div/>").addClass("item").attr("id",id)
	
	div.append(
		$("<span/>")
			.addClass("square")
			.append(
				$("<img/>")
					.attr("src", youtube_thumbnail)
			)
		)
		.append(
			$("<div/>")
				.addClass("title")
				.append(
					$("<span/>")
						.addClass("middle")
						.html(youtube_title)
				)
		)
		.append(
			$("<div/>")
				.addClass("subtitle")
				.append(
					$("<div/>")
						.addClass("duration")
						.html(youtube_duration)
				)
				.append(
					$("<div/>")
						.addClass("process-actions")
						.append(
							$("<a/>")
								.addClass("btn")
								.attr("name",id)
								.html(process_action)
						)
				)
		)
				
	return div;
}
