// ---------------------------------------------------------------------------
// FAVORITE MANAGER
// ---------------------------------------------------------------------------

FavoriteManager.prototype = new ScrollTabManager();
FavoriteManager.prototype.constructor = FavoriteManager;

function FavoriteManager(station_client){
	ScrollTabManager.call(this, station_client);
	
	// Settings
	this.url = "api/favorites";
	this.data_type = "json";
	
	// UI Settings
	this.name = "#favorites-tab";	
	this.selector = this.name + " .tab-items"
	
	// Init methods
	this.postListen();
	this.deleteListen();

	// REMOVE THE COMMENTS BELOW ONCE FAVORITE TAB DISPLAYED
	// Methods only if tab displayed
	/*if(this.station_client.admin){
	//	this.getListen();
	//	this.previewListen();
	//	this.processListen();
	//	this.scrollListen();
	}
	*/
}

FavoriteManager.prototype.postListen = function(){
	var that = this;
	
	$("a.fav").live("click", function(){
		var new_item = that.station_client.queue_manager.live_item;
		
		// Change icon
		$(this).removeClass("fav").addClass("unfav");
		
		// POST new favorite to server
		that.post(new_item, function(response){
			that.postCallback(new_item, response)
		})
		
		// Post action to FACEBOOK
		that.postAction();
		
		$(this).blur();
		return false;
	})
}

FavoriteManager.prototype.postAction = function(){
	var track_url = PHB.site_url + "/track/" + this.station_client.queue_manager.live_item.content.track_id;
	var station_url = PHB.site_url + "/" + this.station_client.station.shortname;
	var obj = { "track": track_url };
	var extra = { "station": station_url };
	var expires_in = 0;
	var action = "favorite";	
	FACEBOOK.putAction(action, obj, extra, expires_in);
}


FavoriteManager.prototype.postCallback = function(new_item, response){
	if(!response){
		$("a.unfav").removeClass("unfav").addClass("fav");
		PHB.error("Favorite has not been stored.")
	}
}

FavoriteManager.prototype.deleteListen = function(){
	var that = this;
	
	$("a.unfav").live("click", function(){
		// Clone live item
		var item = $.extend(true, {}, that.station_client.queue_manager.live_item);
		
		// Change the Broadcast item into a Track item 
		item.id = item.content.track_id
		
		// Change icon
		$(this).removeClass("unfav").addClass("fav");
		
		that.delete(item, function(response){
			that.deleteCallback(item, response)
		})
		
		$(this).blur();
		return false;
	})
}

FavoriteManager.prototype.deleteCallback = function(item, response){
	if(!response){
		$("a.fav").removeClass("fav").addClass("unfav");
		PHB.error("Favorite has not been deleted.")
	}
}

FavoriteManager.prototype.UIBuild = function(item){
	var id = item.id;
	var content = item.content;

	var youtube_title = content.youtube_title;
	var youtube_duration = PHB.convertDuration(content.youtube_duration);
	var youtube_thumbnail = "http://i.ytimg.com/vi/" + content.youtube_id + "/default.jpg";
	
	var track_submitter_name = content.track_submitter_name;
	var track_submitter_url = content.track_submitter_url;
	var track_submitter_picture = "https://graph.facebook.com/" + content.track_submitter_key_name + "/picture?type=square";	
	var preview = "http://www.youtube.com/embed/" + content.youtube_id + "?autoplay=1"
	
	var div = $("<div/>").addClass("wrapper-item").attr("id", id)
	
	div.append(
		$("<img/>")
			.addClass("submitter")
			.attr("src", track_submitter_picture)
	)
	.append(
		$("<div/>")
			.addClass("content")
			.append(
				$("<p/>")
					.append(
						$("<a/>")
							.attr("href", track_submitter_url)
							.html(track_submitter_name)
					)
			)
	)
	.append(
		$("<div/>")
			.addClass("item")
			.append(
				$("<span/>")
					.addClass("square")
					.append(
						$("<img/>").attr("src", youtube_thumbnail)
					)
			)
			.append(
				$("<div/>")
					.addClass("title")
					.append(
						$("<span/>")
							.addClass("middle")
							.html(youtube_title))
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
									.attr("name", id)
									.html("Queue")
							)
							.append(
								$("<a/>")
									.addClass("preview")
									.addClass("fancybox.iframe")
									.attr("href", preview)
							)
					)
			)
	)
	
	return div;
	
}


