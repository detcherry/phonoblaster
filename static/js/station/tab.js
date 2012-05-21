// ---------------------------------------------------------------------------
// PANEL DISPLAYER
// ---------------------------------------------------------------------------

$(function(){
	
	// Show panel
	$(".show-panel").click(function(){
		$("#panel").show();
		return false;
	})
	
	// Hide panel
	$(".hide-panel").click(function(){
		$("#panel").hide();
		return false;
	})
	
})

// ---------------------------------------------------------------------------
// TAB DISPLAYER
// ---------------------------------------------------------------------------

$(function(){
	var tab = new TabDisplayer();
});

function TabDisplayer(){
	this.init()
}

TabDisplayer.prototype = {
	
	init: function(){
		// Listen for click on tabs.
	 	$("#tabs a").bind("click",function() {
			// If not current tab. 
			if (!$(this).hasClass("current")) {
				// Change the current indicator.
				 $(this)
					.addClass("current")
					.parent("li")
					.siblings("li")
					.find("a.current")
					.removeClass("current");
				
				// Show target, hide others.
				 $($(this).attr('href'))
					.show()
					.siblings(".tab")
					.hide();
			}
			
			// Nofollow.
			 this.blur();
			 return false;
		});
		
	},	
}

// ---------------------------------------------------------------------------
// TAB MANAGER
// ---------------------------------------------------------------------------

function TabManager(station_client){
	this.station_client = station_client;
	this.items = [];
	
	// Settings
	this.url = null;
	this.data_type = null;	
	
	// UI Settings
	this.name = null;
	this.selector = this.name + " .tab-content";
}

TabManager.prototype = {
	
	previewListen: function(){
		var preview_selector = this.selector + " a.preview"
		$(preview_selector).fancybox({
			beforeShow: function(){
				try{ytplayer.mute();}
				catch(e){PHB.log(e);}
			},
			afterClose: function(){
				if(VOLUME){
					try{ytplayer.unMute();}
					catch(e){PHB.log(e);}
				}
			},
		});
	},
		
	processListen: function(){
		var that = this;

		var process_selector = this.selector + " .item-process a.btn"
		$(process_selector).live("click", function(){			
			var btn = $(this);
			var item_id = btn.attr("name");

			// Find the item the user has clicked on
			var to_submit = null;
			for(var i=0, c= that.items.length; i<c; i++){
				var item = that.items[i];
				if(item.id == item_id){ 
					to_submit = item;
					break;
				}
			}

			that.process(btn, to_submit);
			return false;			
		})
	},
	
	// Dispatch if the user is admin (queue) or not (suggest)
	process: function(btn, to_submit){
		// If station admin it's a broadcast
		if(this.station_client.admin){
			var process_manager = this.station_client.queue_manager;
		}
		// Otherwise it's a suggestion
		else{
			var process_manager = this.station_client.suggestion_manager;
		}
		process_manager.postSubmit(btn, to_submit);
	},
	
	// Collect the data necessary to GET items from the server
	getData: function(){
		var shortname = this.station_client.station.shortname;
		var data = {
			shortname: shortname,
		}
		return data
	},
	
	// GET items from server
	get: function(){},
	
	empty: function(callback){
		this.items = [];
		$(this.selector).empty();
		callback();
	},
	
	getCallback: function(items_from_server){
		var that = this;
		
		// Add each item to the manager
		$.each(items_from_server, function(index, value){
			that.add(value);
		})
	},
	
	// Transform raw item into a formatted item
	serverToLocalItem: function(content){},
	
	// Add item to the list and display it in the UI
	add: function(item_from_server){
		if(item_from_server){
			var that = this;
			var new_item = this.serverToLocalItem(item_from_server)

			this.addToItems(new_item, function(previous_item){
				that.UIAdd(new_item, previous_item);
			})
		}
	},
	
	// Add new item to list items
	addToItems: function(new_item, callback){},
	
	postData: function(item){
		var shortname = this.station_client.station.shortname;		
		var data = {
			shortname: shortname,
			content: JSON.stringify(item.content),
		}
		return data
	},
	
	// POST request to server
	post: function(item, callback){
		var data = this.postData(item);
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
		
	},
	
	postCallback: function(item, response){
		if(!response){
			this.UIRemove(item.id);
			this.unPostEvent();
			PHB.error("An error occured")
		}
	},
	
	unPostEvent: function(){},
	
	deleteListen: function(){
		var that = this;
		var delete_selector = this.selector + " a.item-cross"
		
		$(delete_selector).live("click", function(){
			var item_id = $(this).attr("name");
			
			var item_to_delete = null;
			for(var i=0, c= that.items.length; i<c; i++){
				var item = that.items[i];
				if(item.id == item_id){
					item_to_delete = item;
					break;
				}
			}
			
			// We check if the item is in the list (sometimes it has not been received by PUBNUB yet...)
			if(item_to_delete){
				that.deleteSubmit(item_to_delete);
			}
			
			return false;
		})
	},
	
	deleteSubmit: function(item){
		// Hide the item
		this.UIHide(item.id)
		
		var that = this;
		this.delete(item, function(response){
			that.deleteCallback(item, response)
		})
	},
	
	delete: function(item, callback){
		var that = this;
		var delete_url = that.url + "/" + item.id
		
		$.ajax({
			url: delete_url,
			type: "DELETE",
			dataType: that.data_type,
			timeout: 60000,
			error: function(xhr, status, error) {
				callback(false)
			},
			success: function(json){
				callback(json.response);
			},
		});
		
	},
	
	deleteCallback: function(item, response){
		if(!response){
			this.UIUnhide(item.id);
			PHB.error("Item hasn't been deleted.")
		}
	},
		
	//--------- EVERYTHING THAT DEALS WITH THE UI IS BELOW -----------//
	
	// Add new item to the UI
	UIAdd: function(new_item, previous_item){},
	
	UIInsert: function(new_item_div, previous_item_selector){
		new_item_div.insertBefore(previous_item_selector)
	},
	
	// Reset the tab in case it contained some init content
	UIReset: function(){
		var init_selector = this.selector + " .init";
		$(init_selector).remove();
	},
	
	UIAppend: function(new_item_div){
		this.UIReset();
		
		var that = this;
		$(that.selector).append(new_item_div)
	},
	
	UIPrepend: function(new_item_div){
		this.UIReset();
		
		var that = this;
		$(that.selector).prepend(new_item_div)
	},
	
	UIBuild: function(item){},
	
	UIRemove: function(id){
		var re = RegExp("[.]","g");
		var selector = "#" + id.replace(re, "\\.");
		$(selector).remove();
	},
	
	UIHide: function(id){
		var re = RegExp("[.]","g");
		var selector = "#" + id.replace(re, "\\.");
		$(selector).hide()
	},
	
	UIUnhide: function(id){
		var re = RegExp("[.]","g");
		var selector = "#" + id.replace(re, "\\.");
		$(selector).show()
	}
	
}

