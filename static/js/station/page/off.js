// ---------------------------------------------------------------------------
// SPECIFIC OVERWRITING FUNCTIONS FOR IFRAME APP - "OFF" MODE
// ---------------------------------------------------------------------------

// ---------------- BROADCAST MANAGER -----------------

BroadcastManager.prototype.init = function(){
	// Settings
	this.url = "/api/broadcasts"
	this.data_type = "json"
	this.offset = PHB.now()
	
	// UI Settings
	this.name = "#broadcasts-tab";
	this.selector = this.name + " .tab-items";
	
	// Additional attributes
	this.live_item = null;
	this.youtube_manager = new EmbeddedYoutubeManager(this, 510, 287); // Dimensions changed
	
	this.get();
	// No Scroll listen
	this.liveListen();
}

// -------------- STATION CLIENT --------------

StationClient.prototype.init = function(user, admin, station){
	this.user = user;
	this.admin = admin;
	this.station = station;
	
	this.broadcast_manager = new BroadcastManager(this);
	this.favorite_sdk = new FavoriteSDK(this.broadcast_manager);
	
	this.comment_manager = new CommentManager(this);
	this.comment_manager.get(); // Force comments to be fetched
}




