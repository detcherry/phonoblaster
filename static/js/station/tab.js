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
	
	// Fetch extended tracks from the fetch address and the offset
	fetch: function(){
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
				if(that.fetch_offset == that.default_offset){
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
		
	},
	
	fetchCallback: function(items){
		var that = this;
		if(items){
			$.each(items, function(i) {
				var item = items[i];
				var new_track = {
					"youtube_id": item.id,
					"youtube_title": item.title,
					"youtube_thumbnail": item.thumbnail.sqDefault,
					"youtube_duration": item.duration,
					"created": item.created,
					"submitter_key_name": item.submitter_key_name,
					"submitter_name": item.submitter_name,
					"submitter_url": item.submitter_url,
					"admin": item.admin,
				}
				
				that.tracklist.push(new_track);
				that.UIAppend(new_track);
			});				
		}
		
		this.offset += 20;
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