// ---------------------------------------------------------------------------
// SCROLLTAB MANAGER
// ---------------------------------------------------------------------------

ScrollTabManager.prototype = new TabManager();
ScrollTabManager.prototype.constructor = ScrollTabManager;

function ScrollTabManager(station_client){
	TabManager.call(this, station_client);
	
	// Additional attributes
	this.offset = null;
	this.load = false;
	this.scrolling_on = true;	
}

// Lazy fetching
ScrollTabManager.prototype.getListen = function(){
	var that = this;
	
	$("#tabs a").click(function(){
		if(that.items.length == 0){
			that.offset = PHB.now();
			
			var active_tab_name = $("a.current").attr("href")
			var tab_active = false;
			if(that.name == active_tab_name){
				tab_active = true;
			}

			if(tab_active){
				that.get();
			}
		}		
	})
}

ScrollTabManager.prototype.getData = function(){
	var offset = this.offset;
	var data = {
		offset: offset,
	}
	return data
}

ScrollTabManager.prototype.get = function(){
	
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
			that.removeScrolling();
		},
		success: function(json){
			var items_from_server = json;
			
			// Content exists on the server
			if(items_from_server.length > 0){
				// First GET
				if(!that.load){
					// Empty the tab items zone before displaying everything
					that.empty(function(){
						that.getCallback(items_from_server); 
					})
				}
				// Scrolling GET
				else{
					that.getCallback(items_from_server); 
					that.emptyScrolling();
				}
			}
			else{
				// There is no result on the server. Remove the possibility of scrolling
				that.removeScrolling();
				that.noData();
			}
		},
	});	
	
}

ScrollTabManager.prototype.noData = function(){}

ScrollTabManager.prototype.serverToLocalItem = function(content){
	var item = {
		id: content.track_id,
		created: content.created,
		content: content,
	}
	return item;
}

ScrollTabManager.prototype.addToItems = function(new_item, callback){
	this.items.push(new_item);
	callback(null);
}

