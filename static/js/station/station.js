$(function(){
	STATION_CLIENT = new StationClient(USER, ADMIN, STATION)
})


function StationClient(user, admin, station){
	this.user = user;
	this.admin = admin;
	this.station = station;
	this.channel_id = null;
	this.time_delta = null;
	
	this.broadcasts_counter = new Counter("#broadcasts");
	this.views_counter = new Counter("#views");
	
	this.presence_manager = null;
	this.comment_manager = null;
	this.suggestion_manager = null;
	this.queue_manager = null;
	this.search_manager = null;
	this.favorite_manager = null;
	this.library_manager = null;
	this.status_manager = null;
	
	this.presence();
}

StationClient.prototype = {
	
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
				alert("Connection Lost. Will auto-reconnect when Online.");
			},
	        callback: function(message) {
	            that.dispatch(message);
	        },
	        connect: function(){
				// Fetch all the content: presences, comments, queue
				that.fetch();
	        }
		})
	},
	
	// Fetch presences, comments and queue after connection to pubnub + init all the tabs
	fetch: function(){
		this.presence_manager = new PresenceManager(this);
		
		// Once time has been initialized, fetch everything
		var that = this;
		PHB.time(function(){
			that.comment_manager = new CommentManager(that);
			that.queue_manager = new QueueManager(that);
			that.suggestion_manager = new SuggestionManager(that);
			that.search_manager = new SearchManager(that);
			
			that.favorite_manager = new FavoriteManager(that);				
			that.status_manager = new StatusManager(that);
		})
	},
	
	// Dispatch incoming messages according to their content
	dispatch: function(data){
		var message = JSON.parse(data);
		var event = message.event;
		var content = message.content;
		
		if(event == "new-presence"){
			PHB.log("new-presence");
			this.presence_manager.new(content);
		}
		if(event == "presence-removed"){
			PHB.log("presence-removed");
			this.presence_manager.remove(content);
		}
		if(event == "new-comment"){
			PHB.log("new-comment");
			this.comment_manager.new(content);
		}
		if(event == "new-broadcast"){
			PHB.log("new-broadcast");
			this.queue_manager.new(content);
		}
		if(event == "broadcast-removed"){
			PHB.log("broadcast-removed");
			this.queue_manager.remove(content);
		}
		if(event == "new-suggestion"){
			PHB.log("new-suggestion");
			this.suggestion_manager.new(content);
		}
	},
	
}

// ---------------------------------------------------------------------------
// BROADCASTS COUNTER
// ---------------------------------------------------------------------------


function Counter(selector){
	this.selector = selector;
	this.count = parseInt($(selector + " strong.number").html(), 10);
	this.display();
}

Counter.prototype = {
	
	increment: function(){
		this.count++;
		this.display()
	},
	
	decrement: function(){
		this.count--;
		this.display()
	},
	
	display: function(){
		var units = this.count % 1000;
		var thousands_plus = (this.count - units)/1000;
		var thousands = thousands_plus % 1000
		var millions_plus = (thousands_plus - thousands)/1000
		
		if(millions_plus >0){
			var total = millions_plus.toString()
			if(millions_plus < 10){
				total += "," + thousands.toString()
			}
			var to_display = total.slice(0,3) + "m"
		}
		else{
			if(thousands > 0){
				var total = thousands.toString()
				if(thousands < 10){
					total += "," + units.toString()					
				}
				var to_display = total.slice(0,3) + "k"
			}
			else{
				var to_display = units;
			}
		}
		
		$(this.selector + " strong.number")
			.css("visibility", "visible")
			.html(to_display);
	},
	
}
