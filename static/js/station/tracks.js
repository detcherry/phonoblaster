// ---------------------------------------------------------------------------
// TRACK MANAGER
// ---------------------------------------------------------------------------

TrackManager.prototype = new ScrollTabManager();
TrackManager.prototype.constructor = TrackManager;

function TrackManager(client){
	ScrollTabManager.call(this, client);
	this.init();
}

TrackManager.prototype.init = function(){
	// Settings
	this.url = "/api/tracks";
	this.data_type = "json";
	this.offset = null;
	
	// UI Settings
	this.name = "#tracks-tab";	
	this.selector = this.name + " .tab-content"
	
	// Init methods
	this.getListen();
	this.previewListen();
	this.processListen();
	this.scrollListen();
	this.deleteListen();

}

TrackManager.prototype.getData = function(){
	var shortname = this.client.host.shortname;
	var offset = this.offset;
	var data = {
		shortname: shortname,
		offset: offset,
	}
	return data
}

TrackManager.prototype.serverToLocalItem = function(content){
	content["track_submitter_key_name"] = this.client.host.key_name;
	content["track_submitter_name"] = this.client.host.name;
	content["track_submitter_url"] = "/" + this.client.host.shortname;
	
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
		$("<a/>")
			.attr("href","#")
			.addClass("item-cross")
			.attr("name", id)
			.html("X")
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
			// First we check if the track is not in the buffer
			var items = that.client.buffer_manager.items;
			var item_to_delete_is_in_buffer = false;

			for(var i = 0; i < items.length; i++){
				if (item_to_delete.id == items[i].content.track_id){
					item_to_delete_is_in_buffer = true;
					alert("You have to remove "+items[i].content.youtube_title+" from your buffer first.");
					break;
				}
			}

			if (!item_to_delete_is_in_buffer){
				if (confirm("Do you want to delete the track : "+item_to_delete.content.youtube_title+" ?")) {
					that.deleteSubmit(item_to_delete);
				}
			}
		}
		
		return false;
	})
}

TrackManager.prototype.deleteAjax = function(item, callback){
	var that = this;
	var delete_url = that.url +"/"+ item.id
	
	$.ajax({
		url: delete_url,
		type: "DELETE",
		dataType: that.data_type,
		timeout: 60000,
		error: function(xhr, status, error) {
			callback(false)
		},
		success: function(json){
			callback(json.response);
		},
	});
	
}