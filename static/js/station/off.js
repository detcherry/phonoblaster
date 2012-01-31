$(function(){
	STATION_CLIENT = new StationClient(USER, ADMIN, STATION)
})

function StationClient(user, admin, station){
	this.user = user;
	this.admin = admin;
	this.station = station;
	
	this.broadcasts_counter = new Counter("#broadcasts");
	this.views_counter = new Counter("#views");
	
	this.broadcast_manager = new BroadcastManager(this);
}