$(function(){
	
	$("#queue-tab a.btn").click(function(){
		FACEBOOK.loginAndRedirect();
		return false;
	})
	
})

// ---------------------------------------------------------------------------
// SPECIFIC OVERWRITING FUNCTIONS FOR IFRAME APP - "ON" MODE
// ---------------------------------------------------------------------------

// ----------------- QUEUE ------------------

// New constructor
QueueManager.prototype.init = function(station_client){
	RealtimeTabManager.call(this, station_client);
	
	// Settings
	this.url = "/api/queue"
	this.data_type = "json"
	
	// UI Settings
	this.name = "#queue-tab";
	this.selector = this.name + " .tab-items";
	
	// Additional attributes
	this.live_item = null;
	this.youtube_manager = new YoutubeManager();
	
	// Init Methods
	this.get();
}

// No recommandations displayed
QueueManager.prototype.noData = function(){
	// UI modifications
	$("#player-wrapper").empty();
	$("#player-wrapper").append($("<div/>").attr("id","no-live").html("No live track."));
}

// No recommandations or switch to off air mode displayed
QueueManager.prototype.nextVideo = function(time_out){
	var that = this;
	
	setTimeout(function(){			
		// Live is over
		that.liveOver();
		
		// Get next item and put it live
		var new_item = that.items.shift();
		if(new_item){
			that.live(new_item)
		}
		else{
			// Switch to off air mode popup
		}		
	}, time_out * 1000)
}

// No alert manager + no broadcast counter incremented
QueueManager.prototype.newEvent = function(){}

// No broadcast counter decremented + No UI room update
QueueManager.prototype.removeEvent = function(){}

// Useless functions
QueueManager.prototype.updateRoom = function(){}
QueueManager.prototype.UIRoom = function(){}
QueueManager.prototype.UIIncrementRoom = function(){}
QueueManager.prototype.UIDecrementRoom = function(){}
QueueManager.prototype.UISetRoom = function(new_room){}

// ----------- SWITCH TO OFF AIR ------------

function AirManager(station_client){}

// ----------- STATION CLIENT ---------------

// No counter, no suggestion/ library/ status or viral manager
StationClient.prototype.init = function(user, admin, station){
	this.user = user;
	this.admin = admin;
	this.station = station;
	this.channel_id = null;
	
	this.presence_manager = null;
	this.queue_manager = null;
	
	this.favorite_sdk = null;
	
	this.presence();
}

StationClient.prototype.fetch = function(){
	this.presence_manager = new PresenceManager(this); // Fetching
	
	// Once time has been initialized, initialize everything else
	var that = this;
	var pubnub_channel = PHB.version + "-" + this.station.shortname
	
	PHB.time(function(){
		that.queue_manager = new QueueManager(that); // Fetching
		that.favorite_sdk = new FavoriteSDK(that.queue_manager)
		
		that.comment_manager = new CommentManager(that);
		that.comment_manager.get(); // Fetching
	})
}

StationClient.prototype.dispatch = function(data){
	var message = JSON.parse(data);
	var entity = message.entity;
	var event = message.event;
	var content = message.content;
	
	PHB.log(entity + " " + event);
	
	var manager = null;
	if(entity == "presence"){
		manager = this.presence_manager;
	}
	if(entity == "broadcast"){
		manager = this.queue_manager;
	}
	
	if(manager){
		if(event == "new"){
			manager.new(content);
		}
		else{
			manager.remove(content);
		}
	}
}