ScrollTabManager.prototype.UIBuild = function(item){
	var id = item.id;
	var content = item.content;

	var youtube_id = content.youtube_id;
	var youtube_title = content.youtube_title;
	var youtube_duration = PHB.convertDuration(content.youtube_duration)
	var youtube_thumbnail = "https://i.ytimg.com/vi/" + youtube_id + "/default.jpg";
	var preview = "https://www.youtube.com/embed/" + youtube_id + "?autoplay=1"
	
	var process_action = "Suggest"
	var process_info = "Suggest this track to the broadcaster"
	if(this.station_client.admin){
		process_action = "Add"
		process_info = "Add this track to your selection"
	}
	
	var div = $("<div/>").addClass("item").attr("id",id)
	div.append(
		$("<div/>")
			.addClass("item-picture")
			.append($("<img/>").attr("src", youtube_thumbnail))
	)
	.append(
		$("<div/>")
			.addClass("item-title")
			.append($("<span/>").addClass("middle").html(youtube_title))
	)
	.append(
		$("<div/>")
			.addClass("item-subtitle")
			.append($("<div/>").addClass("item-duration").html(youtube_duration))
			.append(
				$("<div/>")
					.addClass("item-process")
					.append(
						$("<a/>")
							.addClass("btn")
							.attr("name", id)
							.html(process_action)
							.addClass("tuto")
							.attr("data-original-title", process_info)
					)
					.append(
						$("<a/>")
							.addClass("preview")
							.addClass("fancybox.iframe")
							.attr("href", preview)
							.addClass("tuto")
							.attr("data-original-title", "Preview this track")
					)
			)
	)
					
	return div;
}

ScrollTabManager.prototype.scrollListen = function(){
	var that = this;

	$(window).scroll(function(){
		
		var active_tab_name = $("a.current").attr("href")
		
		var tab_active = false;
		if(that.name === active_tab_name){
			tab_active = true;
		}
		
		if(tab_active){			
			var above_tab_height = 133;//248-80;
			var tab_height = $(that.name).height();
			var scroll_height = $(this).scrollTop();
			var window_height = $(this).height();
			
			var below_tab_height = scroll_height + window_height - above_tab_height - tab_height;
			if(below_tab_height > 100 && !that.load && that.scrolling_on){
				var last_item = that.items[that.items.length -1];
				that.offset = last_item.created;
				that.load = true;
				that.UIShowLoader();
				that.get();
			}
		}
	})

}

ScrollTabManager.prototype.emptyScrolling = function(){
	this.load = false;
	this.UIRemoveLoader();
	this.UIAppendLoader();
},

ScrollTabManager.prototype.removeScrolling = function(){
	this.scrolling_on = false;
	this.UIRemoveLoader();
}

ScrollTabManager.prototype.UIAdd = function(new_item, previous_item){
	var new_item_div = this.UIBuild(new_item);
	this.UIAppend(new_item_div);
}

ScrollTabManager.prototype.UIAppendLoader = function(){
	$(this.selector).append($("<div/>").addClass("loader"));
}

ScrollTabManager.prototype.UIShowLoader = function(){
	var loader_selector = this.selector + " .loader";
	$(loader_selector).show();
}

ScrollTabManager.prototype.UIRemoveLoader = function(){
	var loader_selector = this.selector + " .loader";
	$(loader_selector).remove();
}

// ---------------------------------------------------------------------------
// SCROLL PLAY TAB MANAGER
// ---------------------------------------------------------------------------

ScrollPlayTabManager.prototype = new ScrollTabManager();
ScrollPlayTabManager.prototype.constructor = ScrollPlayTabManager;

function ScrollPlayTabManager(station_client){
	ScrollTabManager.call(this, station_client);
	
	this.no_data_text = null;
}

ScrollPlayTabManager.prototype.noData = function(){
	// If no track is currently being played
	if(!this.live_item){
		// UI modifications
		$("#media").empty();
		$("#media").append($("<p/>").html(this.no_data_text));
	}
}

ScrollPlayTabManager.prototype.addToItems = function(new_item, callback){
	var initialization = false;
	if(this.items.length == 0){
		initialization = true
	}
	
	// Add it to the list + DOM
	this.items.push(new_item);
	callback(null);
	
	// Put the video live it's the first item
	if(initialization){
		this.live(new_item);
	}
}

// ----------------- LIVE --------------------
ScrollPlayTabManager.prototype.live = function(new_item){		
	this.live_item = new_item;
	
	var id = this.live_item.id;
	var content = this.live_item.content;
	var expired_at = parseInt(content.expired,10);
	var duration = parseInt(content.youtube_duration,10);
	var youtube_id = content.youtube_id;

	// Launches the video
	this.youtube_manager.init(youtube_id);

	// Display the live broadcast in the UI
	this.UILiveSet(this.live_item);
	
	// Set as active in the right column
	this.UIActive(id)
	
	// Post action to FACEBOOK
	this.postAction(this.live_item);
}

