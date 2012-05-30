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
	
	// Dispatch if the user is admin (buffer) or not (suggest)
	process: function(btn, to_submit){
		// If station admin it's a broadcast
		if(this.station_client.admin){
			var process_manager = this.station_client.buffer_manager;
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
	getAjax: function(){},
	
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
	postAjax: function(item, callback){
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
		this.deleteAjax(item, function(response){
			that.deleteCallback(item, response)
		})
	},
	
	deleteAjax: function(item, callback){
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
				that.getAjax();
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

ScrollTabManager.prototype.getAjax = function(){
	
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
			var bottom = $(document).height() - $(this).height() - $(this).scrollTop();			
			if(bottom < 100 && !that.load && that.scrolling_on){
				var last_item = that.items[that.items.length -1];
				that.offset = last_item.created;
				that.load = true;
				that.UIShowLoader();
				that.getAjax();
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
// REALTIME TAB MANAGER
// ---------------------------------------------------------------------------

RealtimeTabManager.prototype = new TabManager();
RealtimeTabManager.prototype.constructor = RealtimeTabManager;

function RealtimeTabManager(station_client){
	TabManager.call(this, station_client);
}

RealtimeTabManager.prototype.getAjax = function(){
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
RealtimeTabManager.prototype.pushNew = function(content){	
	this.add(content);
	
	// Event callback
	this.newEvent();
}

// Item to remove received from PUBNUB
RealtimeTabManager.prototype.pushRemove = function(id){
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

