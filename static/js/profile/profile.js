$(function(){
	STATION_CLIENT = new StationClient(USER, PROFILE)
})

function StationClient(user, profile){
	this.init(user, profile);
}

StationClient.prototype = {
	
	init: function(user, profile){
		this.user = user;
		this.profile = profile;

		this.favorite_manager = new FavoriteManager(this);
		this.favorite_sdk = new FavoriteSDK(this.favorite_manager);
	}
	
}