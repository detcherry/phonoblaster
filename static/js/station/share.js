// ---------------------------------------------------------------------------
// SHARE MANAGER
// ---------------------------------------------------------------------------

function ShareManager(client){
	this.client = client;
	this.listen();
}

ShareManager.prototype = {
	
	listen: function(){
		var that = this;
		
		$("a#fb-share").click(function(){
			var from = null;
			if(that.client.listener){
				if(that.client.admin){
					from = that.client.host.key_name;
				}
				else{
					from = that.client.listener.key_name;
				}
			}
			
			var link = PHB.site_url + "/" + that.client.host.shortname;
			var picture = PHB.site_url + "/" + that.client.host.shortname + "/picture";
			var name = that.client.host.name;
			var facebook_id = that.client.host.key_name;
			FACEBOOK.shareStation(from, link, picture, name);
			
			return false;
		})
	}
}