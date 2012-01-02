function StationClient(user, admin, station){
	this.user = user;
	this.admin = admin;
	this.station = station;
	this.channel_id = null;
	this.presence_manager = null;
	this.comment_manager = null;
	this.status_manager = null;
	this.queue_manager = null;
	this.presence();
}

StationClient.prototype = {
	
	// Add a new presence: request Client ID and Token from Google App Engine
	presence: function(){
		var that = this;
				
		$.ajax({
			url: "/api/presences",
			type: "POST",
			dataType: "json",
			timeout: 60000,
			data: {
				shortname: that.station.shortname,
			},
			error: function(xhr, status, error) {
				PHB.log('An error occurred: ' + error + '\nPlease retry.');
			},
			success: function(json){				
				// Store the presence channel id
				that.channel_id = json.channel_id;
				
				// Create a presence channel
				var channel = new goog.appengine.Channel(json.channel_token);
				
				// Open connection and hook callbacks
				var socket = channel.open();
				socket.onerror = window.location.reload;
				socket.onclose = window.location.reload;
				
				// Subscribe to the station channel
				var station_client = that;
				socket.onopen = function(){
					station_client.pubnub();
				}
				
				// We do not hook the following callback
				// - socket.onmessage
			},
		});
	},
	
	// Subscribe to the station channel with Pubnub
	pubnub: function(){
		var that = this;
		var pubnub_channel = PHB.version + "-" + this.station.shortname
		// Subscribe to the station channel with Pubnub
		PUBNUB.subscribe({
	        channel: pubnub_channel,      
	        error: function(){
				alert("Connection Lost. Will auto-reconnect when Online.");
			},
	        callback: function(message) {
	            that.dispatch(message);
	        },
	        connect: function(){
				// Fetch all the content: presences, comments, queue
				that.fetch();
	        }
		})
	},
	
	// Fetch presences, comments and queue after connection to pubnub
	fetch: function(){
		this.presence_manager = new PresenceManager(this);
		this.comment_manager = new CommentManager(this);
		this.status_manager = new StatusManager(this);
		this.queue_manager = new QueueManager(this);
	},
	
	// Dispatch incoming messages according to their content
	dispatch: function(data){
		var message = JSON.parse(data);
		var event = message.event;
		var content = message.content;
		
		if(event == "new-presence"){
			PHB.log("new-presence");
			this.presence_manager.add(content);
		}
		if(event == "presence-removed"){
			PHB.log("presence-removed");
			this.presence_manager.remove(content);
		}
		if(event == "new-comment"){
			PHB.log("new-comment");
			this.comment_manager.add(content);
		}
	},
	
}

// ---------------------------------------------------------------------------
// PRESENCE MANAGER
// ---------------------------------------------------------------------------

function PresenceManager(station_client){
	this.station_client = station_client;
	this.duplicate_presences = [];
	
	this.admins_presences = [];
	this.friends_presences = [];
	this.authenticated_presences = [];
	this.unauthenticated_presences = [];
	
	this.admins = [];
	this.friends = [];
	this.init();
}

