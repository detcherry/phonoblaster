// ---------------------------------------------------------------------------
// QUEUE MANAGER
// ---------------------------------------------------------------------------

QueueManager.prototype = new RealtimeTabManager();
QueueManager.prototype.constructor = QueueManager;

function QueueManager(station_client){
	RealtimeTabManager.call(this, station_client);
	
	// Settings
	this.url = "/api/queue"
	this.data_type = "json"
	
	// UI Settings
	this.name = "#queue-tab";
	this.selector = this.name + " .tab-items:nth-child(2)";
	
	// Additional attributes
	this.live_item = null;
	this.youtube_manager = new YoutubeManager();
	this.alert_manager = new AlertManager(station_client, "New broadcast!", "#queue-header");
	this.recommandation_manager = null;
	
	// Init Methods
	this.get();
	this.deleteListen();
}

//--------------------------------- GET -----------------------------------

QueueManager.prototype.noData = function(){
	// UI modifications
	$("#player-wrapper").empty();
	$("#player-wrapper").append($("<div/>").attr("id","no-live").html("No live track."));
	
	if(this.station_client.admin){
		// Open the recommandation manager
		this.recommandation_manager = new RecommandationManager(this.station_client)
	}
}

QueueManager.prototype.add = function(content){
	var that = this;
	var new_item = this.serverToLocalItem(content);
	
	if(this.live_item == null){
		this.live(new_item);
	}
	else{
		this.addToItems(new_item, function(previous_item){
			that.UIAdd(new_item, previous_item);
		})
	}
	
	//Update room
	this.updateRoom()
}

QueueManager.prototype.addToItems = function(new_item, callback){
	var that = this;
	var previous_items = this.items.slice(0); // Copy items
	var following_items = [];
	var previous_item = null;
	
	// If queue is empty, just add the new item to the queue
	if(this.items.length == 0){
		this.items.push(new_item);
	}
	else{
		// Browse the queue and insert the item at the right place
		for(var i=0, c=that.items.length; i<c; i++){
			var item = that.items.slice(0).reverse()[i] // Specific to the QueueManager

			// The new item has been created before (NOT OK)
			if(item.created > new_item.created){
				following_items.push(previous_items.shift())
			}
			// The new item has been created after (OK)
			else{
				previous_item = item;
				previous_items.push(new_item);
				break;
			}
		}
		this.items = previous_items.concat(following_items)
	}
	
	callback(previous_item);
}

QueueManager.prototype.UIAdd = function(new_item, previous_item){
	// If the item was initially displayed, we don't care (honey badger style) and remove it
	this.UIRemove(new_item.id);
	var new_item_div = this.UIBuild(new_item);		
	
	if(previous_item){
		// If there was a previous item, we insert the new item just before
		var re = RegExp("[.]","g");
		var previous_item_selector = this.selector + " #" + previous_item.id.replace(re, "\\.");
		this.UIInsert(new_item_div, previous_item_selector)
	}
	else{
		// Else, we have to append the item at the top of the column
		this.UIPrepend(new_item_div); // Specific to the QueueManager
	}
}

