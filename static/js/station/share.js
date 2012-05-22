// ---------------------------------------------------------------------------
// SHARE MANAGER
// ---------------------------------------------------------------------------

function ShareManager(station_client){
	this.station_client = station_client;
	this.listen();
}

ShareManager.prototype = {
	
	listen: function(){
		var that = this;
		
		$("a#fb-share").click(function(){
			var from = null;
			if(that.station_client.user){
				if(that.station_client.admin){
					from = that.station_client.station.key_name;
				}
				else{
					from = that.station_client.user.key_name;
				}
			}
			
			var link = PHB.site_url + "/" + that.station_client.station.shortname;
			var picture = PHB.site_url + "/" + that.station_client.station.shortname + "/picture";
			var name = that.station_client.station.name;
			var facebook_id = that.station_client.station.key_name;
			FACEBOOK.shareStation(from, link, picture, name);
			
			return false;
		})
}