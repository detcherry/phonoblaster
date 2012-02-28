// ---------------------------------------------------------------------------
// OVERWRITES FUNCTIONS (SPECIFIC TO THE IFRAME APP)
// ---------------------------------------------------------------------------

// ------------ Facebook ------------

// Necessary to grab the page id before reloading the iFrame
Facebook.prototype.login = function(){
	
	var that = this;
	FB.login(function(response){
		if(response.authResponse){
			
			// Stop the timer resizing the iframe height
			FB.Canvas.setAutoGrow(false);
			
			// Reload the iframe (GET parameter this time)
			var page_id = STATION_CLIENT.station.key_name
			window.location.href = PHB.site_url + "/station/page?id=" + page_id
	
		}
	},{scope: that.scope});

}

Facebook.prototype.loginAndRedirect = function(){
	
	var that = this;
	FB.login(function(response){
		if(response.authResponse){
			
			// Open the new URL in the main window
			var shortname = STATION_CLIENT.station.shortname;
			var url = PHB.site_url + "/" + shortname;
			window.open(url, "_top");			
			
		}
	})
	
}