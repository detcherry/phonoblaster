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
	var that = this;
	// Call Facebook API to know which tracks the user has posted on his wall
	FACEBOOK.retrieveWallLinks(function(items){
		that.filterFacebook(items);
	})
}

RecommendationManager.prototype.filterFacebook = function(items){
	var youtube_ids = []
	var soundcloud_urls = []
	
	$.each(items, function(i, item){		
		var re = RegExp("http://www.youtube.com/watch\\?v=([\\w_-]+)","g")
		var m = re.exec(item.link)
		if(m!= null){
			youtube_ids.push(m[1])
		}
		
		var re2 = RegExp("http://soundcloud.com/(.*)","g")
		var m2 = re2.test(item.link)
		if(m2){
			soundcloud_urls.push(item.link)
		}
	})
		
	var that = this;
	// Get info from Soundcloud
	this.filterSoundcloud(soundcloud_urls, function(soundcloud_tracks){
				
		// Get info from Youtube
		that.filterYoutube(youtube_ids, function(youtube_tracks){
			
			var tracks = soundcloud_tracks.concat(youtube_tracks);
			if(tracks.length > 0){
				
				// Remove volume
				$("#media-volume a").trigger("click");

				that.empty(function(){
					that.getCallback(tracks);
				})

				that.displayPopup();
			}
		})
	})
}

RecommendationManager.prototype.filterSoundcloud = function(soundcloud_urls, callback){
	
	var soundcloud_tracks = [];
	if(soundcloud_urls.length >0){
		// TODO: Resolve Soundcloud urls when it's possible to do it in one GET with their API
	
		callback(soundcloud_tracks)
	}
	else{
		callback(soundcloud_tracks)
	}
	
}

//RecommendationManager.prototype.filterYoutube = function(youtube_ids){
RecommendationManager.prototype.filterYoutube = function(youtube_ids, callback){
	
	var youtube_tracks = []
	
	if(youtube_ids.length > 0){
		$.ajax({
			url: "/api/recommendations",
			dataType: "json",
			timeout: 60000,
			data: {
				"youtube_ids": youtube_ids.join(","),
			},
			error: function(xhr, status, error){
				PHB.log('An error occurred: ' + error + '\nPlease retry.');
			},
			success: function(json){
				youtube_tracks = json;
				callback(youtube_tracks);
			}
		})
	}
	else{
		callback(youtube_tracks)
	}

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
		$("#media-volume a").trigger("click");
	})
}

RecommendationManager.prototype.serverToLocalItem = function(content){	

	// Tracks fetched from Facebook + Youtube
	new_track = {
		"type": "youtube",
		"id": content.id, 
		"title": content.title, 
		"duration": content.duration,
		"thumbnail": "https://i.ytimg.com/vi/" + content.id + "/default.jpg",
		"track_id": null,
		"track_created": null,
		"track_submitter_key_name": this.client.host.key_name,
		"track_submitter_name": this.client.host.name,
		"track_submitter_url": "/" + this.client.host.shortname,
	};
	
	var item = {
		id: new_track.id,
		created: new_track.created,
		content: new_track,
	}
	
	return item;	
}

RecommendationManager.prototype.UIBuild = function(item){
	var id = item.id;
	var content = item.content;
	
	var type = content.type;
	var id = content.id;
	var title = content.title;
	var duration = PHB.convertDuration(content.duration)
	var thumbnail = content.thumbnail;
		
	var div = $("<div/>").addClass("item").attr("id",id)
	div.append(
		$("<div/>")
			.addClass("item-picture")
			.append($("<img/>").attr("src", thumbnail).addClass(type))
	)
	.append(
		$("<div/>")
			.addClass("item-title")
			.append($("<span/>").addClass("middle").html(title))
	)
	.append(
		$("<div/>")
			.addClass("item-subtitle")
			.append($("<div/>").addClass("item-duration").html(duration))
			.append(
				$("<div/>")
					.addClass("item-process")
					.append($("<a/>").addClass("btn").attr("name",id).html("Add"))
			)
	)
				
	return div;
}
