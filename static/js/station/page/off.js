$(function(){
	STATION_CLIENT = new StationClient(USER, ADMIN, STATION)
})

function StationClient(user, admin, station){
	this.user = user;
	this.admin = admin;
	this.station = station;
	
	this.broadcast_manager = new BroadcastManager(this);
	this.favorite_sdk = new FavoriteSDK(this.broadcast_manager);
}