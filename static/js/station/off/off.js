$(function(){
	STATION_CLIENT = new StationClient(USER, ADMIN, STATION, WEBSITE)
})

function StationClient(user, admin, station, website){
	this.user = user;
	this.admin = admin;
	this.station = station;
	this.website = website;
	
	this.broadcast_manager = new BroadcastManager(this);
	
	// If on Phonoblaster website, these elements need to be loaded
	if(this.website){
		this.air_manager = new AirManager(this);

		this.comment_manager = new CommentManager(this);
		this.comment_manager.get(); // Force comments to be fetched

		this.broadcasts_counter = new Counter("#broadcasts");
		this.views_counter = new Counter("#views");
	}

	this.favorite_sdk = new FavoriteSDK(this.broadcast_manager);
}