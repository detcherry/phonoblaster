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
	
	this.init();
}

QueueManager.prototype = {
	
	init: function(){
		// GET the queue from the server
		this.get();
		
		// Listen to delete broadcast events
		this.deleteListen();
	},
	
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
	postSubmit: function(btn, track){
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
		new_broadcast["broadcast_key_name"] = channel_id + ".queued." + created + Math.floor(Math.random()*10).toString();
		new_broadcast["broadcast_expired"] = null;
		new_broadcast["broadcast_created"] = PHB.now();

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
		// Display the new broadcast in the queue only if it's not the current live broadcast!
		var tab_selector = this.name + " .tab-items:nth-child(2)";

		// Reset the tab in case it contained some init content
		var init_selector = tab_selector + " .init";
		$(init_selector).remove();

		var that = this;
		this.UIBuild(new_broadcast, function(new_broadcast_jquery_object){
			$(tab_selector).append(new_broadcast_jquery_object);
		})
	},
	
	// Set the broadcast live in the UI
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
		
		var broadcast_div = $("<div/>")
			.addClass("track")
			.attr("id", new_broadcast.broadcast_key_name)
			.append($("<span/>").addClass("square").append($("<img/>").attr("src", track_thumbnail)))
			.append(
				$("<div/>")
					.addClass("title")
					.append($("<span/>").addClass("middle").html(new_broadcast.youtube_title))
			)
		
		if(this.station_client.admin){
			broadcast_div.append($("<a/>").attr("href","#").addClass("cross").html("X"))
		}
		
		broadcast_div.append(
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
		
		callback(broadcast_div);
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
				broadcast: JSON.stringify(new_broadcast),
				method: "POST",
			},
			error: function(xhr, status, error) {
				callback(false)
			},
			success: function(json){
				callback(json.response);
			},
		});		
	},

	// New broadcast from PUBNUB
	new: function(new_broadcast){
		// Increment the broadcasts counter
		this.station_client.broadcasts_counter.increment();
		
		// Add new broadcast to queue
		this.add(new_broadcast);
	},

	// Controller for new broadcast (Modify the Queue, modify the UI)
	add: function(new_broadcast){
		var that = this;
		
		var previous_broadcasts = this.queue.slice(0);
		var following_broadcasts = [];
		var previous_broadcast = null;
		
		if(this.live_broadcast == null){
			// Launch the video
			that.live(new_broadcast);
		}
		else{
			// If queue is empty, just add the new broadcast to the queue
			if(this.queue.length == 0){
				this.queue.push(new_broadcast);
			}
			else{
				// Browse the broadcasts list and insert the broadcast at the right place
				for(var i=0, c=that.queue.length; i<c; i++){
					var broadcast = that.queue.slice(0).reverse()[i]

					// The new broadcast expires before (NOT OK)
					if(broadcast.broadcast_expired > new_broadcast.broadcast_expired){
						following_broadcasts.push(previous_broadcasts.shift())
					}
					// The new broadcast expires after (OK)
					else{
						previous_broadcast = broadcast;
						previous_broadcasts.push(new_broadcast);
						break;
					}
				}
				this.queue = previous_broadcasts.concat(following_broadcasts)
			}

			// Insert new broadcast in the queue
			this.UIAdd(new_broadcast, previous_broadcast);
		}

		// Update the room
		this.UIUpdateRoom();
		
	},		
	
	UIAdd: function(new_broadcast, previous_broadcast){
		// If the broadcast was initially displayed, we remove it (honey badger style)
		this.UIRemove(new_broadcast);
		
		if(previous_broadcast){
			// If there is a previous broadcast, we insert the new broadcast just after
			var re = RegExp("[.]","g");
			var previous_broadcast_selector = "#queue-tab .tab-items #" + previous_broadcast.broadcast_key_name.replace(re, "\\.");
			this.UIInsert(new_broadcast, previous_broadcast_selector)
		}
		else{
			// Else, we have to append the broadcast at the bottom
			this.UIQueuePrepend(new_broadcast);
		}
		
	},
	
	UIInsert: function(new_broadcast, previous_broadcast_selector){
		this.UIBuild(new_broadcast, function(new_broadcast_jquery_object){
			// Insert new comment div just before the previous comment div
			new_broadcast_jquery_object.insertAfter(previous_broadcast_selector);
		})
	},
	
	UIQueuePrepend: function(new_broadcast){
		var tab_selector = this.name + " .tab-items:nth-child(2)";

		// Reset the tab in case it contained some init content
		var init_selector = tab_selector + " .init";
		$(init_selector).remove();

		var that = this;
		this.UIBuild(new_broadcast, function(new_broadcast_jquery_object){
			$(tab_selector).prepend(new_broadcast_jquery_object);
		})
	},
	
	UIRemove: function(broadcast){
		var re = RegExp("[.]","g");
		var broadcast_selector = "#queue-tab .tab-items #" + broadcast.broadcast_key_name.replace(re, "\\.");
		$(broadcast_selector).remove();
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
								
			},
		});
	},
	
	// Put a broadcast live
	live: function(new_broadcast){
		this.live_broadcast = new_broadcast;
		
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
		var live_comment = {
			"key_name": this.live_broadcast.broadcast_key_name,
			"created": this.live_broadcast.broadcast_created,
			"broadcast": this.live_broadcast,
		}
		this.station_client.comment_manager.add(live_comment)
		
		// Program the launch of the next video
		this.nextVideo(time_out);
	},
	
	nextVideo: function(time_out){		
		var that = this;
		
		setTimeout(function(){
			// Reset live broadcast
			that.live_broadcast = null;
			
			// Remove the broadcast from the live UI
			that.UILiveBroadcastRemove();
			
			// Update the room in the UI
			that.UIUpdateRoom();
			
			// Get next broadcast and put it live
			new_broadcast = that.queue.shift();
			if(new_broadcast){
				that.live(new_broadcast)
			}
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
	
	// On the upper left, update the number of circles that represents the broadcasts in the queue
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
	
	deleteListen: function(){
		var that = this;
		$(".track a.cross").live("click", function(){
			var broadcast_to_delete_key_name = $(this).parent().attr("id");
			
			var broadcast_to_delete = null;
			for(var i=0, c= that.queue.length; i<c; i++){
				var broadcast = that.queue[i];
				if(broadcast.broadcast_key_name == broadcast_to_delete_key_name){
					broadcast_to_delete = broadcast;
					break;
				}
			}
			
			// We check if the broadcast is in the queue (cause sometimes it has not been received from pubnub yet...)
			if(broadcast_to_delete){
				that.deleteSubmit(broadcast_to_delete);
			}
			
			return false;
		})
		
	},
	
	deleteSubmit: function(broadcast_to_delete){
		//Hide the broadcast
		this.UIHide(broadcast_to_delete);
		
		var that = this;
		this.delete(broadcast_to_delete, function(response){
			that.deleteCallback(broadcast_to_delete, response)
		})
	},
	
	delete: function(broadcast_to_delete, callback){	
		var shortname = this.station_client.station.shortname
		var that = this;

		$.ajax({
			url: that.url,
			type: "POST", // I use the POST method because no request body can be sent with DELETE
			dataType: that.datatype,
			timeout: 60000,
			data: {
				shortname: shortname,
				broadcast: JSON.stringify(broadcast_to_delete),
				method: "DELETE"
			},
			error: function(xhr, status, error) {
				callback(false);
			},
			success: function(json){
				callback(json.response);
			},
		});
	},
	
	deleteCallback: function(broadcast_to_delete, response){
		if(response){
			this.UIRemove(broadcast_to_delete);
			PHB.log("Broadcast has been deleted from the server")
		}
		else{
			this.UIUnHide(broadcast_to_delete);
			PHB.error("Broadcast hasn't been deleted.")
		}
	},
	
	UIHide: function(broadcast_to_delete){
		var re = RegExp("[.]","g");
		var broadcast_selector = "#queue-tab .tab-items #" + broadcast_to_delete.broadcast_key_name.replace(re, "\\.");
		$(broadcast_selector).hide();
	},
	
	UIUnHide: function(broadcast_to_delete){
		var re = RegExp("[.]","g");
		var broadcast_selector = "#queue-tab .tab-items #" + broadcast_to_delete.broadcast_key_name.replace(re, "\\.");
		$(broadcast_selector).show();
	},
	
	// Broadcast to remove from PubNub
	remove: function(broadcast_to_remove){
		var new_queue = []
		var that = this
		for(var i=0, c =that.queue.length; i<c; i++){
			var broadcast = that.queue[i];
			if(broadcast.broadcast_key_name == broadcast_to_remove.broadcast_key_name){
				// Expiration of broadcasts after the broadcast to remove should occur earlier
				var offset = parseInt(broadcast.youtube_duration, 10);
				
				// Edit all the broadcasts after the broadcast to remove
				for(j=i, d=that.queue.length; j<d; j++){
					that.queue[j].broadcast_expired = parseInt(that.queue[j].broadcast_expired, 10) - offset;
				}
				
				// Remove the targeted broadcast
				that.queue.splice(i,1);
				
				// Remove the broadcast from the UI
				that.UIRemove(broadcast_to_remove);
				
				// Update the room
				that.UIUpdateRoom();
				
				// Decrement the broadcasts counter
				that.station_client.broadcasts_counter.decrement();
				
				break;
			}
		}
		
	},
	
}
	


