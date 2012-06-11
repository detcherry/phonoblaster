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
	this.search_content = null;
	
	// Init methods
	this.previewListen();
	this.scrollListen();
	this.processListen();
	this.inputListen();
}

// Typing events in the input box
SearchManager.prototype.inputListen = function(){
	var that = this;
	
	// Clear the input if it contains default values
	$("input#search").focus(function(){	
		// Hide Twipsy
		$(this).twipsy("hide");
		
		var default_content = "Suggest a track to the broadcaster"	
		if(that.client.admin){
			var default_content = "Add a track to your selection"
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
		if(!that.client.listener){
			FACEBOOK.login();
			$(this).blur();
		}
	})
	
	// Trigger get each time something is typed
	$("input#search").keyup(function(){
		// Hide Twipsy
		$(this).twipsy("hide");
		
		that.offset = 1;
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
	var that = this;
	var data = {
		"q": that.search_content,
		"start-index": that.offset,
		"max-results": 20,
		"format": 5,
		"v": 2,
		"alt": "jsonc",
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
			that.offset = that.items.length + 1; // Here it's specific to Youtube			
			that.load = true;
			that.UIShowLoader();
			that.get();
		}
	})
}

// Overwrites the get method because Youtube search makes it specific
SearchManager.prototype.get = function(scrolling){
	var that = this;
	var data = this.getData()
	
	$.ajax({
		url: that.url,
		dataType: that.data_type,
		timeout: 60000,
		data: data,
		error: function(xhr, status, error) {
			PHB.log('An error occurred: ' + error + '\nPlease retry.');
		},
		success: function(json){
			var items = json.data.items; // Here it's specific to Youtube
			
			// Content exists on the server
			if(items && items.length > 0){
				// First GET
				if(!that.load){
					// Empty the tab items zone before displaying everything
					that.empty(function(){
						that.getCallback(items); 
					})
				}
				// Scrolling GET
				else{
					that.getCallback(items); 
					that.emptyScrolling();
				}
			}
			else{
				that.removeScrolling();
			}
		},
	})
}

// Specific to Youtube
SearchManager.prototype.serverToLocalItem = function(raw_item){
	var new_track = {
		"type": "track",
		"youtube_id": raw_item.id, // Here it's specific to Youtube
		"youtube_title": raw_item.title, // Here it's specific to Youtube
		"youtube_duration": raw_item.duration, // Here it's specific to Youtube
		"track_id": null,
		"track_created": null,
	}
	
	// The condition below is specific to Youtube search because the track has not been posted to Phonoblaster yet
	if(this.client.admin){
		new_track["track_admin"] = true;
		new_track["track_submitter_key_name"] = this.client.host.key_name;
		new_track["track_submitter_name"] = this.client.host.name;
		new_track["track_submitter_url"] = "/" + this.client.host.shortname;
	}
	else{
		new_track["track_admin"] = false;
		new_track["track_submitter_key_name"] = this.client.listener.key_name;
		new_track["track_submitter_name"] = this.client.listener.name;
		new_track["track_submitter_url"] = "/user/" + this.client.listener.key_name;
	}
	
	var item = {
		id: new_track.youtube_id,
		created: null,
		content: new_track,
	}
	return item
}