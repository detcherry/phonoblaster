// ---------------------------------------------------------------------------
// BROADCAST MANAGER
// ---------------------------------------------------------------------------

BroadcastManager.prototype = new ScrollTabManager();
BroadcastManager.prototype.constructor = BroadcastManager;

function BroadcastManager(station_client){
	ScrollTabManager.call(this, station_client);
	
	// Settings
	this.url = "/api/broadcasts"
	this.data_type = "json"
	this.offset = PHB.now()
	
	// UI Settings
	this.name = "#broadcasts-tab";
	this.selector = this.name + " .tab-items";
	
	// Additional attributes
	this.live_item = null;
	this.youtube_manager = new EmbeddedYoutubeManager(this);
	
	this.get();
	this.scrollListen();
	this.liveListen();
}

// ----------------------- GET ---------------------------

BroadcastManager.prototype.getData = function(){
	var shortname = this.station_client.station.shortname;
	var offset = this.offset;
	var data = {
		shortname: shortname,
		offset: offset,
	}
	return data
}

BroadcastManager.prototype.noData = function(){
	// If no track is currently being played
	if(!this.live_item){
		// UI modifications
		$("#player-wrapper").empty();
		$("#player-wrapper").append($("<div/>").attr("id","no-live").html("No past broadcast."));
	}
}

BroadcastManager.prototype.addToItems = function(new_item, callback){
	var initialization = false;
	if(this.items.length == 0){
		initialization = true
	}
	
	// Add it to the list + DOM
	this.items.push(new_item);
	callback(null);
	
	// Put the video live it's the first item
	if(initialization){
		this.live(new_item);
	}
}

BroadcastManager.prototype.serverToLocalItem = function(content){
	var item = {
		id: content.key_name,
		created: content.created,
		content: content,
	}
	return item;
}

BroadcastManager.prototype.UIBuild = function(item){
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
	
	var mention = null;
	if(type == "suggestion"){
		mention = "Suggested by"
	}
	if(type == "favorite"){
		mention = "Rebroadcast of"
	}
	
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
	)
	
	if(mention){
		var subtitle = div.find(".subtitle");
		subtitle.append(
				$("<div/>")
				.addClass("submitter")
				.append(
					$("<img/>")
						.attr("src", track_submitter_picture)
						.addClass("station")
						.addClass("tuto")
						.attr("data-original-title", track_submitter_name)
				)
				.append(
					$("<span/>")
						.html(mention)
				)
		)

	}
	
	return div
}


// ---------------------- LIVE ---------------------------

BroadcastManager.prototype.live = function(new_item){		
	this.live_item = new_item;
	
	var id = this.live_item.id;
	var content = this.live_item.content;
	var expired_at = parseInt(content.expired,10);
	var duration = parseInt(content.youtube_duration,10);
	var youtube_id = content.youtube_id;

	// Launches the video
	this.youtube_manager.init(youtube_id);

	// Display the live broadcast in the UI
	this.UILiveSet(this.live_item);
	
	// Set as active in the right column
	this.UIActive(id)
	
	// No Post action to FACEBOOK yet
}

BroadcastManager.prototype.nextVideo = function(time_out){
	
	// Find the next item
	for(var i=0, c=this.items.length; i<c; i++){
		var item = this.items[i]
		if(item.id == this.live_item.id){
			// If item after live item, take it as the next item
			if(this.items[i+1]){
				var next_item = this.items[i+1]
				
				if(!this.items[i+2] && this.scrolling_on){
					
					// Fake a scrolling event
					var last_item = this.items[that.items.length -1];
					this.offset = last_item.created;
					this.load = true;
					this.get();
				}
				
			}
			// Otherwise, take the first item
			else{
				var next_item = this.items[0]
			}

			break;
		}
	}
	
	this.live(next_item);
}

BroadcastManager.prototype.liveListen = function(){
	var that = this;
	
	$("#broadcasts-tab div.item").live("click", function(){
		
		var id = $(this).attr("id");
		
		// Find the next item
		for(var i=0, c=that.items.length; i<c; i++){
			var item = that.items[i]
			if(item.id == id){
				var next_item = item;
				break;
			}
		}
		
		that.live(next_item);
	})
}

// ----------------------------- UI --------------------------------

// Set the live item in the UI
BroadcastManager.prototype.UILiveSet = function(item){
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
	$("#video-details span.clip").append($("<img/>").attr("src", youtube_thumbnail));
	
	// Display the title
	$("#video-details span.middle").html(youtube_title);
	
	var mention = null;
	if(type == "suggestion"){
		mention = "Suggested by"
	}
	if(type == "favorite"){
		mention = "Rebroadcast of"
	}
	
	if(mention){
		// Display the submitter
		$("#video-details .submitter")
			.append(
				$("<img/>")
					.attr("src", track_submitter_picture)
					.addClass("tuto") // Twipsy
					.attr("data-original-title", track_submitter_name)
			)
			.append($("<span/>").html(mention))
	}
	
	// Display the favorite icon
	if(content.track_id && this.station_client.user){
		$("#favorite-track").append($("<a/>").attr("href", "#").addClass("fav"))
	}
}

BroadcastManager.prototype.UILiveRemove = function(){
	// Remove image
	$("#video-details span.clip").empty();
	
	// Remove title
	$("#video-details span.middle").html("No track is being played");
	
	// Remove favorite icon
	$("#favorite-track").empty();
	
	// Remove the submitter
	$("#video-details .submitter").empty();
}

BroadcastManager.prototype.UIActive = function(id){
	$("#broadcasts-tab .item").removeClass("active");
	
	var re = RegExp("[.]","g");
	var selector = "#" + id.replace(re, "\\.");
	$(selector).addClass("active");
}

