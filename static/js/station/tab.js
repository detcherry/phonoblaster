// ---------------------------------------------------------------------------
// TAB MANAGER
// ---------------------------------------------------------------------------

// Parent class for tab classes (search, favorites, library)
function TabManager(station_client){
	this.station_client = station_client;
	this.tracklist = [];
	this.name = null;
	
	// Settings
	this.url = null;
	this.offset = null;
	this.limit_offset = null;
	this.datatype = null;	
	this.load = false;
}

TabManager.prototype = {
	
	// Parent getData method
	getData: function(){
	},
	
	// Parent get method for extended tracks 
	get: function(){
	},
	
	// Parent get callback once the extended tracks have been geted from the server
	getCallback: function(tracks){
	},
	
	// Listen to "queue", "remove", "preview", "suggest" or "more" events (standard events)
	standardListen: function(){
		var that = this;
		
		// Scrolling events listening
		this.scrollListen();
		
		// Preview events listening
		this.previewListen();
		
		// Queue/ Suggest events handler
		this.processListen();
	},
	
	// Scrolling events listening
	scrollListen: function(){
	},
	
	// Preview events listening
	previewListen: function(){
		var preview_selector = this.name + " a.preview"
		$(preview_selector).fancybox({
			beforeShow: function(){
				try{ytplayer.mute();}
				catch(e){PHB.log(e);}
			},
			afterClose: function(){
				if(VOLUME){
					try{ytplayer.unMute();}
					catch(e){PHB.log(e);}
				}
			},
		});
	},
	
	// Queue/suggest events listening
	processListen: function(){
	},
	
	// Dispatch if the user is admin (queue) or not (suggest)
	process: function(btn, to_submit){
		// If station admin it's a broadcast
		if(this.station_client.admin){
			var process_manager = this.station_client.queue_manager;
		}
		// Otherwise it's a suggestion
		else{
			var process_manager = this.station_client.suggestion_manager;
		}
		process_manager.postSubmit(btn, to_submit);
	},
	
	// Build the div for the track
	UIBuild: function(new_track, callback){
	},
	
	// Append a new track to the tab
	UIAppend: function(new_track){
		var tab_selector = this.name + " .tab-items";
		
		// Reset the tab in case it contained some init content
		var init_selector = tab_selector + " .init";
		$(init_selector).remove();
		
		var that = this;
		this.UIBuild(new_track, function(new_track_jquery_object){
			$(tab_selector).append(new_track_jquery_object);
		})
	},
	
	// Append a loader image at the bottom of the tab
	appendLoader: function(){
		var tab_selector = this.name + " .tab-items";
		$(tab_selector).append($("<div/>").addClass("loader"));
	},
	
	// Show the loader gif because user is scrolling down
	showLoader: function(){
		var loader_selector = this.name + " .tab-items .loader";
		$(loader_selector).show();
	},
	
	removeLoader: function(){
		var loader_selector = this.name + " .tab-items .loader";
		$(loader_selector).remove();
	},
}
