// ---------------------------------------------------------------------------
// TAB MANAGER
// ---------------------------------------------------------------------------

// Parent class for tab classes (search, suggestions, favorites, library)
function TabManager(station_client){
	this.station_client = station_client;
	this.tracklist = [];
	this.name = null;
	
	// Fetch settings
	this.fetch_url = null;
	this.default_offset = null;
	this.fetch_offset = null;
	this.fetch_datatype = null;	
}

TabManager.prototype = {
	
	// Overwrite this function to format the data sent by fetch()
	getFetchData: function(){},
	
	// Parent fetch method for extended tracks 
	fetch: function(){
	},
	
	// Parent fetch callback once the extended tracks have been fetched from the server
	fetchCallback: function(tracks){
	},
	
	// Listen to "add", "preview", "suggest" or "more" events (standard events)
	standardListen: function(){
	},
	
	// Build the div for the track
	UIBuild: function(new_track, callback){
		callback(
			$("<div/>")
				.addClass("track")
				.append($("<span/>").addClass("square").append($("<img/>").attr("src", new_track.youtube_thumbnail)))
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
								.addClass("queue-actions")
								.append($("<a/>").addClass("btn").html("Queue"))
								.append($("<span/>").addClass("preview"))
						)
				)
		)
	},
	
	// Append a new track to the tab
	UIAppend: function(new_track){
		var that = this;
		this.UIBuild(new_track, function(new_track_jquery_object){
			var jquery_selector = that.name + " .tab-items";
			$(jquery_selector).append(new_track_jquery_object);
		})
	},
	
	// Add to the queue or the suggestions queue
	submit: function(track){
		
	},
	
	empty: function(callback){
		var jquery_selector = this.name + " .tab-items"
		$(jquery_selector).empty();
		callback();
	},
}
