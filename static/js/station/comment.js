// ---------------------------------------------------------------------------
// COMMENT MANAGER
// ---------------------------------------------------------------------------

function CommentManager(station_client){
	this.station_client = station_client;
	this.comments = [];
	this.init();
}

CommentManager.prototype = {
	
	init: function(){
		
		// Fetch latest comments (Messages in the last 3 minutes)
		this.fetch();
		
		// Listen to focus/ unfocus events
		this.listen();
		
	},
	
	fetch: function(){
		var that = this;	
		var shortname = this.station_client.station.shortname;
		// Fetch station comments
		$.ajax({
			url: "/api/comments",
			type: "GET",
			dataType: "json",
			timeout: 60000,
			data: {
				shortname: shortname,
			},
			error: function(xhr, status, error) {
				PHB.log('An error occurred: ' + error + '\nPlease retry.');
			},
			success: function(json){
				latest_comments = json;
				
				// Add each comment to the DOM
				$.each(latest_comments, function(index, value){
					var new_comment = value;
					that.add(new_comment);
				})
			},
		});
		
	},
	
	add: function(new_comment){		
		var that = this;
		
		following_comments = [];
		previous_comments = this.comments;
		var previous_comment = null;
		
		// If comments array empty, just add the new comment to the list
		if(that.comments.length == 0){
			this.comments.push(new_comment)
		}
		else{
			// Browse the comments list and insert the comment at the right place
			for(i=0, c=that.comments.length; i<c; i++){
				var comment = that.comments[i];

				// The new comment has been posted before (NOT OK)
				if(comment.created > new_comment.created){
					following_comments.push(previous_comments.shift());
				}
				// The new comment has been posted after (OK)
				else{
					previous_comment = comment;
					following_comments.push(new_comment);
					break;
				}
			}
			this.comments = following_comments.concat(previous_comments);
		}
		
		// Insert new comment 
		this.UIDisplay(new_comment, previous_comment)
	},
	
	UIDisplay: function(new_comment, previous_comment){
		var re = RegExp("[.]","g");
		var new_comment_selector = "#" + new_comment.key_name.replace(re, "\\.");
		
		// If the comment was initially displayed, we don't care (honey badger style) and remove it
		$(new_comment_selector).remove();
		
		if(previous_comment){
			// If there was a previous comment, we insert the new comment just before
			var previous_comment_selector = "#" + previous_comment.key_name.replace(re, "\\.");
			this.UIInsert(new_comment, previous_comment_selector)
		}
		else{
			// Else, we have to append the comment at the top
			this.UILocalDisplay(new_comment)
		}
		
	},
	
	listen: function(){
		var that = this;
		
		// Listen to focus events in the comment form
		$("#comment-box input#comment").focus(function(){
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
		$("form#comment").submit(function(){
			var content = $("input[id='comment']").val();
			
			if(content.length > 0){
				
				PHB.time(function(time){
					// Build comment
					var local_comment = that.localBuild(content, time);

					// Add comment at the top
					that.UILocalDisplay(local_comment);

					// Empty the comment box
					$("input[id='comment']").val("");

					// post comment to everyone
					that.post(local_comment);
				})
			}
			
			return false;
		});
		
	},
	
	localBuild: function(content, time){
		
		// Build a comment key name
		var channel_id = this.station_client.channel_id;
		var comment_key_name = channel_id + ".comment." + time;
		
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
		
		// Build local comment to display
		var local_comment = {
			key_name: comment_key_name,
			content: content,
			author_key_name: author_key_name,
			author_name: author_name,
			author_url: author_url,
			admin: admin,
			created: time,
		}

		return local_comment;
	},
	
	UIBuild: function(new_comment, callback){
		var author_picture_url = "https://graph.facebook.com/"+ new_comment.author_key_name + "/picture?type=square";
		var author_name = new_comment.author_name;
		var author_url = new_comment.author_url;
		var comment_key_name = new_comment.key_name;
		var comment_content = new_comment.content;
		var comment_time = PHB.convert(new_comment.created);
		
		callback(
			$("<div/>")
				.addClass("comment")					
				.attr("id", comment_key_name)
				.append(
					$("<img/>")
						.attr("src", author_picture_url)
						.addClass("user")
				)
				.append(
					$("<div/>")
						.addClass("content")
						.append(
							$("<p/>")
								.append($("<a/>").attr("href", author_url).html(author_name))
								.append(" ")
								.append(comment_content)
						)

				)
				.append($("<div/>").addClass("border"))
				.append($("<div/>").addClass("time").html(comment_time))
		)
		
	},
	
	UILocalDisplay: function(new_comment){
		this.UIBuild(new_comment, function(new_comment_jquery_object){
			// Append new comment div at the top of the comments zone
			$("#comments-zone").prepend(new_comment_jquery_object)
		})
	},
	
	UIInsert: function(new_comment, previous_comment_selector){
		this.UIBuild(new_comment, function(new_comment_jquery_object){
			// Insert new comment div just before the previous comment div
			new_comment_jquery_object.insertBefore(previous_comment_selector)
		})
	},
	
	post: function(new_comment){
		var shortname = this.station_client.station.shortname
		var that = this;
		$.ajax({
			url: "/api/comments",
			type: "POST",
			dataType: "json",
			timeout: 60000,
			data: {
				shortname: shortname,
				key_name: new_comment.key_name,
				content: new_comment.content,
			},
			error: function(xhr, status, error) {
				PHB.log('An error occurred: ' + error + '\nPlease retry.');
			},
			success: function(json){
				PHB.log(json.response)
			},
		});		
	},
		
}