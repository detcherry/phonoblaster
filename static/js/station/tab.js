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
	this.fetch_offset = null;
	this.fetch_datatype = null;	
	this.load = false;
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
		var that = this;
		
		var tab_selector = this.name;
		// Infinite scrolling events handler
		$(tab_selector).scroll(function(){	
			var items = $(this).find(".tab-items")
			var height = items.height();
			var scroll_height = $(this).scrollTop();
			var height_left = height - scroll_height;
			
			if(height_left < 400 && !that.load && that.fetch_offset < that.limit_fetch_offset){
				that.fetch_offset = that.tracklist.length + 1;
				that.load = true;
				that.showLoader();
				that.fetch(true);
			}
		})	
		
		var preview_selector = this.name + " a.preview"
		// Preview events handler
		$(preview_selector).fancybox();
	},
	
	// Build the div for the track
	UIBuild: function(new_track, callback){
		var video_url = "http://www.youtube.com/embed/" + new_track.youtube_id + "?autoplay=1"
		
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
								.append($("<a/>").addClass("preview").addClass("fancybox.iframe").attr("href",video_url))
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
	
	// Append a loader image at the bottom of the tab
	appendLoader: function(){
		var jquery_selector = this.name + " .tab-items";
		$(jquery_selector).append($("<div/>").addClass("loader"));
	},
	
	// Show the loader gif because user is scrolling down
	showLoader: function(){
		var jquery_selector = this.name + " .tab-items .loader";
		$(jquery_selector).show();
	},
	
	removeLoader: function(){
		var jquery_selector = this.name + " .tab-items .loader";
		$(jquery_selector).remove();
	},
	
	// Add to the queue or the suggestions queue
	submit: function(track){
		
	},
	
	empty: function(callback){
		this.tracklist = [];
		
		var jquery_selector = this.name + " .tab-items"
		$(jquery_selector).empty();
		callback();
	},
}
