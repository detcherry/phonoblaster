// ---------------------------------------------------------------------------
// COMMENT MANAGER
// ---------------------------------------------------------------------------

CommentManager.prototype = new RealtimeTabManager();
CommentManager.prototype.constructor = CommentManager;

function CommentManager(station_client){
	RealtimeTabManager.call(this, station_client);
	
	// Settings
	this.url = "/api/comments"
	this.data_type = "json"
	
	// UI Settings
	this.selector = "#comments-display"
	
	// Init methods
	this.inputListen();
}

CommentManager.prototype.inputListen = function(){

	var that = this;
	
	// Listen to focus events in the comment form
	$("input#comments-input").focus(function(){
		var default_content = "Comment..."
		var content = $(this).val()
		
		if(content == default_content){
			//Clear the input text
			$(this).val("")
		}
		
		// If user not authenticated, display popup
		if(!that.station_client.user){
			FACEBOOK.login();
			$(this).blur();
		}
	})
	
	// Listen to submit events in the comment form
	$("form#comments-form").submit(function(){
		var message = $("input[id='comments-input']").val();
		
		if(message.length > 0 && message != "Comment..."){	
			// Build comment
			var new_item = that.prePostBuild(message);
			var div = that.UIBuild(new_item);
			
			// Add comment to the top
			that.UIPrepend(div);

			// Empty the comment box
			$("input[id='comments-input']").val("");

			// POST comment to everyone
			that.post(new_item, function(response){
				that.postCallback(new_item, response);
			});
			
			// POST comment to Facebook
			that.facebook(message);
		}
		
		return false;
	});
}

CommentManager.prototype.prePostBuild = function(message){
	
	// Build a comment key name
	var channel_id = this.station_client.channel_id;
	if(channel_id){
		var created = PHB.now();
		var random = Math.floor(Math.random()*100).toString();
		var comment_key_name = channel_id + ".comment." + created + random;
	}
	else{
		var created = PHB.now();
		var random = Math.floor(Math.random()*100).toString();
		var comment_key_name = this.station_client.station.shortname + ".offline.comment." + created + random
	}

	
	if(this.station_client.admin){
		var author_key_name = this.station_client.station.key_name;
		var author_name = this.station_client.station.name;
		var author_url = "/" + this.station_client.station.shortname;
		var admin = true;
	}
	else{
		var author_key_name = this.station_client.user.key_name;
		var author_name = this.station_client.user.name;
		var author_url = "/user/" + this.station_client.user.key_name;
		var admin = false; 
	}
	
	// Build content
	var content = {
		key_name: comment_key_name,
		message: message,
		author_key_name: author_key_name,
		author_name: author_name,
		author_url: author_url,
		admin: admin,
		created: created,
	}
	
	var new_item = this.serverToLocalItem(content)

	return new_item;	
}

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
			$("<div/>")
				.addClass("comment-submitter-picture")
				.append(
					$("<a/>")
						.attr("href", author_url)
						.attr("target", "_top")
						.append($("<img/>").attr("src", author_picture_url))
				)
		)
		.append(
			$("<div/>")
				.addClass("comment-content")
				.append(
					$("<p/>")
						.append($("<a/>").attr("href", author_url).attr("target", "_top").html(author_name))
						.append(" " + message)
				)
		)
		.append($("<div/>").addClass("comment-time").html(created))
				
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
		var youtube_thumbnail = "https://i.ytimg.com/vi/" + youtube_id + "/default.jpg";
		var track_submitter_name = content.track_submitter_name;
		var track_submitter_url = content.track_submitter_url;
		var track_submitter_picture = "https://graph.facebook.com/" + content.track_submitter_key_name + "/picture?type=square";
		
		var station_name = this.station_client.station.name;
		var station_url = "/" + this.station_client.station.shortname;
		var station_picture = "https://graph.facebook.com/" + this.station_client.station.key_name + "/picture?type=square";
		
		var mention = $("<p/>").append(
			$("<a/>")
				.attr("href", track_submitter_url )
				.attr("target", "_top")
				.html(track_submitter_name)
		)
		
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
			$("<div/>")
				.addClass("comment-submitter-picture")
				.append(
					$("<a/>")
						.attr("href", track_submitter_url)
						.attr("target", "_top")
						.append($("<img/>").attr("src", track_submitter_picture))
				)
		)
		.append(
			$("<div/>")
				.addClass("comment-content")
				.append(mention)
				.append(
					$("<div/>")
						.addClass("item")
						.append(
							$("<div/>")
								.addClass("item-picture")
								.append($("<img/>").attr("src", youtube_thumbnail))
						)
						.append(
							$("<div/>")
								.addClass("item-title")
								.append($("<span/>").addClass("middle").html(youtube_title))
						)
				)
				
		)
		.append($("<div/>").addClass("comment-time").html(created))		
		
	}
	
	return div
}

CommentManager.prototype.facebook = function(message){
	var that = this;
	var page_id = this.station_client.station.key_name;
	
	// Retrieve the latest station wall posts
 	FACEBOOK.retrievePageWallPosts(page_id, function(posts){
	
		var station_url = PHB.site_url + "/" + that.station_client.station.shortname;
		$.each(posts, function(index, post){
			// Pick up the last one with url = station url
			if(post.link == station_url){
				var post_id = post.id;
				
				var post_created_time = Date.parse(new Date(post.created_time))/1000
				var one_day = 86400;
				
				if(PHB.now()- post_created_time < one_day){
					// Add comment
					if(that.station_client.station.admin){
						FACEBOOK.putPageComment(page_id, post_id, message, function(response){})
					}
					else{
						FACEBOOK.putComment(post_id, message, function(response){})
					}
				}
				
				return false
			}
		})
		
	})
	
	
}

