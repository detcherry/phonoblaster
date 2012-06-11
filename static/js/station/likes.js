// ---------------------------------------------------------------------------
// LIKES MANAGER
// ---------------------------------------------------------------------------

LikeManager.prototype = new ScrollTabManager();
LikeManager.prototype.constructor = LikeManager;

function LikeManager(client){
	ScrollTabManager.call(this, client);
	this.init();
}

LikeManager.prototype.init = function(){
	// Settings
	this.url = "/api/likes"
	this.data_type = "json"
	this.offset = null;
	
	// UI Settings
	this.name = "#likes-tab";
	this.selector = this.name + " .tab-content";
	
	// Init methods
	this.getListen();
	this.previewListen();
	this.processListen();
	this.scrollListen();
}

LikeManager.prototype.getData = function(){
	var shortname = this.client.host.shortname;
	var offset = this.offset;
	var data = {
		shortname: shortname,
		offset: offset,
	}
	return data
}

LikeManager.prototype.UIBuild = function(item){
	var id = item.id;
	var content = item.content;
	var created = PHB.convert(item.created);
		
	var track_submitter_url = content.track_submitter_url;
	var track_submitter_name = content.track_submitter_name;
	var track_submitter_picture = "https://graph.facebook.com/" + content.track_submitter_key_name + "/picture?type=square";
	
	var youtube_title = content.youtube_title;
	var youtube_duration = PHB.convertDuration(content.youtube_duration);
	var youtube_thumbnail = "https://i.ytimg.com/vi/" + content.youtube_id + "/default.jpg";
	var preview = "https://www.youtube.com/embed/" + content.youtube_id + "?autoplay=1"
	
	var div = $("<div/>").addClass("item-wrapper").attr("id", id)
	
	div.append(
		$("<div/>")
			.addClass("item-wrapper-submitter")
			.append($("<img/>").attr("src", track_submitter_picture))
	)
	.append(
		$("<div/>")
			.addClass("item-wrapper-content")
			.append($("<p/>").append($("<a/>").attr("href", track_submitter_url).html(track_submitter_name)))
			.append(
				$("<div/>")
					.addClass("item")
					.append(
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
									.append(
										$("<a/>")
											.addClass("btn")
											.attr("name", id)
											.html("Add")
											.addClass("tuto")
											.attr("data-original-title", "Add this track to your selection")
									)
									.append(
										$("<a/>")
											.addClass("preview")
											.addClass("fancybox.iframe")
											.attr("href", preview)
											.addClass("tuto")
											.attr("data-original-title", "Preview this track")
									)
							)
					)
			)
	)
	
	return div;
}

