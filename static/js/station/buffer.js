// ---------------------------------------------------------------------------
// BUFFER MANAGER
// ---------------------------------------------------------------------------

BufferManager.prototype = new RealtimeTabManager();
BufferManager.prototype.constructor = BufferManager;

function BufferManager(client){
	this.init(client);
}

//-------------------------------- INIT -----------------------------------

BufferManager.prototype.init = function(client){
	RealtimeTabManager.call(this, client);
	
	// Settings
	this.url = "/api/buffer"
	this.data_type = "json"
	
	// UI Settings
	this.name = "#buffer-tab";
	this.selector = this.name + " .tab-content:nth-child(2)";
	
	// Additional attributes
	this.live_item = null;
	this.timestamp = null;
	this.history = [];
	this.youtube_manager = new YoutubeManager(this);
	this.recommandation_manager = null;
		
	// Init Methods
	this.getAjax();
	this.moveListen();
	this.downListen();
	this.upListen();
	this.deleteListen();
}

//--------------------------------- GET -----------------------------------

BufferManager.prototype.getAjax = function(){
	var that = this;	
	var data = this.getData();
	
	// GET items
	$.ajax({
		url: that.url,
		type: "GET",
		dataType: that.data_type,
		timeout: 60000,
		data: data,
		error: function(xhr, status, error) {
			PHB.log('An error occurred: ' + error + '\nPlease retry.');
		},
		success: function(json){
			
			if(json.broadcasts.length > 0){
				that.timestamp = json.timestamp;
				
				that.empty(function(){
					that.getCallback(json.broadcasts);
				})
			}
			else{
				that.noData();
			}

		},
	});
}

BufferManager.prototype.noData = function(){
	// UI modifications
	$("#youtube-player").empty();
	$("#youtube-player").append($("<p/>").html("No live track."));
	$("#media-title").html("No current track.")
	
	// Buffer panel
	$(this.selector + " .init").html("Nothing on the air")
	
	// Next track
	$("#panel-box p.logged").html("Nothing yet")
	
	if(this.client.admin){
		// Open the recommandation manager
		this.recommandation_manager = new RecommendationManager(this.client)
	}
}

// Save the intial state of the buffer and trigger the cycle
BufferManager.prototype.getCallback = function(broadcasts){
	
	// Format the list from the server
	for(var i=0, c=broadcasts.length; i<c; i++){
		var new_item = this.serverToLocalItem(broadcasts[i]);
		this.items.push(new_item);
	}

	// Play the new live broadcast
	this.play()
	
	// Display the UI
	this.UIEmpty()
	for(var i=0, c=this.items.length; i<c; i++){
		var item = this.items[i];
		var new_item_div = this.UIBuild(item);
		this.UIAppend(new_item_div);
	}
}

BufferManager.prototype.serverToLocalItem = function(content){
	var item = {
		id: content.key_name,
		content: content
	}
	return item
}

//--------------------------------- INCOMING ---------------------------------------

BufferManager.prototype.add = function(new_event){
	// event = incoming item + information (position, created)
	// state = event + buffer_before + buffer_after
	var that = this;
	
	// This is a position change
	if(new_event.position){
		
		that.processIncoming(new_event, function(previous_item){
			
			// Find the item
			var item = null;
			for(var i=0, c=that.items.length; i<c; i++){
				if(that.items[i].id == new_event.id){
					item = that.items[i];
					break;
				}
			}
			
			// Add it to the UI
			that.UIAdd(item, previous_item);
			
			// Refresh next track
			that.displayNextTrack();
		});
				
	}
	// This is a new broadcast
	else{
		that.processIncoming(new_event, function(previous_item){
			var item = that.serverToLocalItem(new_event.item);

			// In case there was no live item before
			if(!that.live_item){
				that.timestamp = PHB.now();

				that.play();
			}

			// Add it to the UI anyway
			that.UIAdd(item, previous_item);
			
			// Refresh next track
			that.displayNextTrack();			
		})
	}
}

