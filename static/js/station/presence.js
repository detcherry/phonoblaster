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
	
	this.friends = [];
	this.init();
}

PresenceManager.prototype = {
	
	init: function(){
		var that = this;
		// First fetch friends
		this.fetchFriends(function(){
			// Then fetch presences
			that.fetchPresences();
		});
	},
	
	// Fetch the user friends (works only for authenticated users)
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
	
	// Incoming presences
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
			if(existing_presence.listener_key_name == new_presence.listener_key_name){
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
			var listener_picture_url = "https://graph.facebook.com/"+ new_presence.listener_key_name + "/picture?type=square";
			var listener_name = new_presence.listener_name;
			var listener_url = new_presence.listener_url;
			
			// Append div to DOM
			outer_div.append(
				$("<div/>")
					.addClass("row")
					.addClass("presence")
					.attr("id",channel_id)
					.append(
						$("<a/>")
							.attr("href", listener_url)
							.append($("<img/>").attr("src", listener_picture_url))
							.append(
								$("<div/>")
									.addClass("title")
									.append(
										$("<span/>")
											.addClass("middle")
											.html(listener_name)
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
					if(duplicate_presence.listener_key_name == presence_gone.listener_key_name){
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
		
		existing_presences = this.admins_presences.concat(
			this.friends_presences,
			this.authenticated_presences,
			this.unauthenticated_presences
		);
		
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
		if(presence.listener_key_name){
			response = true;
		}
		return response
	},
	
	// Check if a presence is an admin user
	isAdmin: function(presence){
		return presence.admin;
	},
	
	// Check if a presence is a friend of current user
	isFriend: function(presence){
		var response = false;
		var that = this;
		for(i=0, c=that.friends.length; i<c; i++){
			var friend = that.friends[i]
			if(presence.listener_key_name == friend.id){
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