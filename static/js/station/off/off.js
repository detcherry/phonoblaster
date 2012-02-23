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

		this.broadcast_manager = new BroadcastManager(this);
		this.air_manager = new AirManager(this);

		this.comment_manager = new CommentManager(this);
		this.comment_manager.get(); // Force comments to be fetched

		this.favorite_sdk = new FavoriteSDK(this.broadcast_manager);
	}
	
}