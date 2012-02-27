$(function(){
	STATION_CLIENT = new StationClient(USER, ADMIN, STATION)
})

// ------------ STATION CLIENT --------------
function StationClient(user, admin, station){
	this.user = user;
	this.admin = admin;
	this.station = station;
	
	this.track_manager = new TrackManager(this);
	this.favorite_sdk = new FavoriteSDK(this.track_manager)
}

// ------------ TRACK MANAGER --------------
function TrackManager(station_client){
	this.station_client = station_client;
	this.live_item = LIVE_ITEM;
	var that = this
	
	// Init interface
	$("#media").empty().append($("<div/>").attr("id","youtube-player"));
	$("#media-details-right").append($("<a/>").addClass("fav").addClass("tuto").attr("data-original-title", "Favorite this track"));
	$("#media-title span.middle").html(that.live_item.content.youtube_title);
	$("#media-picture").append($("<img/>").attr("src", "https://i.ytimg.com/vi/" + that.live_item.content.youtube_id + "/default.jpg"));
	
	this.youtube_manager = new EmbeddedYoutubeManager(this, 640, 360)
	this.youtube_manager.init(LIVE_ITEM.content.youtube_id)
}

TrackManager.prototype = {
	
	nextVideo: function(){},
	
}