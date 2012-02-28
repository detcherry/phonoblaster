// ---------------------------------------------------------------------------
// RECOMMENDATION MANAGER
// ---------------------------------------------------------------------------

RecommendationManager.prototype = new ScrollTabManager();
RecommendationManager.prototype.constructor = RecommendationManager;

function RecommendationManager(station_client){
	ScrollTabManager.call(this, station_client);
	
	// Settings
	this.url = null;
	this.data_type = "json";
	
	// UI Settings
	this.selector = "#recommendations-zone";
	
	// Init Method
	this.dispatch();
	this.processListen();
	this.closeListen();
}

RecommendationManager.prototype.dispatch = function(){
	var number_of_broadcasts = this.station_client.broadcasts_counter.count;
	var that = this;
	
	if(number_of_broadcasts == 0){
		// Call recommendations API
		this.url = "/api/recommendations"
		$("#popup-recommendations h3 strong").html("Facebook")
	}
	else{		
		// Call tracks API 
		this.url = "/api/tracks"
		$("#popup-recommendations h3 strong").html("Phonoblaster")
	}
	
	this.get()
}

// Collect the data necessary to GET items from the server
RecommendationManager.prototype.getData = function(){
	var number_of_broadcasts = this.station_client.broadcasts_counter.count;
	
	if(number_of_broadcasts == 0){
		var data = {}
	}
	else{
		var shortname = this.station_client.station.shortname;
		var offset = PHB.now();
		var data = {
			shortname: shortname,
			offset: offset,
		}
	}
	

	return data
}

RecommendationManager.prototype.get = function(){	
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
				// Remove volume
				$("#media-volume").trigger("click");
								
				that.empty(function(){
					that.getCallback(json);
				})
				
				that.displayPopup();
			}
		},
	});	
}

RecommendationManager.prototype.displayPopup = function(){
	$.fancybox($("#popup-recommendations"), {
		topRatio: 0.4,
		modal: true,
	});
}

RecommendationManager.prototype.closeListen = function(){
	var that = this
	$("#popup-recommendations a.primary").click(function(){
		// Close popup
		$.fancybox.close(true);
		
		// Put volume back
		$("#media-volume").trigger("click");
		
		if(that.station_client.queue_manager.UILive()){
			// Popup to share station delayed after 1 sec
			setTimeout(function(){
				$("#top-right-share").trigger("click");
			}, 1000)
		}
	})
}

RecommendationManager.prototype.serverToLocalItem = function(content){	
	// Tracks fetched from Phonoblaster
	if(content.track_id){
		new_track = content;
		new_track["type"] = "track";
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

RecommendationManager.prototype.UIBuild = function(item){
	var id = item.id;
	var content = item.content;
	
	var youtube_id = content.youtube_id;
	var youtube_title = content.youtube_title;
	var youtube_duration = PHB.convertDuration(content.youtube_duration)
	var youtube_thumbnail = "https://i.ytimg.com/vi/" + youtube_id + "/default.jpg";
	
	var process_action = "Queue!"
	
	var div = $("<div/>").addClass("item").attr("id",id)
	div.append(
		$("<div/>")
			.addClass("item-picture")
			.append($("<img/>").attr("src", youtube_thumbnail))
	)
	.append(
		$("<div/>")
			.addClass("item-title")
			.append($("<span/>").addClass("middle").html(youtube_title))
	)
	.append(
		$("<div/>")
			.addClass("item-subtitle")
			.append($("<div/>").addClass("item-duration").html(youtube_duration))
			.append(
				$("<div/>")
					.addClass("item-process")
					.append($("<a/>").addClass("btn").attr("name",id).html(process_action))
			)
	)
				
	return div;
}
