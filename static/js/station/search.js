// ---------------------------------------------------------------------------
// SEARCH MANAGER
// ---------------------------------------------------------------------------

SearchManager.prototype = new ScrollTabManager();
SearchManager.prototype.constructor = SearchManager;

function SearchManager(client){
	ScrollTabManager.call(this, client);
	
	// Settings 
	this.url = "https://gdata.youtube.com/feeds/api/videos"
	this.offset = 1;
	this.data_type = "jsonp";
	
	// UI Settings
	this.name = "#search-tab";
	this.selector = this.name + " .tab-content";
	
	// Additional attribute
	this.type = "youtube"
	this.search_content = "";
	
	// Init methods
	this.switchListen();
	this.previewListen();
	this.scrollListen();
	this.processListen();
	this.inputListen();
}

SearchManager.prototype.switchListen = function(){
	var that = this
	
	$("a.search-icon").click(function(){
		
		var id = $(this).attr("id")
		if(id == "youtube-search"){
			that.type = "youtube";
			that.offset = 1;
			$(this).addClass("on");
			$(this).next().removeClass("on");
			$("input#search").attr("data-original-title","Search and add tracks from Youtube");
		}
		else{
			that.type = "soundcloud";
			that.offset = 0;
			$(this).addClass("on");
			$(this).prev().removeClass("on");
			$("input#search").attr("data-original-title","Search and add tracks from Soundcloud");
		}
		
		// Trigger search
		if(that.search_content.length > 1){
			that.get();
		}
		
		$(this).blur();
		return false;
		
	})
	
	
}

// Typing events in the input box
SearchManager.prototype.inputListen = function(){
	var that = this;
	
	// Clear the input if it contains default values
	$("input#search").focus(function(){	
		// Hide Twipsy
		$(this).twipsy("hide");
		
		var default_content = "Add a track to your selection"			
		var content = $(this).val()
		
		if(content == default_content || content == ""){
			//Clear the input text
			$(this).val("")
		}
		else{
			// Display the search tab that certainly contains results
			$("#search-overlay").show();
			$("#search-tab").show();
		}
		
		// If user not authenticated, display popup
		if(!that.client.listener){
			FACEBOOK.login();
			$(this).blur();
		}
	})
	
	// Trigger get each time something is typed
	$("input#search").keyup(function(){
		// Hide Twipsy
		$(this).twipsy("hide");
		
		if(that.type == "youtube"){
			that.offset = 1;
		}
		else{
			that.offset = 0;
		}
		
		that.scrolling_on = true;
		that.search_content = $(this).val()
		
		// Only trigger searches that have more than 1 character
		if(that.search_content.length > 1){
			$("#search-overlay").show();
			$("#search-tab").show();
			that.get();
		}
	})
	
	// Remove the search tab if click on overlay
	$("#search-overlay").click(function(){
		$("#search-overlay").hide()
		$("#search-tab").hide()	
		$("input#search").blur();
	})
	
}

// Overwrites the get data method
SearchManager.prototype.getData = function(){
	if(this.type == "youtube"){
		var data = {
			"q": this.search_content,
			"start-index": this.offset,
			"max-results": 20,
			"format": 5,
			"v": 2,
			"alt": "jsonc",
		}
	}
	else{
		var data = {
			"q" : this.search_content,
			"offset": this.offset,
			"limit": 50,
			"filter": "streamable",
			"order": "hotness",
		}
	}
		
	return data
}

// Overwrites the scrollListen method because Youtube search makes it specific
SearchManager.prototype.scrollListen = function(){
	var that = this;
	
	// Infinite scrolling events handler
	$(that.name).scroll(function(){	
		var items = $(this).find(".tab-content");
		var height = items.height();
		var scroll_height = $(this).scrollTop();
		var height_left = height - scroll_height;
		
		if(height_left < 400 && !that.load && that.scrolling_on){
			if(that.type == "youtube"){
				that.offset += 20;
			}
			else{
				that.offset += 50;
			}
			
			that.load = true;
			that.UIShowLoader();
			that.get();
		}
	})
}

