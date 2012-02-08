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


// ----------- Comment -----------

// Necessary to add target = blank for every link
CommentManager.prototype.UIBuild = function(item){
	
	// There are 2 types of items: real comments and broadcast notifications
	if(item.content.message){
		// This a real comment
		var id = item.id;
		var content = item.content;
		var created = PHB.convert(item.created);
		
		var author_picture_url = "https://graph.facebook.com/"+ content.author_key_name + "/picture?type=square";
		var author_name = content.author_name;
		var author_url = content.author_url;
		
		var message = content.message;
		
		var div = $("<div/>").addClass("comment").attr("id", id)
		
		div.append(
			$("<img/>")
				.attr("src", author_picture_url)
				.addClass("user")
			)
			.append(
				$("<div/>")
					.addClass("content")
					.append(
						$("<p/>")
							.append($("<a/>").attr("href", author_url).attr("target", "_top").html(author_name))
							.append(" " + message)
					)
			)
			.append($("<div/>").addClass("border"))
			.append($("<div/>").addClass("time").html(created))
		
	}
	else{
		// This is a broadcast notification
		var id = item.id;
		var content = item.content;
		var created = PHB.convert(item.created);
		
		var type = content.type;
		var youtube_id = content.youtube_id;
		var youtube_title = content.youtube_title;
		var youtube_duration = PHB.convertDuration(content.youtube_duration)
		var youtube_thumbnail = "http://i.ytimg.com/vi/" + youtube_id + "/default.jpg";
		var track_submitter_name = content.track_submitter_name;
		var track_submitter_url = content.track_submitter_url;
		var track_submitter_picture = "https://graph.facebook.com/" + content.track_submitter_key_name + "/picture?type=square";
		
		var station_name = this.station_client.station.name;
		var station_url = "/" + this.station_client.station.shortname;
		var station_picture = "https://graph.facebook.com/" + this.station_client.station.key_name + "/picture?type=square";
		
		var mention = $("<p/>").append($("<a/>").attr("href", track_submitter_url ).attr("target", "_top").html(track_submitter_name))
		
		if(type == "track"){
			// Regular broadcast
			mention.append(" just broadcast a track")
		}
		if(type == "suggestion"){
			// Suggestion
			mention
				.append(" suggestion was broadcast by ")
				.append($("<a/>").attr("href", station_url).attr("target", "_top").html(station_name))
		}
		if(type == "favorite"){
			// Rebroadcast
			mention
				.append(" track was rebroadcast by ")
				.append($("<a/>").attr("href", station_url).attr("target", "_top").html(station_name))
		}
		
		var div = $("<div/>").addClass("comment").attr("id", id)
		
		div.append(
			$("<img/>")
				.attr("src", track_submitter_picture)
				.addClass("station")
			)
			.append(
				$("<div/>")
					.addClass("content")
					.append(mention)
					.append(
						$("<span/>")
							.addClass("clip")
							.append(
								$("<img/>").attr("src", youtube_thumbnail)
							)
					)
					.append(
						$("<div/>")
							.addClass("title")
							.append(
								$("<span/>")
									.addClass("middle")
									.html(youtube_title)
							)
					)
			)
			.append($("<div/>").addClass("border"))
			.append($("<div/>").addClass("time").html(created))
		
	}
	
	return div
}