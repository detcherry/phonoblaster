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
		
		$("a#tw-share").click(function(){
			var twitter = "https://twitter.com/share?"
			var href = "http://www.phonoblaster.com/" + that.client.host.shortname;
			var text = "♫ Listening to " + that.client.host.name + " radio on @phonoblaster ♫"
			
			var width = 800;
			var height = 450;
			var top = (screen.height/2) - height/2;
			var left = (screen.width/2) - width/2;

			var win = window.open("", "_blank", "top=" + top + ",left=" + left + ",width=" + width + ",height=" + height)
			
			var live = that.client.buffer_manager.live_item;			
			if(live.content.type == "soundcloud"){
				var id = live.content.id;
				
				SC.get("/tracks/" + id, function(track){					
					var title = live.content.title;
					var permalink = track.user.permalink;

					$.ajax({
						url: "/soundcloud/crawler/" + permalink,
						type: "GET",
						dataType: "json",
						timeout: 60000,
						error: function(xhr, status, error) {
							that.twitterPopup(null, win)
						},
						success: function(json){
							that.twitterPopup(json.twitter, win)
						},
					})
				})
			}
			else{
				that.twitterPopup(null, win)
			}
			
			return false;
		})
	},
	
	twitterPopup: function(handle, win){
		var twitter = "https://twitter.com/share?"
		var href = PHB.site_url + "/" + this.client.host.shortname;
		
		if(!handle){
			var text = "♫ Listening to " + this.client.host.name + " radio on @phonoblaster ♫"
		}
		else{
			var title = this.client.buffer_manager.live_item.content.title;
			var number_of_characters = 20 + 7 + handle.length + 17 + href.length;
			var available_characters = 140 - number_of_characters;
			
			if(this.client.admin){
				var text = "Live broadcasting ♫ " + title.substring(0, available_characters) + " ♫ by @" + handle + " on @phonoblaster"
			}
			else{
				var text = "Listening now to ♫ " + title.substring(0, available_characters) + " ♫ by @" + handle + " on @phonoblaster"
			}
		}

		var share = twitter + "href=" + encodeURIComponent(href) + "&text=" + encodeURIComponent(text);
		
		// Change popup URL		
		win.location.href = share;
	},
	
}