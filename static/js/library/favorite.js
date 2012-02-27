// ---------------------------------------------------------------------------
// FAVORITE SDK
// ---------------------------------------------------------------------------

function FavoriteSDK(track_manager){
	this.url = "/api/favorites";
	this.track_manager = track_manager;
	
	this.postListen();
	this.deleteListen();
}

FavoriteSDK.prototype = {
	
	// Listen to click events on fav icons
	postListen: function(){
		var that = this;

		$("a.fav").live("click", function(){
			var station_client = that.track_manager.station_client
			var user = station_client.user
			
			if(!user){
				FACEBOOK.login()
			}
			else{
				var new_item = that.track_manager.live_item;

				// Change icon
				var btn = $(this)
				that.toggle(btn)

				// POST new favorite to server
				that.post(new_item, function(response){
					that.postCallback(btn, response)
				})

				// Post action to FACEBOOK
				that.postAction(new_item);
			}
			
			$(this).blur();
			return false;
			
		})
	},
	
	toggle: function(btn){
		if(btn.hasClass("fav")){
			btn.removeClass("fav").addClass("unfav").addClass("tuto").attr("data-original-title", "Unfavorite this track")
		}
		else{
			btn.removeClass("unfav").addClass("fav").addClass("tuto").attr("data-original-title", "Favorite this track")
		}
	},
	
	// Build data to POST
	postData: function(item){
		var data = {
			content: JSON.stringify(item.content),
		}
		return data
	},
	
	// POST request to server
	post: function(item, callback){
		var data = this.postData(item);
		var that = this;

		$.ajax({
			url: that.url,
			type: "POST",
			dataType: "json",
			timeout: 60000,
			data: data,
			error: function(xhr, status, error) {
				callback(false)
			},
			success: function(json){
				callback(json.response);
			},
		});

	},
	
	postCallback: function(btn, response){
		if(!response){
			this.toggle(btn);
			PHB.error("Favorite has not been stored")
		}
	},
	
	postAction: function(item){
		var track_url = PHB.site_url + "/track/" + item.content.track_id;

		var obj = { "track": track_url };
		var extra = {};
		var expires_in = 0;
		var action = "favorite";	

		FACEBOOK.putAction(action, obj, extra, expires_in);
	},
	
	deleteListen: function(){
		var that = this;

		$("a.unfav").live("click", function(){
			// Clone live item
			var item = $.extend(true, {}, that.track_manager.live_item);

			// Change icon
			var btn = $(this)
			that.toggle(btn)

			that.delete(item, function(response){
				that.deleteCallback(btn, response)
			})

			$(this).blur();
			return false;
		})
	},
	
	delete: function(item, callback){
		var that = this;
		var delete_url = that.url + "/" + item.content.track_id
		
		$.ajax({
			url: delete_url,
			type: "DELETE",
			dataType: "json",
			timeout: 60000,
			error: function(xhr, status, error) {
				callback(false)
			},
			success: function(json){
				callback(json.response);
			},
		});
	},
	
	deleteCallback: function(btn, response){
		if(!response){
			btn.removeClass("fav").addClass("unfav");
			PHB.error("Favorite has not been deleted.")
		}
	},
	
}