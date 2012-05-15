// ---------------------------------------------------------------------------
// SESSION MANAGER
// ---------------------------------------------------------------------------

function SessionManager(station_client){
	this.station_client = station_client;
	
	this.sessions_counter = null;
	
	this.sessions = [];
	this.duplicate_sessions = []
	
	this.init();
}


SessionManager.prototype = {
	
	// Fetch sessions
	init: function(){
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
				$("#sessions span.figure").html(that.sessions.length);
				that.sessions_counter = new Counter("#sessions");

				if(json.sessions){
					var sessions = json.sessions;
					
					// Add each new friend session to the DOM
					$.each(sessions, function(index, value){
						var session = value;
						that.add(session);
					})	
				}

				that.sessions_counter.setCount(that.sessions.length);
			},
		});
	},
	
	// Incoming sessions received from PubNub
	new: function(new_session){
		this.add(new_session);
		
		// Increment sessions counter
		if(this.sessions_counter){
			this.sessions_counter.setCount(this.sessions.length);
		}
	},
	
	// Process incoming logged in sessions
	add: function(new_session){
		var that = this;
		
		// Check if the new listener is not already listening
		var duplicate = false;
		if(new_session.listener_key_name){
			for(var i=0, c=that.sessions.length; i<c; i++){
				var session = that.sessions[i];
				if(session.listener_key_name == new_session.listener_key_name){
					duplicate = true;
					break;
				}
			}
		}
		
		if(duplicate){
			// Add session to the duplicate list
			this.duplicate_sessions.push(new_session);

		}
		else{
			// Add session to the list, first are the logged users then the unknown users.
			if(new_session.listener_key_name){
				this.sessions.unshift(new_session);
			}else{
				this.sessions.push(new_session);
			}

			// Add session to the UI
			this.UIAdd(new_session);
		}
	},
	
	UIAdd: function(session){
		var channel_id = session.key_name;
		
		
		if(session.listener_key_name){
			var listener_picture_url = "https://graph.facebook.com/"+ session.listener_key_name + "/picture?type=square";
			var listener_name = session.listener_name;
			var listener_url = session.listener_url;
			$("#listeners").prepend(
			$("<a/>")
				.attr("id", channel_id)
				.attr("href", listener_url)
				.addClass("tuto") // Twipsy
				.addClass("listener")
				.attr("data-original-title", listener_name) // Twipsy
				.append($("<img/>").attr("src", listener_picture_url))
			);
		}else{
			var listener_picture_url = "/static/images/unknown.png";
			var listener_name = "Unknown";
			$("#listeners").append(
			$("<a/>")
				.attr("id", channel_id)
				.addClass("tuto") // Twipsy
				.addClass("listener")
				.attr("data-original-title", listener_name) // Twipsy
				.append($("<img/>").attr("src", listener_picture_url))
			)
		}
		
	},
	
	// Session left
	remove: function(session_gone){
		this.delete(session_gone);
		
		if(this.sessions_counter){
			this.sessions_counter.setCount(this.sessions.length);
		}
	},
	
	delete: function(session_gone){
		// We gonna check first in the duplicate list
		var that = this;
		var was_duplicate = false;
		for(var i=0, c=that.duplicate_sessions.length; i<c; i++){
			var duplicate_session = that.duplicate_sessions[i];
			if(duplicate_session.key_name == session_gone.key_name){
				that.duplicate_sessions.splice(i,1);
				was_duplicate = true;
				break;
			}
		}

		// Then if it's not in the duplicate list, we look into the original list
		if(!was_duplicate){
			for(var i=0, c=that.sessions.length; i<c; i++){
				var session = that.sessions[i];
				if(session.key_name == session_gone.key_name){
					// Remove from the sessions list
					that.sessions.splice(i,1);

					// Remove from the UI
					that.UIRemove(session_gone)

					// Stop the loop
					break;
				}
			}
		}

		// If the same user was in the duplicate sessions list, we put it back in the sessions list
		for(var i=0, c=that.duplicate_sessions.length; i<c; i++){
			var duplicate_session = that.duplicate_sessions[i];
			if(duplicate_session.listener_key_name == session_gone.listener_key_name){
				// We remove the session from the duplicates
				that.duplicate_sessions.splice(i,1)

				// We put it into the main list
				that.add(duplicate_session);

				// Increment sessions counter
				if(this.sessions_counter){
					this.sessions_counter.setCount(this.sessions.length);
				}

				// Stop the loop
				break;
			}					
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