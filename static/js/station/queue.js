// ---------------------------------------------------------------------------
// QUEUE MANAGER
// ---------------------------------------------------------------------------

function QueueManager(station_client){
	this.station_client = station_client;
	
	// Overwrites the default tab values
	this.name = "#queue-tab";
	this.url = "/api/queue";
	this.datatype = "json";
	
	// Additional attribute
	this.live_broadcast = null;
	this.queue = [];
	this.youtube_manager = new YoutubeManager();
	
	this.get();
}

QueueManager.prototype = {
	
	room: function(){
		var response = true;
		var room = this.queue.length;
		if(this.live_broadcast){
			room++
		}
		if(room > 9){
			response = false;
		}
		return response;
	},
	
	// Submit a track to the queue (Broadcast a track)
	submit: function(btn, track){
		var room = this.room()
		if(room){			
			var new_broadcast = this.prePostBuild(track);
			
			// Display "queued" message
			this.UISubmit(btn);
			
			// Append the track locally
			this.UIAppend(new_broadcast);

			// POST request to the server
			var that = this;
			this.post(new_broadcast, function(response){
				that.postCallback(new_broadcast, btn, response);
			});
		}
		else{
			this.UIFull(btn)
		}
	},
	
	// If room in the queue, display queued 
	UISubmit: function(btn){
		btn.addClass("success")
		btn.html("Queued")
	},
	
	// If no room in the queue, display full
	UIFull: function(btn){
		btn.addClass("danger")
		btn.html("Full")
		
		setTimeout(function(){
			btn.removeClass("danger")
			btn.html("Queue")
		}, 2000)
	},
	
	// Once the track has been submitted, we display an error message or nothing
	postCallback: function(broadcast, btn, response){
		if(!response){
			this.UIRemove(broadcast)
			PHB.error("New broadcast has not been published")
		}
		
		this.UISubmitCallback(btn)
	},
	
	// Once the submit action is completed, display the initial message
	UISubmitCallback: function(btn){
		btn.removeClass("success")
		btn.html("Queue")
	},
	
	// Before a track is submitted, we finish building it
	prePostBuild: function(track){
		var channel_id = this.station_client.channel_id;
		var created = PHB.now();

		new_broadcast = track;
		new_broadcast["broadcast_key_name"] = channel_id + ".queued." + created;
		new_broadcast["broadcast_expired"] = null;

		return new_broadcast
	},
	
	// Wrapper above UIQueueAppend and UILiveBroadcastSet
	UIAppend: function(new_broadcast){
		var ui_live_broadcast = this.UILiveBroadcast();
		if(ui_live_broadcast != ""){
			this.UIQueueAppend(new_broadcast);
		}
		else{
			this.UILiveBroadcastSet(new_broadcast);
			this.youtube_manager.init(new_broadcast.youtube_id, 0);
		}
	},
	
	// Return the current live broadcast in the UI
	UILiveBroadcast: function(){
		var broadcast_key_name = $("#live-broadcast .key_name").html();
		return broadcast_key_name;
	},
	
	// Append a broadcast to the queue tab
	UIQueueAppend: function(new_broadcast){
		var ui_live_broadcast = this.UILiveBroadcast();
		// Display the new broadcast in the queue only if it's not the current live broadcast!
		if(ui_live_broadcast != new_broadcast.broadcast_key_name){
			var tab_selector = this.name + " .tab-items";

			// Reset the tab in case it contained some init content
			var init_selector = tab_selector + " .init";
			$(init_selector).remove();

			var that = this;
			this.UIBuild(new_broadcast, function(new_broadcast_jquery_object){
				$(tab_selector).append(new_broadcast_jquery_object);
			})
		}
	},
	
	// Put broadcast at the bottom of the video
	UILiveBroadcastSet: function(new_broadcast){
		var track_thumbnail = "http://i.ytimg.com/vi/" + new_broadcast.youtube_id + "/default.jpg"
		
		// Display the image
		$("#live-broadcast span.clip").append($("<img/>").attr("src", track_thumbnail));
		
		// Display the title
		$("#live-broadcast span.middle").html(new_broadcast.youtube_title);
		
		// Put the broadcast key_name in the div
		$("#live-broadcast .key_name").html(new_broadcast.broadcast_key_name);
	},
	
	// Empty UI broadcast at the bottom of the video
	UILiveBroadcastRemove : function(){
		// Remove image
		$("#live-broadcast span.clip").empty();
		
		// Remove title
		$("#live-broadcast span.middle").html("No track is being broadcast");
		
		// Remove the braodcast key_name in the div
		$("#live-broadcast .key_name").empty();
	},
	
	// Build the div representing a broadcast
	UIBuild: function(new_broadcast, callback){
		var track_submitter_picture_url = "https://graph.facebook.com/" + new_broadcast.track_submitter_key_name + "/picture?type=square";
		var track_thumbnail = "http://i.ytimg.com/vi/" + new_broadcast.youtube_id + "/default.jpg"
		
		if(this.station_client.station.key_name == new_broadcast.track_submitter_key_name){
			if(new_broadcast.track_admin){
				var mention = "Added by"
			}
			else{
				var mention = "Suggested by"
			}
		}
		else{
			var mention = "Rebroadcast of"
		}


		callback(
			$("<div/>")
				.addClass("track")
				.attr("id", new_broadcast.broadcast_key_name)
				.append($("<span/>").addClass("square").append($("<img/>").attr("src", track_thumbnail)))
				.append(
					$("<div/>")
						.addClass("title")
						.append($("<span/>").addClass("middle").html(new_broadcast.youtube_title))
				)
				.append($("<a/>").attr("href","#").addClass("cross").html("X"))
				.append(
					$("<div/>")
						.addClass("subtitle")
						.append($("<div/>").addClass("duration").html(PHB.convertDuration(new_broadcast.youtube_duration)))
						.append(
							$("<div/>")
								.addClass("submitter")
								.append($("<img/>").attr("src", track_submitter_picture_url).addClass("station"))
								.append($("<span/>").html(mention))
						)
				)
		)
	},
	
	// POST the new broadcast to the server
	post: function(new_broadcast, callback){
		var shortname = this.station_client.station.shortname
		var that = this;

		$.ajax({
			url: that.url,
			type: "POST",
			dataType: that.datatype,
			timeout: 60000,
			data: {
				shortname: shortname,
				broadcast: JSON.stringify(new_broadcast)
			},
			error: function(xhr, status, error) {
				callback(false)
			},
			success: function(json){
				callback(json.response);
			},
		});		
	},
	
	// Incoming broadcast received via PUBNUB or Initialization
	add: function(new_broadcast){
		var that = this;
		
		var following_broadcasts = that.queue.slice(0); // Copy the queue
		var previous_broadcasts = [];
		var following_broadcast = null;
		
		// If queue is empty, just add the new long broadcast to the queue
		if(this.queue.length == 0){
			this.queue.push(new_broadcast)
		}
		else{
			// Browse the broadcasts list and insert the broadcast at the right place
			for(var i=0, c=that.queue.length; i<c; i++){
				var broadcast = that.queue[i];
				
				// The new broadcast expires after (OK)
				if(broadcast.broadcast_expired < new_broadcast.broadcast_expired){
					previous_broadcasts.push(following_broadcasts.shift());	
				}
				// The new broadcast expires before (NOT OK)
				else{
					following_broadcast = broadcast;
					break;
				}
			}
			previous_broadcasts.push(new_broadcast);
			this.queue = previous_broadcasts.concat(following_broadcasts);
		}
		
		// Insert new broadcast in the queue
		this.UIAdd(new_broadcast, following_broadcast);
		
		// Update the room
		this.UIUpdateRoom();
	},
	
	UIAdd: function(new_broadcast, following_broadcast){
		// If the broadcast was initially displayed, we remove it (honey badger style)
		this.UIRemove(new_broadcast);
		
		if(following_broadcast){
			// If there is a following broadcast, we insert the new broadcast just before
			var re = RegExp("[.]","g");
			var following_broadcast_selector = "#queue-tab #" + following_broadcast.broacast_key_name.replace(re, "\\.");
			this.UIInsert(new_broadcast, following_broadcast_selector)
		}
		else{
			// Else, we have to append the broadcast at the bottom
			this.UIQueueAppend(new_broadcast)
		}
	},
	
	UIRemove: function(broadcast){
		var re = RegExp("[.]","g");
		var broadcast_selector = "#queue-tab #" + broadcast.broadcast_key_name.replace(re, "\\.");
		$(broadcast_selector).remove();
	},
	
	UIInsert: function(new_broadcast, following_broadcast_selector){
		this.UIBuild(new_broadcast, function(new_broadcast_jquery_object){
			// Insert new comment div just before the previous comment div
			new_broadcast_jquery_object.insertBefore(following_broadcast_selector);
		})
	},
	
	// Get all the broadcasts in the station queue
	get: function(){
		var that = this;	
		var shortname = this.station_client.station.shortname;
		// Fetch station comments
		$.ajax({
			url: "/api/queue",
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
				queue = json;
				
				// Add each comment to the DOM
				$.each(queue, function(index, value){
					var new_broadcast = value;
					that.add(new_broadcast);
				})
				
				that.playNext();
				
			},
		});
	},
	
	playNext: function(){
		this.live_broadcast = this.queue.shift();
		var time_out = 2
		if(this.live_broadcast){		
			var expired_at = parseInt(this.live_broadcast.broadcast_expired,10);
			var duration = parseInt(this.live_broadcast.youtube_duration,10);

			var time_out = expired_at - PHB.now();
			var video_start = duration - time_out;
			
			// Check if the broadcast is not currently being played before initializing the youtube manager
			var existing_ui_live_broadcast = this.UILiveBroadcast();
			if(existing_ui_live_broadcast != this.live_broadcast.broadcast_key_name){
				this.youtube_manager.init(this.live_broadcast.youtube_id, video_start);
			}
			
			// Remove the display in the queue
			this.UIRemove(this.live_broadcast);
			
			// Display the live broadcast in the UI
			this.UILiveBroadcastSet(this.live_broadcast);
			
			// Display the progress of the video
			this.UIProgress(video_start, duration);
			
			// Display the current broadcast in the comments zone
			this.station_client.comment_manager.UINewBroadcast(this.live_broadcast);
		}
		this.nextVideo(time_out);
	},
	
	nextVideo: function(time_out){		
		var that = this;
		setTimeout(function(){
			if(that.live_broadcast){
				that.live_broadcast = null;
				that.UILiveBroadcastRemove();
			}
			
			that.UIUpdateRoom();
			that.playNext();
		}, time_out * 1000)
	},
	
	UIProgress: function(video_start, duration){		
		var x = parseInt(video_start*400/duration);
		$('#filler').css('width', x.toString() + 'px');
		
		$("#filler").clearQueue();
		$('#filler').animate({
			width:'400px',
		}, (duration - video_start)*1000,'linear');
		
		var that = this;
		var time_out = duration - video_start;
		var elapsed = video_start;
		
		// Update a time counter
		var time_counter = setInterval(function(){
			time_out--;
			elapsed++;
			
			$("#counter-left").html(PHB.convertDuration(elapsed));
			$("#counter-right").html("-" + PHB.convertDuration(time_out));
			
		}, 1000);
		
		// Remove time counter once the broadcast is over
		setTimeout(function(){
			clearInterval(time_counter)
			$("#counter-left").html("0:00");
			$("#counter-right").html("-0:00");
		}, (duration - video_start)*1000);
	},
	
	UIUpdateRoom: function(){
		var number_of_broadcasts = this.queue.length;
		if(this.live_broadcast){
			number_of_broadcasts++
		}
		
		$("#queue-status .circle").each(function(index, element){
			if(index < number_of_broadcasts){
				$(this).removeClass("grey").addClass("black")
			}
			else{
				$(this).removeClass("black").addClass("grey")
			}
		})
		$("#queue-counter span").html(number_of_broadcasts)
	},
	
}
	


