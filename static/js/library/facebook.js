$(function(){
	var app_id = phb.facebook_app_id;
	facebook = new Facebook(app_id);
})

function Facebook(app_id){
	this.app_id = app_id
}

Facebook.prototype = {
	
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
	

		
}