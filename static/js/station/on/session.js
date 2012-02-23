// ---------------------------------------------------------------------------
// SESSION MANAGER
// ---------------------------------------------------------------------------

function SessionManager(station_client){
	this.station_client = station_client;
	
	//this.sessions_counter = new Counter("#sessions");
	this.sessions_counter = null;
	this.friend_sessions = [];
	this.duplicate_friend_sessions = [];
	
	this.friends = [];
	this.init();
}


SessionManager.prototype = {
	
	init: function(){
		var that = this;
		
		if(this.station_client.user){
			// First fetch friends
			this.fetchFriends(function(){
				// Then fetch sessions
				that.fetchSessions();
			});	
		}
		else{
			// Fetch sessions directly (in fact only the number of sessions)
			that.fetchSessions();
		}
	},
	
	// Fetch the user friends (works only for authenticated users)
	fetchFriends: function(callback){
		var that = this;
		FACEBOOK.retrieveFriends(function(friends){
			that.friends = friends;
			callback();
		})
	},
	
	// Fetch friend sessions
	fetchSessions: function(){
		var that = this;	
		var shortname = this.station_client.station.shortname;
		// Fetch station presences
		$.ajax({
			url: "/api/sessions",
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
				// Init sessions counter
				$("#top-right-sessions span.figure").html(json.number)
				that.sessions_counter = new Counter("#top-right-sessions");
				
				if(json.friends){
					friends = json.friends

					// Add each new friend session to the DOM
					$.each(friends, function(index, value){
						var friend_session = value
						that.add(friend_session);
					})
				}
				else{
					// Display facebook facepile or 'login button to see friends listening'
				}
	
			},
		});
	},
	
	// Incoming sessions received from PubNub
	new: function(new_session){
		this.add(new_session)
		
		// Increment sessions counter
		if(this.sessions_counter){
			this.sessions_counter.increment();
		}
	},
	
	// Process incoming sessions
	add: function(new_session){
		if(this.isFriend(new_session)){
			var that = this;
			
			// Check if the new listener is not already listening
			var duplicate = false;
			for(var i=0, c=that.friend_sessions.length; i<c; i++){
				var friend_session = that.friend_sessions[i];
				if(friend_session.listener_key_name == new_session.listener_key_name){
					duplicate = true;
					break;
				}
			}
			
			if(duplicate){
				this.duplicate_friend_sessions.push(new_session)
			}
			else{
				// Add session to the friends list
				this.friend_sessions.push(new_session)

				// Add session to the UI
				this.UIAdd(new_session)
			}
		}
	},
	
	UIAdd: function(session){
		var channel_id = session.key_name;
		var listener_picture_url = "https://graph.facebook.com/"+ session.listener_key_name + "/picture?type=square";
		var listener_name = session.listener_name;
		var listener_url = session.listener_url;
		
		$("#top-right-session-pictures").append(
			$("<a/>")
				.attr("id", channel_id)
				.attr("href", listener_url)
				.addClass("tuto") // Twipsy
				.addClass("session-picture")
				.attr("data-original-title", listener_name) // Twipsy
				.append($("<img/>").attr("src", listener_picture_url))
		)
		
	},
	
	// Check if a session is a friend of current user
	isFriend: function(session){
		var response = false;
		var that = this;
		for(var i=0, c=that.friends.length; i<c; i++){
			var friend = that.friends[i]
			if(session.listener_key_name == friend.id){
				response = true;
				break;
			}
		}
		return response;
	},
	
	// Remove the session gone if it's a friend who's listening
	remove: function(session){		
		var was_duplicate = false;

		if(this.isFriend(session)){
			// We gonna check first in the duplicate list
			var that = this;
			for(var i=0, c=that.duplicate_friend_sessions.length; i<c; i++){
				var duplicate_friend_session = that.duplicate_friend_sessions[i];
				if(duplicate_friend_session.key_name == session.key_name){
					that.duplicate_friend_sessions.splice(i,1);
					was_duplicate = true;
					break;
				}
			}

			// Then if it's not in the duplicate list, we look into the original list
			if(!was_duplicate){
				for(var i=0, c=that.friend_sessions.length; i<c; i++){
					var friend_session = that.friend_sessions[i];
					if(friend_session.key_name == session.key_name){
						// Remove from the friends list
						that.friend_sessions.splice(i,1);

						// Remove from the UI
						that.UIRemove(session)

						// Stop the loop
						break;
					}
				}
			}

			// If the same user was in the duplicate sessions list, we put it back in the sessions list
			for(var i=0, c=that.duplicate_friend_sessions.length; i<c; i++){
				var duplicate_friend_session = that.duplicate_friend_sessions[i];
				if(duplicate_friend_session.listener_key_name == session.listener_key_name){
					// We remove the sessions from the duplicates
					that.duplicate_friend_sessions.splice(i,1)

					// We put it into the friends list
					that.add(duplicate_friend_session);

					// Stop the loop
					break;
				}					
			}
		}
		
		if(this.sessions_counter){
			// Decrement sessions counter
			this.sessions_counter.decrement();
		}
	},
	
	UIRemove: function(session){
		var channel_id = session.key_name;
		
		// A little trick necessary for attributes that features a '.'
		var re = RegExp("[.]","g");
		var jquery_id = "#" + channel_id.replace(re, "\\.");
		$(jquery_id).remove();
	},
	
}