$(function(){
	FACEBOOK = new Facebook();
})

function Facebook(){
	this.app_id = FACEBOOK_APP_ID;
	this.version = VERSION;
	this.scope = 'user_likes,email,publish_actions,read_stream,publish_stream,manage_pages'
	// Note: recently publish_actions became a subset of publish_stream but we keep it like that
}

Facebook.prototype = {
	
	login: function(){
		var that = this;

		FB.login(function(response){
			PHB.log(response);
		},{ 
			scope: that.scope,
		});
	},
	
	logout: function(){
		FB.logout();
	},
	
	putTab: function(page_id, callback){
		var that = this;
		that.retrievePageToken(page_id, function(page_token){
			if(page_token){
				var url = "/" + page_id + "/tabs";
				FB.api(url, "post",{ access_token: page_token, app_id: that.app_id, }, callback)
			}
			else{
				callback(false)
			}
		})
	},
	
	retrievePageToken: function(page_id, callback){
		var url = "/" + page_id + "?fields=access_token";
		FB.api(url, function(response){
			var page_token = null;
			if(response.access_token){
				page_token = response.access_token;
			}
			callback(page_token)
		})
	},
	
	retrieveAdmins: function(page_id, callback){
		var that = this;
		this.retrievePageToken(
			page_id,
			function(page_token){
				var url = "/"+ page_id + "/admins"
				FB.api(url, { access_token: page_token }, function(response){
					var admins = response.data
					callback(admins);
				})
			}
		);
	},
	
	retrieveFriends: function(callback){
		var url = "/me/friends"
		FB.api(url, function(response){
			var friends = response.data
			callback(friends)
		})
	},
	
	putPageWallPost: function(page_id, message, link, picture, callback){
		var that = this;
		this.retrievePageToken(
			page_id,
			function(page_token){
				var url = "/"+ page_id + "/feed"
				FB.api(url, "post",{ access_token: page_token, message: message, link: link, picture: picture }, function(response){
					if(response.id){
						callback(true);
					}
					else{
						callback(false);
					}
				})
			}
		);
	},
	
	putWallPost: function(message, link, picture, callback){
		var url = "/me/feed"
		FB.api(url, "post", { message: message, link: link, picture: picture }, function(response){
			if(response.id){
				callback(true);
			}
			else{
				callback(false);
			}
		})
	},
	
	retrievePageWallPosts: function(page_id, callback){
		var url = "/"+ page_id + "/posts";
		FB.api(url, function(response){
			if(response.data){
				callback(response.data);
			}
			else{
				callback([]);
			}
		})
	},
	
	retrieveWallLinks: function(callback){
		var url = "/me/links?limit=50"
		FB.api(url, function(response){
			if(response.data){
				callback(response.data);
			}
			else{
				callback([]);
			}
		})
	},
	
	putComment: function(post_id, message, callback){
		var url = "/" + post_id + "/comments"
		FB.api(url, "post", { message: message }, function(response){
			if(response.id){
				callback(true)
			}
			else{
				callback(false)
			}
		})
	},
	
	putPageComment: function(page_id, post_id, message, callback){
		var that = this;
		this.retrievePageToken(
			page_id,
			function(page_token){
				var url = "/" + post_id + "/comments"
				FB.api(url, "post", { access_token: page_token, message: message }, function(response){
					if(response.id){
						callback(true)
					}
					else{
						callback(false)
					}
				})
			}
		)
	},
	
	putAction: function(action, obj, extra, expires_in){
		
		// Publishing actions does not work on local server
		if(this.version != "phb_local"){
			var url = "/me/" + this.version + ":" + action;		
			var instance = $.extend(obj, extra)

			var date = new Date(PHB.now()*1000);
			instance["start_time"] = date.toUTCString();
			instance["expires_in"] = parseInt(expires_in,10);

			FB.api(url, "post", instance, function(response){
				PHB.log(response);
			})
		}
		else{
			PHB.log("No Facebook action sent on localhost")
		}

	},
	
	shareStation: function(from, link, picture, name){
		var obj = {
			method: "feed",
			link: link,
			picture: picture,
			name: name,
		}
		
		if(from){
			obj["from"] = from;
		}
		
		FB.ui(obj, function(response){})
	},
	
	retrievePagePhotos: function(page_id, callback){
		var query = "SELECT src_big, src_big_width, src_big_height FROM photo WHERE aid IN (SELECT aid FROM album WHERE owner="+ page_id +")"
		var url = "/fql?q=" + encodeURIComponent(query)
		
		FB.api(url, function(response){
			callback(response.data)
		})
		
	}
}