ScrollPlayTabManager.prototype.nextVideo = function(time_out){
	
	// Find the next item
	for(var i=0, c=this.items.length; i<c; i++){
		var item = this.items[i]
		if(item.id == this.live_item.id){
			// If item after live item, take it as the next item
			if(this.items[i+1]){
				var next_item = this.items[i+1]
				
				if(!this.items[i+2] && this.scrolling_on){
					
					// Fake a scrolling event
					var last_item = this.items[this.items.length -1];
					this.offset = last_item.created;
					this.load = true;
					this.get();
				}
				
			}
			// Otherwise, take the first item
			else{
				var next_item = this.items[0]
			}

			break;
		}
	}
	
	this.live(next_item);
}

ScrollPlayTabManager.prototype.liveListen = function(){
	var that = this;
	var selector = this.name + " div.item"
	
	$(selector).live("click", function(){
		
		var id = $(this).attr("id");
		
		// Find the next item
		for(var i=0, c=that.items.length; i<c; i++){
			var item = that.items[i]
			if(item.id == id){
				var next_item = item;
				break;
			}
		}
		
		that.live(next_item);
	})
}

ScrollPlayTabManager.prototype.postAction = function(item){
	if(this.station_client.user){
		var track_url = PHB.site_url + "/track/" + item.content.track_id;
		var obj = { "track": track_url };
		var extra = {};
		var expires_in = item.content.youtube_duration;
		
		var action = "replay";
		
		FACEBOOK.putAction(action, obj, extra, expires_in);
	}
}
//---------------- UI ------------------
ScrollPlayTabManager.prototype.UILiveRemove = function(){
	// Remove image
	$("#media-picture").empty();
	
	// Remove title
	$("#media-title span.middle").html("No track is being broadcast");
	
	// Remove the favorite icon
	$("#media-details-right").empty();
	
	// Remove the submitter
	$("#media-submitter").empty();
}

ScrollPlayTabManager.prototype.UIActive = function(id){
	var selector = this.name + " .item"
	$(selector).removeClass("active");
	
	var re = RegExp("[.]","g");
	var selector = "#" + id.toString().replace(re, "\\.");
	$(selector).addClass("active");
}

// ---------------------------------------------------------------------------
// REALTIME TAB MANAGER
// ---------------------------------------------------------------------------

RealtimeTabManager.prototype = new TabManager();
RealtimeTabManager.prototype.constructor = RealtimeTabManager;

function RealtimeTabManager(station_client){
	TabManager.call(this, station_client);
}

RealtimeTabManager.prototype.get = function(){
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
			if(json.length > 0){
				that.empty(function(){
					that.getCallback(json);
				})
			}
			else{
				that.noData();
			}
		},
	});
}

// Callback when no data has been found on the server
RealtimeTabManager.prototype.noData = function(){}

RealtimeTabManager.prototype.serverToLocalItem = function(content){
	var item = {
		id: content.key_name,
		created: content.created,
		content: content
	}
	return item
}

RealtimeTabManager.prototype.addToItems = function(new_item, callback){
	var that = this;
	
	var following_items = [];
	var previous_items = this.items.slice(0);
	var previous_item = null;
	
	// If items array empty, just add the new item to the list
	if(this.items.length == 0){
		this.items.push(new_item)
	}
	else{
		// Browse the items list and insert the item at the right place
		for(var i=0, c=that.items.length; i<c; i++){
			var item = that.items[i];

			// The new item has been posted before (NOT OK)
			if(item.created > new_item.created){
				following_items.push(previous_items.shift());
			}
			// The new item has been posted after (OK)
			else{
				previous_item = item;
				break;
			}
		}
		following_items.push(new_item);
		this.items = following_items.concat(previous_items);
	}
	
	callback(previous_item);
}

RealtimeTabManager.prototype.UIAdd = function(new_item, previous_item){
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
		// Else, we have to append the item at the bottom
		this.UIAppend(new_item_div);
	}
}

RealtimeTabManager.prototype.UISuccess = function(btn){}
RealtimeTabManager.prototype.UIFail = function(btn){}

RealtimeTabManager.prototype.prePostBuild = function(item){}
RealtimeTabManager.prototype.postSubmit = function(btn, item){}

// Item to add received from PUBNUB
RealtimeTabManager.prototype.new = function(content){	
	this.add(content);
	
	// Event callback
	this.newEvent();
}

// Item to remove received from PUBNUB
RealtimeTabManager.prototype.remove = function(id){
	var new_items = []
	var that = this
	for(var i=0, c =that.items.length; i<c; i++){
		var item = that.items[i];
		if(item.id == id){
			// Remove the targeted broadcast
			that.items.splice(i,1);
			
			// Remove the item from the UI
			that.UIRemove(id);
			
			// Event callback
			that.removeEvent();
			
			break;
		}
	}	
}

RealtimeTabManager.prototype.newEvent = function(){}
RealtimeTabManager.prototype.removeEvent = function(){}

