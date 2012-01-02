// ---------------------------------------------------------------------------
// SEARCH MANAGER
// ---------------------------------------------------------------------------

SearchManager.prototype = new TabManager();
SearchManager.prototype.constructor = SearchManager;

function SearchManager(station_client){
	TabManager.call(this, station_client);
	
	// Overwrite the parent offset attributes
	this.name = "#search-tab";
	this.fetch_url = "https://gdata.youtube.com/feeds/api/videos"
	this.default_offset = 1;
	this.fetch_offset = 1;
	this.fetch_datatype = "jsonp"
	
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
		
		that.fetch();	
	})
	
	// Remove the search tab if click on overlay
	$("#search-overlay").click(function(){
		$("#search-overlay").hide()
		$("#search-tab").hide()	
		$("input#search").blur();
	})
	
}

// Format the fetch data
SearchManager.prototype.getFetchData = function(){
	var that = this;
	return {
		"q": that.search_content,
		"category": "music",
		"start-index": that.fetch_offset,
		"max-results": 20,
		"format": 5,
		"v": 2,
		"alt": "jsonc",
	}
}