BufferManager.prototype.pushRemove = function(new_event){
	
	var that = this;
	that.processIncoming(new_event, function(previous_item){	
		
		// Remove from the UI
		that.UIRemove(new_event.id);
		
		// Refresh next track
		that.displayNextTrack();
	});
}

BufferManager.prototype.filter = function(new_event, callback){
	
	var created = new_event.created
	var past_states = [];
	var next_events = [new_event];
	
	// Browse history to filter events that happened before and after the new event
	for(var i=0, c=this.history.length; i<c; i++){
		var state = this.history[i];
		var event = state.event;
		
		// Normal case: the new event happened after
		if(event.created <= created){
			past_states.push(state);
		}
		// Unusual case due to PubNub: the new event happened before
		else{
			next_events.push(event);
		}
	}
	
	// Determine which buffer state to build on top of
	var buffer_before = {};
	// If the past states list is not empty, get the last item buffer
	if(past_states.length > 0){
		buffer_before = past_states[past_states.length-1].buffer_after;
		
		// Clean the history from all the states that are going to be recalculated
		var history_reset = this.history.slice(0, past_states.length);
		this.history = history_reset;
	}
	// If not pick up as the buffer before the current item list
	else{
		buffer_before = {
			"broadcasts": this.items.slice(0),
			"timestamp": this.timestamp,
		}		
	}
	
	callback(buffer_before, next_events);
}

BufferManager.prototype.getDuration = function(broadcasts){
	var total_duration = 0;
	for(var i=0, c=broadcasts.length; i<c; i++){
		total_duration += broadcasts[i].content.youtube_duration;
	}
	return total_duration;
}

BufferManager.prototype.reOrderBuffer = function(buffer, callback){
	
	var broadcasts = buffer.broadcasts;
	var timestamp = buffer.timestamp;
	
	var buffer_duration = this.getDuration(broadcasts);
	var offset = ((PHB.now() - timestamp)) % buffer_duration
	var elapsed = 0;
	
	var new_live_item = null;
	var start = 0;
	var updated_buffer = {
		"broadcasts": [],
		"timestamp": PHB.now(),
	};
	
	for(var i=0, c=broadcasts.length; i<c; i++){
		var item = broadcasts[i];
		var duration = item.content.youtube_duration;
		
		// This is the current broadcast
		if(elapsed + duration > offset){
			start = offset - elapsed;
					
			var previous_items = broadcasts.slice(0,i);
			var new_live_item = broadcasts[i];
			var next_items = broadcasts.slice(i+1);
			
			updated_buffer = {
				"broadcasts": [new_live_item].concat(next_items, previous_items),
				"timestamp": PHB.now() - start,
			}
			
			break;
		}
		// We must keep browsing the list before finding the current track
		else{
			elapsed += duration
		}
	}
		
	callback(new_live_item, start, updated_buffer);
}