// Overwrites the GET method
SearchManager.prototype.get = function(){
	var that = this;
	var data = this.getData()
		
	if(this.type == "youtube"){
		// Here it's specific to Youtube
		$.ajax({
			url: that.url,
			dataType: that.data_type,
			timeout: 60000,
			data: data,
			error: function(xhr, status, error) {
				PHB.log('An error occurred: ' + error + '\nPlease retry.');
			},
			success: function(json){
				var items = []
				if(json.data.items){
					items = json.data.items
				}
				
				that.searchCallback(items)
			},
		})
	}
	else{
		// Here it's specific to Soundcloud
		SC.get("/tracks", data,
		function(items){
			filtered_items = []
			
			// Filter results with artwork
			$.each(items, function(i, item){
				if(item.artwork_url){
					filtered_items.push(item);
				}
			})
			
			that.searchCallback(filtered_items);
		})
	}
}

SearchManager.prototype.searchCallback = function(items){
	if(items.length > 0){
		// First GET
		if(!this.load){
			// Empty the tab items zone before displaying everything
			var that = this
			this.empty(function(){
				that.getCallback(items); 
			})
		}
		// Scrolling GET
		else{
			this.getCallback(items); 
			this.emptyScrolling();
		}	
	}
	else{
		this.removeScrolling();
	}
}

// Specific to search
SearchManager.prototype.serverToLocalItem = function(raw_item){
	if(this.type == "youtube"){
		var new_track = {
			"youtube_id": raw_item.id, // Here it's specific to Youtube
			"youtube_title": raw_item.title, // Here it's specific to Youtube
			"youtube_duration": raw_item.duration, // Here it's specific to Youtube
			"track_id": null,
			"track_created": null,
			"track_submitter_key_name": this.client.host.key_name,
			"track_submitter_name": this.client.host.name,
			"track_submitter_url": "/" + this.client.host.shortname,
		}

		var item = {
			id: new_track.youtube_id,
			created: null,
			content: new_track,
		}
	}
	else{
		var new_track = {
			"soundcloud_id": raw_item.id, // Here it's specific to Soundcloud
			"soundcloud_title": raw_item.title, // Here it's specific to Soundcloud
			"soundcloud_duration": Math.round(parseInt(raw_item.duration)/1000), // Here it's specific to Soundcloud
			"soundcloud_thumbnail": raw_item.artwork_url, // Herer it's specific to Soundcloud
			"track_id": null,
			"track_created": null,
			"track_submitter_key_name": this.client.host.key_name,
			"track_submitter_name": this.client.host.name,
			"track_submitter_url": "/" + this.client.host.shortname,
		}

		var item = {
			id: new_track.soundcloud_id,
			created: null,
			content: new_track,
		}
	}
	
	return item
}

SearchManager.prototype.UIBuild = function(item){
	// Youtube track
	if(item.content.youtube_id){
		
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
	}
	// Soundcloud track
	else{
		
		var id = item.id;
		var content = item.content;

		var soundcloud_id = content.soundcloud_id;
		var soundcloud_title = content.soundcloud_title;
		var soundcloud_duration = PHB.convertDuration(content.soundcloud_duration)
		var soundcloud_thumbnail = content.soundcloud_thumbnail;

		var div = $("<div/>").addClass("item").attr("id",id)
		div.append(
			$("<div/>")
				.addClass("item-picture")
				.append($("<img/>").attr("src", soundcloud_thumbnail))
		)
		.append(
			$("<div/>")
				.addClass("item-title")
				.append($("<span/>").addClass("middle").html(soundcloud_title))
		)
		.append(
			$("<div/>")
				.addClass("item-subtitle")
				.append($("<div/>").addClass("item-duration").html(soundcloud_duration))
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
				)
		)
		
	}
	
	return div;
}





