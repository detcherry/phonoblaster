// ---------------------------------------------------------------------------
// FAVORITE MANAGER
// ---------------------------------------------------------------------------

FavoriteManager.prototype = new ScrollPlayTabManager();
FavoriteManager.prototype.constructor = FavoriteManager;

function FavoriteManager(station_client){
	ScrollPlayTabManager.call(this, station_client);
	this.init();
}

FavoriteManager.prototype.init = function(){
	// Settings
	this.url = "/api/favorites"
	this.data_type = "json"
	this.offset = PHB.now()
	
	// UI Settings
	this.name = "#favorites-tab";
	this.selector = this.name + " .tab-items";
	
	// Additional attributes
	this.live_item = null;
	this.youtube_manager = new EmbeddedYoutubeManager(this, 640, 360);
	this.no_data_text = "No Favorite."
	
	this.get();
	this.scrollListen();
	this.liveListen();
}

// ----------------------- GET ---------------------------

FavoriteManager.prototype.getData = function(){
	var key_name = this.station_client.profile.key_name;
	var offset = this.offset;
	var data = {
		key_name: key_name,
		offset: offset,
	}
	return data
}

FavoriteManager.prototype.UIBuild = function(item){	
	var id = item.id;
	var content = item.content;

	var type = content.type;
	var youtube_id = content.youtube_id;
	var youtube_title = content.youtube_title;
	var youtube_duration = PHB.convertDuration(content.youtube_duration)
	var youtube_thumbnail = "http://i.ytimg.com/vi/" + youtube_id + "/default.jpg";
	var preview = "http://www.youtube.com/embed/" + youtube_id + "?autoplay=1"
	
	var track_submitter_name = content.track_submitter_name;
	var track_submitter_url = content.track_submitter_url;
	var track_submitter_picture = "https://graph.facebook.com/" + content.track_submitter_key_name + "/picture?type=square";	
	
	var mention = "Favorited from"
	
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
	
	div.append(
		$("<div/>")
			.addClass("item-subtitle")
			.append($("<div/>").addClass("item-duration").html(youtube_duration))
	)
	
	if(mention){
		var subtitle = div.find(".item-subtitle")
		subtitle.append(
			$("<div/>")
				.addClass("item-submitter")
				.append(
					$("<img/>")
						.attr("src", track_submitter_picture)
						.addClass("tuto")
						.attr("data-original-title", track_submitter_name)
				)
				.append($("<span/>").html(mention))
		)
	}
		
	return div
}

// ----------------------------- UI --------------------------------

// Set the live item in the UI
FavoriteManager.prototype.UILiveSet = function(item){
	this.UILiveRemove();
	
	var id = item.id;
	var content = item.content;
	var type = content.type;
	
	var youtube_title = content.youtube_title;
	var youtube_thumbnail = "http://i.ytimg.com/vi/" + content.youtube_id + "/default.jpg";
	
	var track_submitter_name = content.track_submitter_name;
	var track_submitter_url = content.track_submitter_url;
	var track_submitter_picture = "https://graph.facebook.com/" + content.track_submitter_key_name + "/picture?type=square";
	
	// Display the image
	$("#media-picture").append($("<img/>").attr("src", youtube_thumbnail));
	
	// Display the title
	$("#media-title span.middle").html(youtube_title);
	
	// Display the submitter
	var mention = "Favorited from"
	$("#media-submitter").append(
		$("<img/>")
			.attr("src", track_submitter_picture)
			.addClass("tuto") // Twipsy
			.attr("data-original-title", track_submitter_name)
	)
	.append($("<span/>").html(mention))
	
	// Display the favorite icon
	if(content.track_id){
		$("#media-details-right").append(
			$("<a/>")
				.attr("href", "#")
				.addClass("fav")
				.addClass("tuto") // Twipsy
				.attr("data-original-title", "Favorite this track") // Twipsy
		)
	}
}

