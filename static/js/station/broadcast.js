$(function(){
	STATION_CLIENT = new StationClient(USER, ADMIN, STATION)
})

// ------------ STATION CLIENT --------------
function StationClient(user, admin, station){
	this.user = user;
	this.admin = admin;
	this.station = station;
	
	this.broadcasts_counter = new Counter("#broadcasts");
	this.views_counter = new Counter("#views");
	
	this.track_manager = new BroadcastManager(this);
	this.latest_manager = new LatestManager(this);
	
	this.favorite_sdk = new FavoriteSDK(this.track_manager)
}

// ------------ BROADCAST MANAGER --------------
function BroadcastManager(station_client){
	this.station_client = station_client;
	this.live_item = LIVE_ITEM;
	
	this.youtube_manager = new EmbeddedYoutubeManager(this)
	this.youtube_manager.init(LIVE_ITEM.content.youtube_id)
}

BroadcastManager.prototype = {
	
	nextVideo: function(){},
	
}