BufferManager.prototype.processIncoming = function(new_event, callback){
	
	var that = this;

	// Figure out the right position in the history to insert the event
	this.filter(new_event, function(buffer_before, next_events){
		
		var buffer_after = null;
		var previous_item = null;
		
		// Browse next events list
		for(var i=0, c=next_events.length; i<c; i++){
			
			// Get buffer reordered before making any changes to it
			that.reOrderBuffer(buffer_before, function(new_live_item, start, updated_buffer){
				
				var event = next_events[i]
				buffer_after = updated_buffer

				// Move a broadcast to a different position
				if(event.position){
					
					// Withdraw the broadcast from the existing list
					var broadcast_to_move = null;
					for(var j=0, d=buffer_after.broadcasts.length; j<d; j++){
						if(event.id == buffer_after.broadcasts[j].id){
							broadcast_to_move = buffer_after.broadcasts.splice(j,1)[0];
							break;
						}
					}
					
					// Insert the broadcast at the right position
					var previous_broadcasts = buffer_after.broadcasts.slice(0, event.position)
					var next_broadcasts = buffer_after.broadcasts.slice(event.position, buffer_after.broadcasts.length)
					
					// There ought to be a previous broadcast
					previous_item = previous_broadcasts[previous_broadcasts.length - 1];
					buffer_after.broadcasts = previous_broadcasts.concat([broadcast_to_move], next_broadcasts);
					
				}
				else{
					if(event.id){
						// Remove the item with this id
						for(var j=0, d=buffer_after.broadcasts.length; j<d; j++){
							if(event.id == buffer_after.broadcasts[j].id){
								buffer_after.broadcasts.splice(j,1);
								break;
							}
						}
					}
					else{
						// Add it at the end of the list
						var new_item = that.serverToLocalItem(event.item);
						previous_item = buffer_after.broadcasts[buffer_after.broadcasts.length-1]
						buffer_after.broadcasts.push(new_item);
					}
				}
				
				// Build the new state and put in history
				var new_state = {
					"event": event,
					"buffer_before": buffer_before,
					"buffer_after": buffer_after,
				}
				that.history.push(new_state);

				// Only keep a 30 elements history
				var new_history = that.history.reverse().slice(0,30).reverse();
				that.history = new_history;
				
				// Necessary for the next round in the loop
				buffer_before = buffer_after;	
			});
						
		}
		
		// At the end of the buffer recalculation, set the new items list and timestamp
		that.timestamp = buffer_after.timestamp
		that.items = buffer_after.broadcasts
			
		// Callback necessary to make UI changes
		callback(previous_item);
	});
}

//--------------------------------- MOVE -----------------------------------

BufferManager.prototype.moveListen = function(){
	
	var that = this
	$(this.selector).sortable({
		
		// Prevent other items to be moved to the first position
		items:".item:not(:first)",
		zIndex: 4000,
		axis: "y",
		scrollSensitivity: 40,
		scrollSpeed: 40,
		
		sort: function(event, ui){
			// Necessary on Firefox to reposition the draggable element
			if(SYSTEM.browser == "Firefox"){
				ui.helper.css({'top' : ui.position.top + $(window).scrollTop() + 'px'});
			}
		},
		
		// Once sorting has stopped
		update:function(event, ui){
			
			var move = true;
			
			// Prevent live item to be moved
			var id = $(ui.item).attr("id");
			if(id == that.live_item.id){
				
				var move = false;
				var re = RegExp("[.]","g");
				var div_selector = "#" + id.toString().replace(re, "\\.");
				$(div_selector).prependTo(that.selector);
								
			}
			
			if(move){
				// If move authorized, get new position
				var new_position = 0;
				var ids_list = $(this).sortable("toArray");
				for(var i=0, c=ids_list.length; i<c; i++){
					if(ids_list[i] == id){
						new_position = i + 1; // Because the first element is not in the "draggable list"
						break;
					}
				}
				
				var plugin = $(this);
				that.move(id, new_position, function(response){	
					if(!response){
						plugin.sortable("cancel");
						PHB.error("Broadcast has not been moved in your selection.")
					}
				})
				
			}
			
		},	
	});
	
}

BufferManager.prototype.move = function(id, new_position, callback){
	
	var data = this.moveData(id, new_position);
	var that = this;

	$.ajax({
		url: that.url,
		type: "POST",
		dataType: that.data_type,
		timeout: 60000,
		data: data,
		error: function(xhr, status, error) {
			callback(false)
		},
		success: function(json){
			callback(json.response);
		},
	});

}

BufferManager.prototype.moveData = function(id, new_position){
	// Build data
	var shortname = this.client.host.shortname;		
	var data = {
		shortname: shortname,
		content: JSON.stringify(id),
		position: new_position,
	}
	return data
}

//-------------------------------------  UP  --------------------------------------

