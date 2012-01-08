// ---------------------------------------------------------------------------
// SEARCH MANAGER
// ---------------------------------------------------------------------------

SearchManager.prototype = new TabManager();
SearchManager.prototype.constructor = SearchManager;

function SearchManager(station_client){
	TabManager.call(this, station_client);
		
	// Overwrites the parent offset attributes
	this.name = "#search-tab";
	this.url = "https://gdata.youtube.com/feeds/api/videos"
	this.offset = 1;
	this.datatype = "jsonp";
	this.limit_offset = 100;
	
	// Additional attribute
	this.search_content = null;
	
	// Additional methods
	this.standardListen();
	this.inputListen();
}

// Typing events in the input box
SearchManager.prototype.inputListen = function(){
	var that = this;
	
	// Clear the input if it contains default values
	$("input#search").focus(function(){	
		var default_content = "Suggest a track"	
		if(that.station_client.admin){
			var default_content = "Add a track"
		}
			
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
		if(!that.station_client.user){
			FACEBOOK.login();
			$(this).blur();
		}
	})
	
	// Trigger get each time something is typed
	$("input#search").keyup(function(){
		that.offset = 1;
		that.search_content = $(this).val()
		
		// Only trigger searches that have more than 1 character
		if(that.search_content.length > 1){
			$("#search-overlay").show();
			$("#search-tab").show();
			that.get(false);
		}
	})
	
	// Remove the search tab if click on overlay
	$("#search-overlay").click(function(){
		$("#search-overlay").hide()
		$("#search-tab").hide()	
		$("input#search").blur();
	})
	
}

// Specific to the search
SearchManager.prototype.empty = function(callback){
	this.tracklist = [];
	
	var jquery_selector = this.name + " .tab-items"
	$(jquery_selector).empty();
	
	callback();
}

// Overwrites the get data method
SearchManager.prototype.getData = function(){
	var that = this;
	get_data = {
		"q": that.search_content,
		"start-index": that.offset,
		"max-results": 20,
		"format": 5,
		"v": 2,
		"alt": "jsonc",
	}	
	return get_data
}

// Overwrites the scrollListen method because Youtube search makes it specific
SearchManager.prototype.scrollListen = function(){
	var that = this;
	
	// Infinite scrolling events handler
	var tab_selector = this.name;
	$(tab_selector).scroll(function(){	
		var items = $(this).find(".tab-items");
		var height = items.height();
		var scroll_height = $(this).scrollTop();
		var height_left = height - scroll_height;
		
		if(height_left < 400 && !that.load && that.offset < that.limit_offset){
			that.offset = that.tracklist.length + 1; // Here it's specific to Youtube
			that.load = true;
			that.showLoader();
			that.get(true);
		}
	})
}

// Overwrites the get method because Youtube search makes it specific
SearchManager.prototype.get = function(scrolling){
	var that = this;
	$.ajax({
		url: that.url,
		dataType: that.datatype,
		timeout: 60000,
		data: that.getData(),
		error: function(xhr, status, error) {
			PHB.log('An error occurred: ' + error + '\nPlease retry.');
		},
		success: function(json){
			var items = json.data.items; // Here it's specific to Youtube
			
			// First get
			if(!scrolling){
				// Empty the tab items zone before displaying everything
				that.empty(function(){
					that.getCallback(items); 
				})
			}
			// Scrolling get
			else{
				that.getCallback(items); 
			}			
		},
	})
}

// Overwrites the getCallback method because Youtube search makes it specific
SearchManager.prototype.getCallback = function(items){
	var that = this;
	if(items){
		$.each(items, function(i) {
			var item = items[i];
			var new_track = {
				"youtube_id": item.id, // Here it's specific to Youtube
				"youtube_title": item.title, // Here it's specific to Youtube
				"youtube_duration": item.duration, // Here it's specific to Youtube
				"track_id": null,
				"track_created": null,
			}
			
			// The condition below is specific to Youtube search because the track has not been posted to Phonoblaster yet
			if(that.station_client.admin){
				new_track["track_admin"] = true;
				new_track["track_submitter_key_name"] = that.station_client.station.key_name;
				new_track["track_submitter_name"] = that.station_client.station.name;
				new_track["track_submitter_url"] = "/" + that.station_client.station.shortname;
			}
			else{
				new_track["track_admin"] = false;
				new_track["track_submitter_key_name"] = that.station_client.user.key_name;
				new_track["track_submitter_name"] = that.station_client.user.name;
				new_track["track_submitter_url"] = "/user/" + that.station_client.user.key_name;
			}
			
			that.tracklist.push(new_track);
			that.UIAppend(new_track);
		});				
	}
	
	that.load = false;
	that.removeLoader();
	that.appendLoader();
}

// Overwrites the UIBuild method because Youtube search makes it specific
SearchManager.prototype.UIBuild = function(new_track, callback){
	var preview_url = "http://www.youtube.com/embed/" + new_track.youtube_id + "?autoplay=1"
	var track_thumbnail = "http://i.ytimg.com/vi/" + new_track.youtube_id + "/default.jpg"
	
	var default_action = "Suggest"
	if(this.station_client.admin){
		default_action = "Queue"
	}
	
	callback(
		$("<div/>")
			.addClass("track")
			.attr("id", new_track.youtube_id) // Here it's specific to Youtube (in other tabs, it's the new_track.track_id)
			.append($("<span/>").addClass("square").append($("<img/>").attr("src", track_thumbnail)))
			.append(
				$("<div/>")
					.addClass("title")
					.append($("<span/>").addClass("middle").html(new_track.youtube_title))
			)
			.append(
				$("<div/>")
					.addClass("subtitle")
					.append($("<div/>").addClass("duration").html(PHB.convertDuration(new_track.youtube_duration)))
					.append(
						$("<div/>")
							.addClass("process-actions")
							.append($("<a/>").addClass("btn").html(default_action))
							.append($("<a/>").addClass("preview").addClass("fancybox.iframe").attr("href",preview_url))
					)
			)
	)	
}

// Overwrites the processListen method because Youtube search makes it specific
SearchManager.prototype.processListen = function(){
	
	var that = this;
	
	var process_selector = this.name + " .process-actions a.btn"
	$(process_selector).live("click", function(){			
		var btn = $(this);
		var track_div = btn.parent().parent().parent();
		var track_id = track_div.attr("id");
		
		// Find the track information in the tab tracklist
		var track_to_submit = null;
		for(var i=0, c= that.tracklist.length; i<c; i++){
			var track = that.tracklist[i];
			if(track.youtube_id == track_id){ // Here it's specific to Youtube search
				to_submit = track;
				break;
			}
		}
		
		that.process(btn, to_submit);
		return false;			
	})
}