QueueManager.prototype.UIBuild = function(item){
	var id = item.id;
	var content = item.content;
	var type = content.type;
	
	var youtube_id = content.youtube_id;
	var youtube_title = content.youtube_title;
	var youtube_duration = PHB.convertDuration(content.youtube_duration)
	var youtube_thumbnail = "http://i.ytimg.com/vi/" + youtube_id + "/default.jpg";
	
	var track_submitter_name = content.track_submitter_name;
	var track_submitter_url = content.track_submitter_url;
	var track_submitter_picture = "https://graph.facebook.com/" + content.track_submitter_key_name + "/picture?type=square";	
	
	var mention = null;
	if(type == "suggestion"){
		mention = "Suggested by"
	}
	if(type == "favorite"){
		mention = "Rebroadcast of"
	}
	
	var div = $("<div/>").addClass("item").attr("id", id)
	
	div.append(
		$("<span/>")
			.addClass("square")
			.append(
				$("<img/>")
					.attr("src", youtube_thumbnail)
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

	if(this.station_client.admin){
		div.append(
			$("<a/>")
				.attr("href","#")
				.addClass("cross")
				.attr("name", id)
				.html("X")
		)
	}

	div.append(
		$("<div/>")
			.addClass("subtitle")
			.append(
				$("<div/>")
					.addClass("duration")
					.html(youtube_duration)
			)
	)

	if(mention){
		var subtitle = div.find(".subtitle")
		subtitle.append(
			$("<div/>")
				.addClass("submitter")
				.append(
					$("<img/>")
						.attr("src", track_submitter_picture)
						.addClass("station")
						.addClass("tuto")
						.attr("data-original-title", track_submitter_name)
				)
				.append(
					$("<span/>")
						.html(mention)
				)
		)
	}

	return div
}

QueueManager.prototype.UIInsert = function(new_item_div, previous_item_selector){	
	new_item_div.insertAfter(previous_item_selector); // Specific to the QueueManager
}

//--------------------------------- LIVE -----------------------------------

QueueManager.prototype.live = function(new_item){	
	this.live_item = new_item;
 	var content = new_item.content;
	
	var id = this.live_item.id
	var expired_at = parseInt(content.expired,10);
	var duration = parseInt(content.youtube_duration,10);
	var youtube_id = content.youtube_id;
	var now = PHB.now()

	var time_out = expired_at - now;
	var video_start = duration - time_out;

	// Check if the broadcast is not currently being played before initializing the youtube manager
	var ui_live_id = this.UILive();
	if(ui_live_id != id){
		this.youtube_manager.init(youtube_id, video_start);
	}

	// Remove the display in the queue
	this.UIRemove(id);
	
	// Display the live broadcast in the UI
	this.UILiveSet(this.live_item);
	
	// Display the progress of the video
	this.UIProgress(video_start, duration);
	
	// Program the launch of the next video
	this.nextVideo(time_out);
	
	// Increment the number of views on the server
	this.postView();
	
	// Post action to FACEBOOK
	this.postAction(this.live_item);
}

QueueManager.prototype.nextVideo = function(time_out){
	var that = this;
	
	setTimeout(function(){			
		// Live is over
		that.liveOver();
		
		// Get next item and put it live
		var new_item = that.items.shift();
		if(new_item){
			that.live(new_item)
		}
		else{
			// If user admin, display recommandations to broadcast
			if(that.station_client.admin){
				if(that.recommandation_manager){
					that.recommandation_manager.dispatch();
				}
				else{
					that.recommandation_manager = new RecommandationManager(that.station_client)
				}
			}
		}	
		
	}, time_out * 1000)
}

QueueManager.prototype.liveOver = function(){
	// Display past broadcast in the comments zone
	var fake_comment = this.live_item.content;
	fake_comment.created = PHB.now();
	this.station_client.comment_manager.add(fake_comment)
	
	// Reset live item
	this.live_item = null;
	
	// Remove the broadcast from the live UI
	this.UILiveRemove();
	
	// Update the room
	this.updateRoom();
}

QueueManager.prototype.postView = function(){
	var shortname = this.station_client.station.shortname
	
	$.ajax({
		url: "/api/views",
		type: "POST", 
		dataType: "json",
		timeout: 60000,
		data: {
			shortname: shortname,
		},
		error: function(xhr, status, error) {
			PHB.log('An error occurred: ' + error + '\nPlease retry.');
		},
		success: function(){
			// The view has been added
		},
	});
	
}

QueueManager.prototype.UIProgress = function(video_start, duration){
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
	
}

QueueManager.prototype.postAction = function(item){	
	if(this.station_client.user){
		var broadcast_url = PHB.site_url + "/broadcast/" + item.id;
		
		var obj = { "live": broadcast_url };
		var extra = {};
		var expires_in = item.content.youtube_duration;
		
		if(this.station_client.admin){
			// BROADCAST action
			var action = "broadcast";
		}
		else{
			// ATTEND action
			var action = "attend";
		}
		
		FACEBOOK.putAction(action, obj, extra, expires_in);
	}
}


//----------------------------- QUEUE STATUS -------------------------------

QueueManager.prototype.updateRoom = function(){
	var number_of_items = this.items.length;
	if(this.live_item){
		number_of_items++
	}
	
	var room = 10 - number_of_items;
	this.UISetRoom(room);
}

QueueManager.prototype.UIRoom = function(){
	var queue_room = $("#queue-status .grey").length
	return queue_room
}

QueueManager.prototype.UIIncrementRoom = function(){
	var queue_room = this.UIRoom();
	queue_room++;
	this.UISetRoom(queue_room);
}

QueueManager.prototype.UIDecrementRoom = function(){
	var queue_room = this.UIRoom();
	queue_room--;
	this.UISetRoom(queue_room);
}

QueueManager.prototype.UISetRoom = function(new_room){
	var number_of_items = 10 - new_room;
	
	$("#queue-status .circle").each(function(index, element){
		if(index < number_of_items){
			$(this).removeClass("grey").addClass("black")
		}
		else{
			$(this).removeClass("black").addClass("grey")
		}
	})	
	
	$("#queue-counter span").html(number_of_items)
}

//------------------------------- POST -------------------------------------

// Before a track is submitted, we finish building it
QueueManager.prototype.prePostBuild = function(item){
	var channel_id = this.station_client.channel_id;
	var created = PHB.now();

	content = item.content;
	content["key_name"] = channel_id + ".queued." + created + Math.floor(Math.random()*100).toString();
	content["expired"] = null;
	content["created"] = null;
	
	var new_item = this.serverToLocalItem(content)
	
	return new_item
}

// Submit an item to the queue (Broadcast a track)
QueueManager.prototype.postSubmit = function(btn, incoming_item){
	var ui_room = this.UIRoom()
	if(ui_room > 0){			
		// Format the Track item into a Broadcast item
		var new_item = this.prePostBuild(incoming_item);
		
		// Display "queued" message
		this.UISuccess(btn);
		
		var ui_live_id = this.UILive();
		if(ui_live_id != ""){
			// Append the new item locally
			var new_item_div = this.UIBuild(new_item)
			this.UIAppend(new_item_div);
		}
		else{
			// Put it live if there was no item before
			this.UILiveSet(new_item);
			this.youtube_manager.init(new_item.content.youtube_id, 0);
		}
		
		this.UIDecrementRoom();

		// POST request to the server
		var that = this;
		this.post(new_item, function(response){
			that.postCallback(new_item, response);
		});
	}
	else{
		this.UIFail(btn)
	}
}

QueueManager.prototype.unPostEvent = function(){
	this.UIIncrementRoom(); // Specific to QueueManager
}

QueueManager.prototype.UISuccess = function(btn){
	btn.addClass("success")
	btn.html("Queued")
	
	setTimeout(function(){
		btn.removeClass("success")
		btn.html("Queue")
	}, 2000)
}

QueueManager.prototype.UIFail = function(btn){
	btn.addClass("danger")
	btn.html("Full")
	
	setTimeout(function(){
		btn.removeClass("danger")
		btn.html("Queue")
	}, 2000)
},

// Returns the current live item 
QueueManager.prototype.UILive = function(){
	var item_id = $("#video-details .id").html();
	return item_id;
}

// Set the live item in the UI
QueueManager.prototype.UILiveSet = function(item){
	this.UILiveRemove();
	
	var id = item.id;
	var content = item.content;
	var type = content.type;
	
	var youtube_title = content.youtube_title;
	var youtube_duration = PHB.convertDuration(content.youtube_duration);
	var youtube_thumbnail = "http://i.ytimg.com/vi/" + content.youtube_id + "/default.jpg";
	
	var track_submitter_name = content.track_submitter_name;
	var track_submitter_url = content.track_submitter_url;
	var track_submitter_picture = "https://graph.facebook.com/" + content.track_submitter_key_name + "/picture?type=square";
	
	// Display the image
	$("#video-details span.clip").append($("<img/>").attr("src", youtube_thumbnail));
	
	// Display the title
	$("#video-details span.middle").html(youtube_title);
	
	// Put the item id in the div
	$("#video-details .id").html(id);
	
	var mention = null;
	if(type == "suggestion"){
		mention = "Suggested by"
	}
	if(type == "favorite"){
		mention = "Rebroadcast of"
	}
	
	if(mention){
		// Display the submitter
		$("#video-details .submitter")
			.append(
				$("<img/>")
					.attr("src", track_submitter_picture)
					.addClass("tuto") // Twipsy
					.attr("data-original-title", track_submitter_name)
			)
			.append($("<span/>").html(mention))
	}
	
	if(content.track_id && this.station_client.user){
		// Favorite button
		$("#favorite-track").append(
			$("<a/>")
				.attr("href", "#")
				.addClass("fav")
				.addClass("tuto") // Twipsy
				.attr("data-original-title", "Favorite this track") // Twipsy
		)
	}
	
	$("#station-status span.btn").addClass("danger").html("On air")
}

QueueManager.prototype.UILiveRemove = function(){
	// Remove image
	$("#video-details span.clip").empty();
	
	// Remove title
	$("#video-details span.middle").html("No track is being broadcast");
	
	// Remove the broadcast key_name in the div
	$("#video-details .id").empty();
	
	// Remove the favorite icon
	$("#favorite-track").empty();
	
	// Remove the submitter
	$("#video-details .submitter").empty();
	
	$("#station-status span.btn").removeClass("danger").html("Off air")
}

// -------------------------------- NEW --------------------------------------

QueueManager.prototype.newEvent = function(){
	// Increment the broadcasts counter
	this.station_client.broadcasts_counter.increment();
	
	// Alert
	this.alert_manager.alert();
}

//------------------------------- REMOVE -------------------------------------

QueueManager.prototype.remove = function(id){
	var new_items = []
	var that = this
	for(var i=0, c =that.items.length; i<c; i++){
		var item = that.items[i];
		if(item.id == id){
			// Expiration of broadcasts after the broadcast to remove should occur earlier
			var offset = parseInt(item.content.youtube_duration, 10);
			
			// Edit all the broadcasts after the broadcast to remove
			for(j=i, d=that.items.length; j<d; j++){
				that.items[j].content.expired = parseInt(that.items[j].content.expired, 10) - offset;
			}
			
			// Remove the targeted broadcast
			that.items.splice(i,1);
			
			// Remove the broadcast from the UI
			that.UIRemove(id);
			
			// Event callback
			that.removeEvent();
			
			break;
		}
	}
}

QueueManager.prototype.removeEvent = function(){
	// Update the room
	this.updateRoom();
	
	// Decrement the broadcasts counter
	this.station_client.broadcasts_counter.decrement();
}