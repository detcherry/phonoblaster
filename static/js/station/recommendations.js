// ---------------------------------------------------------------------------
// RECOMMENDATION MANAGER
// ---------------------------------------------------------------------------

RecommendationManager.prototype = new ScrollTabManager();
RecommendationManager.prototype.constructor = RecommendationManager;

function RecommendationManager(client){
	ScrollTabManager.call(this, client);
	
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
	$("#popup-recommendations h3 strong").html("Facebook")
	
	var that = this;
	// Call Facebook API to know which tracks the user has posted on his wall
	FACEBOOK.retrieveWallLinks(function(items){
		that.filterFacebook(items);
	})
}

RecommendationManager.prototype.filterFacebook = function(items){
	var youtube_ids = []
	
	$.each(items, function(i, item){
		var re = RegExp("http://www.youtube.com/watch\\?v=([\\w_]+)","g")
		var m = re.exec(item.link)
		if(m!= null){
			youtube_ids.push(m[1])
		}
	})
	
	if(youtube_ids.length > 0){
		this.filterYoutube(youtube_ids)
	}
}

RecommendationManager.prototype.filterYoutube = function(youtube_ids){
	var data = {
		"youtube_ids": youtube_ids.join(","),
	}
	var that = this;
	
	$.ajax({
		url: "/api/recommendations",
		dataType: "json",
		timeout: 60000,
		data: data,
		error: function(xhr, status, error){
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
		}
	})	
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
	})
}

RecommendationManager.prototype.serverToLocalItem = function(content){	

	// Tracks fetched from Facebook + Youtube
	new_track = {
		"type": "track",
		"youtube_id": content.id, 
		"youtube_title": content.title, 
		"youtube_duration": content.duration,
		"track_id": null,
		"track_created": null,
		"track_submitter_key_name": this.client.host.key_name,
		"track_submitter_name": this.client.host.name,
		"track_submitter_url": "/" + this.client.host.shortname,
	};
	
	var item = {
		id: new_track.youtube_id,
		created: new_track.created,
		content: new_track,
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
	
	var process_action = "Add"
	
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