BufferManager.prototype.upListen = function(){
		
	var that = this;
	$("a.item-up").live("click", function(){
				
		var id = $(this).attr("name");
		
		var previous_item = null;
		var item_to_move = null;
		var existing_position = null;
		for(var i=0, c= that.items.length; i<c; i++){
			var item = that.items[i];
			if(item.id == id){
				previous_item = that.items[i-1];
				item_to_move = item;
				existing_position = i;
				break;
			}
		}
				
		if(existing_position && existing_position != 1){
			
			// Make a fake animation
			var first_anim_over = false;
			var second_anim_over = false;
			
			var re = RegExp("[.]","g");
			var selector = "#" + id.replace(re, "\\.");
			var margin_top = 1 + 82 * existing_position;		
			$(selector).animate(
				{"marginTop": "-" + margin_top + "px"}, 
				{
					"duration": 400,
					"complete": function(){
						first_anim_over = true;
					}
				});
			
			var next_item = that.items[1]
			var selector_next_item = "#" + next_item.id.replace(re, "\\.");
			var margin_top_next_item = 81
			$(selector_next_item).animate(
				{"marginTop": margin_top_next_item + "px"},
				{
					"duration":400,
					"complete": function(){
						second_anim_over = true;
					}
				});
			
			// Once animation ended, replace items in html
			setTimeout(function(){
				$(selector)
					.css("marginTop","-1px")
					.insertAfter("#buffer-tab .tab-content:nth-child(2) .item:first-child")
				
				$(selector_next_item)
					.css("marginTop","-1px")
					.insertAfter(selector)				
			}, 420)		
			
			// Submit the position change
			that.up(id, function(response){
				
				if(!response){				
					// Hack necessary to bypass bugs due to the jquery animation
					var timeout = 0;
					if(!first_anim_over || !second_anim_over){
						timeout = 420;
					}
					
					setTimeout(function(){
						// Remove item put up in the list
						that.UIRemove(id)

						// Put it back to his initial place
						that.UIAdd(item_to_move, previous_item)
					}, timeout)
					
					PHB.error("Broadcast position did not change")
				}
			})
			
		}
		
		$(this).blur();
		return false;
	})
	
}

BufferManager.prototype.up = function(id, callback){
	var data = this.upData(id);
	var that = this;

	$.ajax({
		url: that.url,
		type: "POST",
		dataType: that.data_type,
		timeout: 60000,
		data: data,
		error: function(xhr, status, error) {
			callback(false)
		},
		success: function(json){
			callback(json.response);
		},
	});

}

BufferManager.prototype.upData = function(id){
	// Build data
	var shortname = this.client.host.shortname;		
	var data = {
		shortname: shortname,
		content: JSON.stringify(id),
		position: 1,
	}
	return data
}

//------------------------------------- DOWN ---------------------------------------

BufferManager.prototype.downListen = function(){
	
	var that = this;
	$("a.item-down").live("click",function(){
		
		var id = $(this).attr("name");
		
		var previous_item = null;
		var item_to_move = null;
		var existing_position = null;
		for(var i=0, c= that.items.length; i<c; i++){
			var item = that.items[i];
			if(item.id == id){
				previous_item = that.items[i-1];
				item_to_move = item;
				existing_position = i;
				break;
			}
		}
		
		if(existing_position && existing_position != that.items.length - 1){
			
			// Make a fake animation
			var anim_over = false;
			
			var re = RegExp("[.]","g");
			var selector = "#" + id.replace(re, "\\.");
			var margin_top = 81 * (that.items.length - 1 - i);
			var margin_bottom = margin_top + 83;	
			$(selector).animate(
				{
					"marginTop": margin_top + "px",
					"marginBottom": "-" + margin_bottom + "px",
				},{
					"duration": 400,
					"complete": function(){
						anim_over = true;
					}
				});
				
			// Once animation ended, replace items in html
			setTimeout(function(){
				$(selector)
					.css("marginTop","-1px")
					.css("marginBottom","0px")
					.appendTo("#buffer-tab .tab-content")			
			}, 420)
			
			// Submit the position change
			that.down(id, function(response){
				
				if(!response){
					var timeout = 0;
					if(!anim_over){
						timeout = 420;
					}
					
					setTimeout(function(){
						// Remove item put up in the list
						that.UIRemove(id)

						// Put it back to his initial place
						that.UIAdd(item_to_move, previous_item)
					}, timeout)

					PHB.error("Broadcast position did not change")
					
				}

			})
		
		}
		
		$(this).blur()
		return false;
		
	})
	
}

