// ---------------------------------------------------------------------------
// LATEST MANAGER
// ---------------------------------------------------------------------------

LatestManager.prototype = new ScrollTabManager()
LatestManager.prototype.constructor = LatestManager;

function LatestManager(station_client){
	ScrollTabManager.call(this, station_client);
	
	// Settings
	this.url = "/api/broadcasts"
	this.data_type = "json"
	this.offset = PHB.now()
	
	// UI Settings
	this.name = "#latest-tab";
	this.selector = this.name + " .tab-items";
	
	this.get();
}

LatestManager.prototype.getData = function(){
	var shortname = this.station_client.station.shortname;
	var offset = this.offset;
	var data = {
		shortname: shortname,
		offset: offset,
	}

	return data	
}

LatestManager.prototype.UIBuild = function(item){
	var id = item.id;
	var content = item.content;

	var type = content.type;
	var youtube_id = content.youtube_id;
	var youtube_title = content.youtube_title;
	var youtube_duration = PHB.convertDuration(content.youtube_duration)
	var youtube_thumbnail = "https://i.ytimg.com/vi/" + youtube_id + "/default.jpg";
	var preview = "https://www.youtube.com/embed/" + youtube_id + "?autoplay=1"
	
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