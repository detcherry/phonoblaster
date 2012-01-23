$(function(){
	var app_id = PHB.facebook_app_id;
	FACEBOOK = new Facebook(app_id);
})

function Facebook(app_id){
	this.app_id = app_id
}

Facebook.prototype = {
	
	login: function(){
		FB.login(function(response){
			if(response.authResponse){
				window.location.reload();
			}
		 },{scope: 'email, publish_actions, read_stream, publish_stream, manage_pages'});
	},
	
	logout: function(){
		FB.logout(function(response){
			window.location.reload();
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
	
	putTab: function(page_id, page_token, callback){
		var url = "/" + page_id + "/tabs";
		var that = this;
		FB.api(url, "post",{ access_token: page_token, app_id: that.app_id, }, callback)
	},
	
	createPhonoblasterTab: function(page_id, callback){
		var that = this;
		this.retrievePageToken(
			page_id,
			function(page_token){
				that.putTab(page_id, page_token, callback);
			}
		);
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
					PHB.log(response);
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
			PHB.log(response);
			if(response.id){
				callback(true);
			}
			else{
				callback(false);
			}
		})
	},
		
}