BufferManager.prototype.down = function(id, callback){
	var data = this.downData(id);
	var that = this;

	$.ajax({
		url: that.url,
		type: "POST",
		dataType: that.data_type,
		timeout: 60000,
		data: data,
		error: function(xhr, status, error) {
			callback(false)
		},
		success: function(json){
			callback(json.response);
		},
	});
}

BufferManager.prototype.downData = function(id){
	// Build data
	var shortname = this.client.host.shortname;		
	var data = {
		shortname: shortname,
		content: JSON.stringify(id),
		position: this.items.length - 1,
	}
	return data
}

//--------------------------------- POST methods -----------------------------------

// Before a track is submitted, we finish building it
BufferManager.prototype.prePostBuild = function(item){
	var channel_id = this.client.channel_id;
	var created = PHB.now();

	content = item.content;
	content["key_name"] = channel_id + ".queued." + created + Math.floor(Math.random()*100).toString();
	
	var new_item = this.serverToLocalItem(content)
	return new_item
}
// Submit an item to the buffer (Broadcast a track)
BufferManager.prototype.postSubmit = function(btn, incoming_item){
	var ui_room = this.UIRoom()
	if(ui_room > 0){			
		// Format the Track item into a Broadcast item
		var new_item = this.prePostBuild(incoming_item);
		
		// Display "added" message
		this.UISuccess(btn);
		
		// Append the new item locally
		new_item_div = this.UIBuild(new_item)
		this.UIAppend(new_item_div);
		
		// POST request to the server
		var that = this;
		this.postAjax(new_item, function(response){
			that.postCallback(new_item, response);
		});
	}
	else{
		this.UIFail(btn)
	}
}

BufferManager.prototype.postData = function(item){
	var shortname = this.client.host.shortname;		
	var data = {
		shortname: shortname,
		content: JSON.stringify(item.content),
	}
	return data
},

//------------------------------------- UI  -----------------------------------------

BufferManager.prototype.UISuccess = function(btn){
	btn.addClass("success")
	btn.html("Added")
	
	setTimeout(function(){
		btn.removeClass("success")
		btn.html("Add")
	}, 2000)
}

BufferManager.prototype.UIFail = function(btn){
	btn.addClass("danger")
	btn.html("Full")
	
	setTimeout(function(){
		btn.removeClass("danger")
		btn.html("Add")
	}, 2000)
},

BufferManager.prototype.UIAdd = function(new_item, previous_item){	
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
		this.UIPrepend(new_item_div); // Specific to the BufferManager
	}
}

BufferManager.prototype.UIBuild = function(item){
	var id = item.id;
	var content = item.content;
	var title = content.title;
	var duration = PHB.convertDuration(content.duration);
	var thumbnail = content.thumbnail;
	var track_submitter_name = content.track_submitter_name;
	var track_submitter_url = content.track_submitter_url;
	var track_submitter_picture = "https://graph.facebook.com/" + content.track_submitter_key_name + "/picture?type=square";	
	
	var div = $("<div/>").addClass("item").attr("id", id)
	
	div.append(
		$("<div/>")
			.addClass("item-picture")
			.append($("<img/>").attr("src", thumbnail))
	)
	.append(
		$("<div/>")
			.addClass("item-title")
			.append($("<span/>").addClass("middle").html(title))
	)
	.append(
		$("<a/>")
			.attr("href","#")
			.addClass("item-up")
			.attr("name", id)
	)
	.append(
		$("<a/>")
			.attr("href","#")
			.addClass("item-down")
			.attr("name", id)
	)
	.append(
		$("<a/>")
			.attr("href","#")
			.addClass("item-cross")
			.attr("name", id)
			.html("X")
	)
	.append(
		$("<div/>")
			.addClass("item-subtitle")
			.append($("<div/>").addClass("item-duration").html(duration))
	)
	
	var mention = null;
	// If submitter different than host, display rebroadcast mention
	if(this.client.host.key_name != content.track_submitter_key_name){
		mention = "Rebroadcast of"
	}
	
	if(mention){
		var subtitle = div.find(".item-subtitle")
		subtitle.append(
			$("<div/>")
				.addClass("item-submitter")
				.append(
					$("<a/>")
						.attr("href", track_submitter_url)
						.attr("target", "_top")
						.append(
							$("<img/>")
								.attr("src", track_submitter_picture)
								.addClass("tuto")
								.attr("data-original-title", track_submitter_name)
						)
				)
				.append($("<span/>").html(mention))
		)
	}
	
	return div
}

