$(function(){
	STATION_CLIENT = new StationClient(USER, ADMIN, STATION)
})


function StationClient(user, admin, station){
	this.init(user, admin, station);
}

StationClient.prototype = {
	
	init: function(user, admin, station){
		this.user = user;
		this.admin = admin;
		this.station = station;
		this.channel_id = null;

		this.broadcasts_counter = new Counter("#broadcasts");
		this.views_counter = new Counter("#views");

		this.presence_manager = null;
		this.comment_manager = null;
		this.suggestion_manager = null;
		this.queue_manager = null;
		this.search_manager = null;
		this.tracks_manager = null;
		this.status_manager = null;
		this.viral_manager = null;

		this.favorite_sdk = null;

		this.presence();
	},

	// Add a new presence: request Client ID and Token from Google App Engine
	presence: function(){
		var that = this;
		
		$.ajax({
			url: "/api/presences",
			type: "POST",
			dataType: "json",
			timeout: 60000,
			data: {
				shortname: that.station.shortname,
			},
			error: function(xhr, status, error) {
				PHB.log('An error occurred: ' + error + '\nPlease retry.');
			},
			success: function(json){				
				// Store the presence channel id
				that.channel_id = json.channel_id;
				
				// Create a presence channel
				var channel = new goog.appengine.Channel(json.channel_token);
				
				// Open connection and hook callbacks
				var socket = channel.open();
				socket.onerror = window.location.reload;
				socket.onclose = window.location.reload;
				
				// Subscribe to the station channel
				var station_client = that;
				socket.onopen = function(){
					station_client.pubnub();
				}
				
				// We do not hook the following callback
				// - socket.onmessage
			},
		});
	},
	
	// Subscribe to the station channel with Pubnub
	pubnub: function(){
		var that = this;
		var pubnub_channel = PHB.version + "-" + this.station.shortname
		// Subscribe to the station channel with Pubnub
		PUBNUB.subscribe({
	        channel: pubnub_channel,      
	        error: function(){
				PHB.log("Connection Lost. Will auto-reconnect when Online.");
			},
	        callback: function(message) {
	            that.dispatch(message);
	        },
	        connect: function(){
				// Fetch all the content: presences, comments, suggestions, queue
				that.fetch();
	        }
		})
	},
	
	// Fetch presences, comments and queue after connection to pubnub + init all the tabs
	fetch: function(){
		this.presence_manager = new PresenceManager(this); // Fetching
		
		// Once time has been initialized, initialize everything else
		var that = this;
		var pubnub_channel = PHB.version + "-" + this.station.shortname
		
		PHB.time(function(){
			that.queue_manager = new QueueManager(that); // Fetching
			that.search_manager = new SearchManager(that); // No Fetching
			
			that.comment_manager = new CommentManager(that); // Pubnub Fetching
			that.suggestion_manager = new SuggestionManager(that); // Pubnub Fetching
			
			// Fetch latest comments and suggestions via PUBNUB
			PUBNUB.history({
					channel: pubnub_channel,
					limit: 100,
				},
				function(messages){
					$.each(messages, function(index, value){
						var message = JSON.parse(value);
						var entity = message.entity;
						var event = message.event;
						var content = message.content;
						
						if(entity == "comment"){
							// Event is "new"
							that.comment_manager.add(content);
						}
						
						if(entity == "suggestion"){
							// Event is "new"
							that.suggestion_manager.add(content);
						}
					})
				}
			)	
			
			that.tracks_manager = new TracksManager(that); // Lazy fetching
			that.status_manager = new StatusManager(that);
			that.viral_manager = new ViralManager(that);
			
			that.favorite_sdk = new FavoriteSDK(that.queue_manager)
			
		})
	},
	
	// Dispatch incoming messages according to their content	
	dispatch: function(data){
		var message = JSON.parse(data);
		var entity = message.entity;
		var event = message.event;
		var content = message.content;
		
		PHB.log(entity + " " + event)
		
		var manager = null;
		if(entity == "presence"){
			manager = this.presence_manager;
		}
		if(entity == "broadcast"){
			manager = this.queue_manager;
		}
		if(entity == "comment"){
			manager = this.comment_manager;
		}
		if(entity == "suggestion"){
			manager = this.suggestion_manager;
		}
		if(entity == "status"){
			manager = this.status_manager;
		}
		
		if(event == "new"){
			manager.new(content);
		}
		else{
			manager.remove(content);
		}
		
	},
	
}