PresenceManager.prototype = {
	
	init: function(){
		var that = this;
		// Fetch admins first
		this.fetchAdmins(function(){
			// Then fetch friends
			that.fetchFriends(function(){
				// Finally fetch presences
				that.fetchPresences();
			});
		});
	},
	
	// Fetch the admins of a page (only for station admins)
	fetchAdmins: function(callback){
		if(this.station_client.admin){
			var that = this;
			var page_id = this.station_client.station.key_name
			FACEBOOK.retrieveAdmins(page_id, function(admins){
				that.admins = admins;
				callback();
			})
		}
		else{
			callback();
		}

	},
	
	// Fetch the user friends (only for authenticated users)
	fetchFriends: function(callback){
		if(this.station_client.user){
			var that = this;
			FACEBOOK.retrieveFriends(function(friends){
				that.friends = friends;
				callback();
			})
		}
		else{
			callback();
		}
	},
	
	// Fetch station presences (for everyone)
	fetchPresences: function(){
		var that = this;	
		var shortname = this.station_client.station.shortname;
		// Fetch station presences
		$.ajax({
			url: "/api/presences",
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
				new_presences = json;
				
				// Add each new presence to the DOM
				$.each(new_presences, function(index, value){
					var new_presence = value
					that.add(new_presence);
				})
				
				// Listen to click events on the listeners link
				that.listen();
			},
		});
	},
	
	// Add new presence to the DOM
	add: function(new_presence){		
		var duplicate = false;
		
		// Concat all presences array to obtain all the unique existing presences
		existing_presences = this.admins_presences.concat(
			this.friends_presences,
			this.authenticated_presences,
			this.unauthenticated_presences
		);
		
		// Check if the new presence is not a duplicate of an existing presence
		for(i=0, c=existing_presences.length; i<c; i++){
			var existing_presence = existing_presences[i];
			if(existing_presence.user_key_name == new_presence.user_key_name){
				duplicate = true;
				break;
			}
		}
		
		if(duplicate){
			this.duplicate_presences.push(new_presence);
		}
		else{
			this.dispatch(new_presence);
		}	
	},

	// Dispatch the new presence according to his status: admin, friend of the current user, just authenticated or anonymous
	dispatch: function(new_presence){
		var outer_div = null;
		
		if(this.isAuthenticated(new_presence)){
			if(this.isAdmin(new_presence)){
				outer_div = $("#admins-rows")
				this.admins_presences.push(new_presence)
			}
			else{
				if(this.isFriend(new_presence)){
					outer_div = $("#friends-rows");
					this.friends_presences.push(new_presence)
				}
				else{
					outer_div = $("#authenticated-rows");
					this.authenticated_presences.push(new_presence)
				}
			}
		}
		else{
			this.unauthenticated_presences.push(new_presence)
		}
		
		// If user is authenticated 
		if(outer_div){
			var channel_id = new_presence.channel_id
			var user_url = "/user/"+ new_presence.user_key_name;
			var user_picture_url = "https://graph.facebook.com/"+ new_presence.user_key_name + "/picture?type=square";
			var user_name = new_presence.user_name;
			
			// Append div to DOM
			outer_div.append(
				$("<div/>")
					.addClass("row")
					.addClass("presence")
					.attr("id",channel_id)
					.append(
						$("<a/>")
							.attr("href", user_url)
							.append($("<img/>").attr("src", user_picture_url))
							.append(
								$("<div/>")
									.addClass("title")
									.append(
										$("<span/>")
											.addClass("middle")
											.html(user_name)
									)
							)
					)
			)
		}
		
		// Update the presence counter
		this.updateCounter()
	},
	
	// Remove the presence that is now gone
	remove: function(presence_gone){		
		var was_duplicate = false;

		// We gonna check first in the duplicate list
		var that = this;
		for(i=0, c=that.duplicate_presences.length; i<c; i++){
			var duplicate_presence = that.duplicate_presences[i];
			if(duplicate_presence.channel_id == presence_gone.channel_id){
				that.duplicate_presences.splice(i,1);
				was_duplicate = true;
				break;
			}
		}
		
		// If we don't find it in the duplicate list, we look everywhere else
		var correct_presences_list = null;
		if(!was_duplicate){
			// First, we inspect where to look for
			if(this.isAuthenticated(presence_gone)){
				if(this.isAdmin(presence_gone)){
					correct_presences_list = this.admins_presences
				}
				else{
					if(this.isFriend(presence_gone)){
						correct_presences_list = this.friends_presences
					}
					else{
						correct_presences_list = this.authenticated_presences
					}
				}
			}
			else{
				correct_presences_list = this.unauthenticated_presences
			}
			
			// Once we pick up the right user list, we remove the presence
			for(i=0, c=correct_presences_list.length; i<c; i++){
				var presence = correct_presences_list[i];
				if(presence.channel_id == presence_gone.channel_id){
					correct_presences_list.splice(i,1);
					
					// If user is authenticated, we also remove it from the interface
					if(this.isAuthenticated(presence_gone)){
						var channel_id = presence_gone.channel_id;
						
						// A little trick necessary for attributes that features a '.'
						var re = RegExp("[.]","g");
						var jquery_id = "#" + channel_id.replace(re, "\\.");
						$(jquery_id).remove();
					}
					
					// Stop the loop
					break;
				}
			}
			
			// If the same user was in the duplicate presences, we put it back in the correct list
			if(this.isAuthenticated(presence_gone)){
				for(i=0, c=that.duplicate_presences.length; i<c; i++){
					var duplicate_presence = that.duplicate_presences[i];
					if(duplicate_presence.user_key_name == presence_gone.user_key_name){
						// We remove the presence from the duplicates
						that.duplicate_presences.splice(i,1)
						
						// We put it to the correct list
						that.add(duplicate_presence);
						
						// Stop the loop
						break;
					}					
				}
			}
					
		}
		
		this.updateCounter();
	},
	
	// Get the presences counter
	getCounter: function(){
		var existing_presences = [];
		
		// Whether the current user is an admin or not, we count the number of admins in the number of presences
		if(this.station_client.admin){
			existing_presences = this.admins_presences.concat(
				this.friends_presences,
				this.authenticated_presences,
				this.unauthenticated_presences
			);
		}
		else{
			existing_presences = this.friends_presences.concat(
				this.authenticated_presences,
				this.unauthenticated_presences
			);
		}
		
		var presences_counter = existing_presences.length;
		return presences_counter;
	},
	
	// Update the presence counter
	updateCounter: function(){
		var new_counter = this.getCounter();
		$("#presences .number").html(new_counter);
	},
	
	// Check if a presence is an authenticated user
	isAuthenticated: function(presence){
		var response = false;
		if(presence.user_key_name){
			response = true;
		}
		return response
	},
	
	// Check if a presence is an admin user
	isAdmin: function(presence){
		var response = false;
		var that = this;
		for(i=0, c=that.admins.length; i<c; i++){
			var admin = that.admins[i];
			if(presence.user_key_name == admin.id){
				response = true;
				break;
			}
		}
		return response;
	},
	
	// Check if a presence is a friend of current user
	isFriend: function(presence){
		var response = false;
		var that = this;
		for(i=0, c=that.friends.length; i<c; i++){
			var friend = that.friends[i]
			if(presence.user_key_name == friend.id){
				response = true;
				break;
			}
		}
		return response;
	},
	
	listen: function(){
		var that = this;
		
		// When somebody clicks on the listener link, a pop up displays all the listeners
		$("div#presences a span.title").click(function(){
			that.buildPresencesPopup();
			
			// Nofollow.
			 this.blur();
			 return false;
		})
	},
	
	buildPresencesPopup: function(){
		
		var popup_content = $("#presence-rows").clone()
		
		// Change id attribute
		popup_content.attr("id","presence-popup")
		
		// Add a title
		var presences_counter = this.getCounter();
		popup_content.prepend($("<h2/>").html("Listeners ("+ presences_counter +")"))
		
		// Add at the bottom the number of unauthenticated users
		var unauthenticated_counter = this.unauthenticated_presences.length;
		if(unauthenticated_counter != 0){
			popup_content.append(
				$("<div/>")
					.addClass("row")
					.addClass("presence")
					.attr("id","unauthenticated-presences")
					.append($("<strong/>").html(unauthenticated_counter))
					.append($("<span/>").html(" anonymous users"))
			)
		}
		
		$.fancybox(popup_content,{
			maxWidth	: 400,
			maxHeight	: 400,
			fitToView	: false,
			width		: 400,
			height		: 400,
			autoSize	: false,
			closeClick	: false,
			openEffect	: 'none',
			closeEffect	: 'none',
			scrolling	: 'auto',
		});
		
	},
}

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
		this.fetchLatestComments();
		
		// Listen to focus/ unfocus events
		this.listen();
		
	},
	
	fetchLatestComments: function(){
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
					that.IOAdd(new_comment);
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
			var admin = true;
		}
		else{
			var author_key_name = this.station_client.user.key_name;
			var author_name = this.station_client.user.name;
			var admin = false; 
		}
		
		// Build local comment to display
		var local_comment = {
			key_name: comment_key_name,
			content: content,
			author_key_name: author_key_name,
			author_name: author_name,
			admin: admin,
			created: time,
		}

		return local_comment;
	},
	
	UIBuild: function(new_comment, callback){
		var author_picture_url = "https://graph.facebook.com/"+ new_comment.author_key_name + "/picture?type=square";
		var author_name = new_comment.author_name;
		
		if(new_comment.admin){
			var author_url = "/" + this.station_client.station.shortname;
		}
		else{
			var author_url = "/user/" + new_comment.author_key_name;
		}
		
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

// ---------------------------------------------------------------------------
// STATUS MANAGER
// ---------------------------------------------------------------------------

function StatusManager(station_client){
	// Reference useful to access the admin status of the current user
	this.station_client = station_client;
	this.status = null;
	this.init();
}

StatusManager.prototype = {
	
	init: function(){
		PHB.log("Listening to status events if user is admin")
	},
	
	setStatus: function(new_status){
		this.status = new_status;
		this.displayStatus();
	},
	
	displayStatus: function(){
		PHB.log("Display status")
	},
	
}

// ---------------------------------------------------------------------------
// QUEUE MANAGER
// ---------------------------------------------------------------------------


function QueueManager(station_client){
	// Reference useful to access the other managers from the queue manager
	this.station_client = station_client;
	this.queue = null;
	this.init();
}

QueueManager.prototype = {
	
	init: function(){
		PHB.log("Fetch queue")
	},
	
}