BufferManager.prototype.UIInsert = function(new_item_div, previous_item_selector){	
	new_item_div.insertAfter(previous_item_selector); // Specific to the BufferManager
}

BufferManager.prototype.UIEmpty = function(){
	var that = this;
	$(that.selector).empty();
}

BufferManager.prototype.UIRoom = function(){

	var items_selector = this.selector + " .item"
	var items_number = $(items_selector).length
    var	room = 30 - items_number;
	
	return room
}

//------------------------------------- LIVE -----------------------------------------

// Play the new live broadcast
BufferManager.prototype.play = function(){
	
	var that = this;
	var buffer = {
		"broadcasts": this.items,
		"timestamp": this.timestamp,
	}
	
	this.reOrderBuffer(buffer, function(new_live_item, start, updated_buffer){
		
		// Update data
		that.live_item = new_live_item;
		that.items = updated_buffer.broadcasts;
		that.timestamp = updated_buffer.timestamp;
		
		// Play the live broadcast
		that.youtube_manager.init(new_live_item, start);
		
		// Post action to FACEBOOK
		that.postAction(new_live_item, start);
		
		// Display next track
		that.displayNextTrack();
		
		var timeout = new_live_item.content.youtube_duration - start;
		
		// Program the next play
		setTimeout(function(){
			// Refresh the UI
			that.UIRefresh()

			// Trigger the next broadcast
			that.play()

		}, timeout * 1000);
	})
}

BufferManager.prototype.UIRefresh = function(){
	var item_div = this.UIBuild(this.live_item);
	
	// Remove old live item from the top
	this.UIRemove(this.live_item.id)
	
	// Replace old live item at the bottom
	this.UIAppend(item_div)	
}

BufferManager.prototype.postAction = function(item, start){	
	if(this.client.listener){
		var offset = 10;	
		
		var broadcast_url = PHB.site_url + "/broadcast/" + item.id;
		var obj = { "live": broadcast_url };
		var extra = {};
		var expires_in = item.content.youtube_duration - start - offset;
		
		// If track still playing in 10 sec
		if(expires_in > 0 && VOLUME){
			if(this.client.admin){
				// BROADCAST action
				var action = "broadcast";
			}
			else{
				// ATTEND action
				var action = "attend";
			}
			
			// Auto publish action after 10 sec interaction + VOLUME on
			setTimeout(function(){
				if(VOLUME){
					FACEBOOK.putAction(action, obj, extra, expires_in);
				}
			}, offset * 1000)
		}
	}
}

/* --------------------------------- NEXT TRACK --------------------------------- */

BufferManager.prototype.displayNextTrack = function(){
	
	if(this.client.listener){
		var items = this.items;
		var next_item = null;
		if(items.length == 0){
			$("#panel-box p.logged").html("Nothing yet")
		}
		else{
			if(items.length == 1){
				next_item = items[0]
			}
			else{
				next_item = items[1]
			}

			var content = next_item.content;
			var youtube_title = content.youtube_title;
			var youtube_thumbnail = "https://i.ytimg.com/vi/" + content.youtube_id + "/default.jpg";

			$("#panel-box-picture").empty().append($("<img/>").attr("src", youtube_thumbnail))
			$("#panel-box p.logged").html(youtube_title)
		}
	}
	
}
