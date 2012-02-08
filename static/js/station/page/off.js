// ---------------------------------------------------------------------------
// SPECIFIC OVERWRITING FUNCTIONS FOR IFRAME APP - "OFF" MODE
// ---------------------------------------------------------------------------

StationClient.prototype.init = function(user, admin, station){
	this.user = user;
	this.admin = admin;
	this.station = station;
	
	this.broadcast_manager = new BroadcastManager(this);
	this.favorite_sdk = new FavoriteSDK(this.broadcast_manager);
	
	this.comment_manager = new CommentManager(this);
	this.comment_manager.get(); // Force comments to be fetched
}