$(function(){
	CLIENT = new Client(LISTENER, ADMIN, HOST)
})

function Client(listener, admin, host){
	this.init(listener, admin, host);
}

Client.prototype = {
	
	init: function(listener, admin, host){
		this.listener = listener;
		this.admin = admin;
		this.host = host;
		this.channel_id = null;

		this.session_manager = null;
		this.message_manager = null;
		this.suggestion_manager = null;
		this.buffer_manager = null;
		this.search_manager = null;
		this.track_manager = null;
		this.like_manager = null;
		this.share_manager = null;
		this.background_manager = null;

		this.connect();
	},

	// Add a new session: request client ID and token from Google App Engine
	connect: function(){
		var that = this;
		
		$.ajax({
			url: "/api/sessions",
			type: "POST",
			dataType: "json",
			timeout: 60000,
			data: {
				shortname: that.host.shortname,
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
				
				// Subscribe to the host channel
				var host_client = that;
				socket.onopen = function(){
					host_client.pubnub();
				}
				
				// We do not hook the following callback
				// - socket.onmessage
			},
		});
	},
	
	// Subscribe to the host channel with Pubnub
	pubnub: function(){
		var that = this;
		var pubnub_channel = PHB.version + "-" + this.host.shortname
		// Subscribe to the host channel with Pubnub
		PUBNUB.subscribe({
	        channel: pubnub_channel,      
	        error: function(){
				PHB.log("Connection Lost. Will auto-reconnect when Online.");
			},
	        callback: function(message) {
	            that.dispatch(message);
	        },
	        connect: function(){
				// Fetch all the content: sessions, comments, suggestions, queue
				that.fetch();
	        }
		})
	},
	
	// Fetch presences, comments and queue after connection to pubnub + init all the tabs
	fetch: function(){
		this.session_manager = new SessionManager(this); // Fetching
		
		// Once time has been initialized, initialize everything else
		var that = this;
		var pubnub_channel = PHB.version + "-" + this.host.shortname
		
		PHB.time(function(){
			that.buffer_manager = new BufferManager(that); // Fetching
			that.search_manager = new SearchManager(that); // No Fetching
			
			that.message_manager = new MessageManager(that); // Fetching
			that.suggestion_manager = new SuggestionManager(that); // Fetching	
			that.track_manager = new TrackManager(that); // Lazy fetching
			that.like_manager = new LikeManager(that); // Lazy fetching
			that.share_manager = new ShareManager(that);
			that.background_manager = new BackgroundManager(that);			
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
		if(entity == "session"){
			manager = this.session_manager;
		}
		if(entity == "buffer"){
			manager = this.buffer_manager;
		}
		if(entity == "message"){
			manager = this.message_manager;
		}
		if(entity == "suggestion"){
			manager = this.suggestion_manager;
		}
		if(entity == "background"){
			manager = this.background_manager;
		}
		
		if(event == "new"){
			manager.pushNew(content);
		}
		else{
			manager.pushRemove(content);
		}
		
	},
	
}


