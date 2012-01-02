// ---------------------------------------------------------------------------
// SEARCH MANAGER
// ---------------------------------------------------------------------------

SearchManager.prototype = new TabManager();
SearchManager.prototype.constructor = SearchManager;

function SearchManager(station_client){
	TabManager.call(this, station_client);
	
	// Overwrites the parent offset attributes
	this.name = "#search-tab";
	this.fetch_url = "https://gdata.youtube.com/feeds/api/videos"
	this.fetch_offset = 1;
	this.fetch_datatype = "jsonp";
	this.limit_fetch_offset = 100;
	
	// Additional attribute
	this.search_content = null
	
	// Additional methods
	this.standardListen();
	this.inputListen();
}

// Typing events in the input box
SearchManager.prototype.inputListen = function(){
	var that = this;
	
	// Clear the input if it contains default values
	$("input#search").focus(function(){
		if(that.station_client.admin){
			var default_content = "Add a track"
		}
		else{
			var default_content = "Suggest a track"
		}
		var content = $(this).val()
		
		if(content == default_content){
			//Clear the input text
			$(this).val("")
		}
		else{
			// Display the search tab that certainly contains results
			$("#search-overlay").show();
			$("#search-tab").show();
		}
	})
	
	// Trigger fetch each time something is typed
	$("input#search").keyup(function(){
		that.fetch_offset = 1;
		that.search_content = $(this).val()
		
		$("#search-overlay").show();
		$("#search-tab").show();
		
		that.fetch(false);	
	})
	
	// Remove the search tab if click on overlay
	$("#search-overlay").click(function(){
		$("#search-overlay").hide()
		$("#search-tab").hide()	
		$("input#search").blur();
	})
	
}

// Overwrites the fetch data method
SearchManager.prototype.getFetchData = function(){
	var that = this;
	fetch_data = {
		"q": that.search_content,
		"start-index": that.fetch_offset,
		"max-results": 20,
		"format": 5,
		"v": 2,
		"alt": "jsonc",
	}	
	return fetch_data
}

// Overwrites the fetch method because Youtube makes it really specific
SearchManager.prototype.fetch = function(scrolling){
	var that = this;
	$.ajax({
		url: that.fetch_url,
		dataType: that.fetch_datatype,
		timeout: 60000,
		data: that.getFetchData(),
		error: function(xhr, status, error) {
			PHB.log('An error occurred: ' + error + '\nPlease retry.');
		},
		success: function(json){
			// First fetch
			if(!scrolling){
				// Empty the tab items zone before displaying everything
				that.empty(function(){
					that.fetchCallback(json.data.items);
				})
			}
			// Scrolling fetch
			else{
				that.fetchCallback(json.data.items);
			}			
		},
	})
}

// Overwrites the fetchCallback method for the same reasons
SearchManager.prototype.fetchCallback = function(items){
	var that = this;
	if(items){
		$.each(items, function(i) {
			var item = items[i];
			var new_track = {
				"youtube_id": item.id,
				"youtube_title": item.title,
				"youtube_thumbnail": item.thumbnail.sqDefault,
				"youtube_duration": item.duration,
				"created": null,
				"submitter_key_name": null,
				"submitter_name": null,
				"submitter_url": null,
				"admin": null,
			}
			
			that.tracklist.push(new_track);
			that.UIAppend(new_track);
		});				
	}
	
	that.load = false;
	that.removeLoader();
	that.appendLoader();
}



