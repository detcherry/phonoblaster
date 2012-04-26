// ---------------------------------------------------------------------------
// TRACK MANAGER
// ---------------------------------------------------------------------------

TrackManager.prototype = new ScrollTabManager();
TrackManager.prototype.constructor = TrackManager;

function TrackManager(station_client){
	ScrollTabManager.call(this, station_client);
	this.init();
}

TrackManager.prototype.init = function(){
	// Settings
	this.url = "/api/tracks";
	this.data_type = "json";
	this.offset = null;
	
	// UI Settings
	this.name = "#tracks-tab";	
	this.selector = this.name + " .tab-items"
	
	// Init methods
	this.getListen();
	this.previewListen();
	this.processListen();
	this.scrollListen();
	this.deleteListen();
}

TrackManager.prototype.getData = function(){
	var shortname = this.station_client.station.shortname;
	var offset = this.offset;
	var data = {
		shortname: shortname,
		offset: offset,
	}
	return data
}

TrackManager.prototype.serverToLocalItem = function(content){
	content["type"] = "track";
	content["track_submitter_key_name"] = this.station_client.station.key_name;
	content["track_submitter_name"] = this.station_client.station.name;
	content["track_submitter_url"] = "/" + this.station_client.station.shortname;
	
	var item = {
		id: content.track_id,
		created: content.track_created,
		content: content,
	}
	
	return item;
}

TrackManager.prototype.UIBuild = function(item){
	var id = item.id;
	var content = item.content;

	var youtube_id = content.youtube_id;
	var youtube_title = content.youtube_title;
	var youtube_duration = PHB.convertDuration(content.youtube_duration)
	var youtube_thumbnail = "https://i.ytimg.com/vi/" + youtube_id + "/default.jpg";
	var preview = "https://www.youtube.com/embed/" + youtube_id + "?autoplay=1"
	
	var process_action = "Suggest"
	var process_info = "Suggest this track to the broadcaster"
	if(this.station_client.admin){
		process_action = "Queue"
		process_info = "Add this track to the queue"
	}
	
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

	if(this.station_client.admin){
		div.append(
			$("<a/>")
				.attr("href","#")
				.addClass("item-cross")
				.attr("name", id)
				.html("X")
		)
	}
	
	div.append(
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
							.html(process_action)
							.addClass("tuto")
							.attr("data-original-title", process_info)
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
					
	return div;
}

TrackManager.prototype.UIHide = function(id){
	var selector = "#" + id;
	$(selector).hide();
}

TrackManager.prototype.UIUnhide = function(id){
		var selector = "#" + id;
		$(selector).show();
}

TrackManager.prototype.deleteListen = function(){
		var that = this;
		var delete_selector = this.selector + " a.item-cross"
		
		$(delete_selector).live("click", function(){
			var item_id = $(this).attr("name");
			
			var item_to_delete = null;
			for(var i=0, c= that.items.length; i<c; i++){
				var item = that.items[i];
				if(item.id == item_id){
					item_to_delete = item;
					break;
				}
			}
			
			// We check if the item is in the list (sometimes it has not been received by PUBNUB yet...)
			if(item_to_delete){
				if (confirm("Do you want to delete the track : "+item_to_delete.content.youtube_title+" ?")) {
					console.log("Deleting track");
					that.deleteSubmit(item_to_delete);
				}
			}
			
			return false;
		})
	}