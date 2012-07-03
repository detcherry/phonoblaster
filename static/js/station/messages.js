// ---------------------------------------------------------------------------
// CHAT MANAGER
// ---------------------------------------------------------------------------

MessageManager.prototype = new RealtimeTabManager();
MessageManager.prototype.constructor = MessageManager;

function MessageManager(client){
	RealtimeTabManager.call(this, client);
	
	// Settings
	this.url = "/api/messages"
	this.data_type = "json"
	
	// UI Settings
	this.selector = "#messages-feed"
	
	// Init methods
	this.init();
	this.focus = true;
	this.unread_messages = 0;
	this.search_items = [];
	this.search_content = "";
}

MessageManager.prototype.init = function(){
	// General events 
	this.toggleListen();
	this.inputListen();
	this.switchListen();
	this.previewListen();
	this.processListen();
	
	// Events relative to chat
	this.submitListen();	
	
	// Events relative to suggestions
	this.searchListen();
	this.searchPreviewListen();
	this.searchSubmitListen();
	
	// Get latest messages
	this.getAjax();
}

MessageManager.prototype.toggleListen = function(){	
	var that = this;
	
	// Toggle messages interface
	$("#messages-header, #messages-alert").click(function(){
		var messages = $(this).parent();
		
		var messages_status = messages.hasClass("opened");
		var notifications_status = false;
		if(document.title != that.client.host.name){
			notifications_status = true;
		}
		
		// Chat window opened
		if(messages_status){
			// Notifications displayed
			if(notifications_status){
				
				// Hide and reset notifications
				that.unread_messages = 0;
				
				// Clear notifications in the tab header
				document.title = that.client.host.name;
				
				// Hide notifications in the messages
				$("#messages-alert").hide();
				$("#messages-alert-number").html(that.unread_messages);
			}
			else{
				// Close the messages interface
				messages.removeClass("opened")
			}
		}
		else{
			// Hide and reset notifications
			that.unread_messages = 0;
			
			// Clear notifications in the tab header
			document.title = that.client.host.name;
			
			// Hide notifications in the messages
			$("#messages-alert").hide();
			$("#messages-alert-number").html(that.unread_messages);
			
			// Open the messages interface
			messages.addClass("opened");
			
			// Scroll to the bottom
			var height = $(that.selector).height();
			$(that.selector).parent().scrollTop(height);
		}
	})
	
	// Listen to clicks on tab
	$(window).focus(function(){
		that.focus = true;
	})
	
	$(window).blur(function(){
		that.focus = false;
	})
}

/* Switch from a text to a track message or the opposite */
MessageManager.prototype.switchListen = function(){
	$("ul#messages-options a").click(function(){
		// If not current form
		if(!$(this).hasClass("current")){
			// Show the current form
			 $(this)
				.addClass("current")
				.parent("li")
				.siblings("li")
				.find("a.current")
				.removeClass("current");
				
			// Show target, hide others.
			 $($(this).attr('href'))
				.show()
				.siblings("form")
				.hide();
		}
		
		// Hide suggestions if text form selected
		if($(this).attr("id") == "text-option"){
			$("#messages-suggestions").hide()
		}
		
		$(this).blur();
		return false;
	})
}

MessageManager.prototype.inputListen = function(){

	var that = this;
	
	// Listen to focus events in the messages form
	$("#messages-field input").focus(function(){
		var default_text_content = "Send a message..."
		var default_track_content = "Suggest a track..."
		var content = $(this).val()
		
		if(content == default_text_content || content == default_track_content){
			//Clear the input text
			$(this).val("")
		}
		
		// If user not authenticated, display popup
		if(!that.client.listener){
			FACEBOOK.login();
			$(this).blur();
		}
	})
}

MessageManager.prototype.searchListen = function(){
	// Show suggestions search screen if search already in input
	$("#track-form input").focus(function(){
		var content = $(this).val();
		if(content != "Suggest a track..." && content.length > 1){
			$("#messages-suggestions").show();
		}
	})
	
	var that = this;
	// Trigger get each time something is typed
	$("#track-form input").keyup(function(){
		that.search_content = $(this).val()
		
		// Only trigger searches that have more than 1 character
		if(that.search_content.length > 1){
			$("#messages-suggestions").show();
			that.search();
		}
	})
	
	// Prevent submit events
	$("form#track-form").submit(function(){
		return false;
	})
	
}

MessageManager.prototype.search = function(){	
	var that = this;
	
	$.ajax({
		url: "https://gdata.youtube.com/feeds/api/videos",
		dataType: "jsonp",
		timeout: 60000,
		data: {
			"q": that.search_content,
			"max-results": 6,
			"format": 5,
			"v": 2,
			"alt": "jsonc",
		},
		error: function(xhr, status, error) {
			PHB.log('An error occurred: ' + error + '\nPlease retry.');
		},
		success: function(json){
			var items = json.data.items;
			
			if(items && items.length > 0){
				that.search_items = items
				
				$("#messages-suggestions").empty();
				$.each(that.search_items, function(index, item){


					var youtube_id = item.id;
					var youtube_title = item.title;
					var youtube_duration = PHB.convertDuration(item.duration)
					var youtube_thumbnail = "https://i.ytimg.com/vi/" + youtube_id + "/default.jpg";
					var preview = "https://www.youtube.com/embed/" + youtube_id + "?autoplay=1"

					$("#messages-suggestions").append(
						$("<div/>")
							.addClass("item")
							.attr("id", youtube_id)
							.append(
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
													.attr("name", youtube_id)
													.html("Suggest")
											)
											.append(
												$("<a/>")
													.addClass("preview")
													.addClass("fancybox.iframe")
													.attr("href", preview)
											)
									)
							)
					)
				})
			}
		}
	})
}

MessageManager.prototype.searchPreviewListen = function(){
	$("#messages-suggestions a.preview").fancybox({
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
}

MessageManager.prototype.searchSubmitListen = function(){
	
	var that = this;
	$("#messages-suggestions .item-process a.btn").live("click", function(){
		
		var btn = $(this);
		var id = btn.attr("name");
		
		// Find the item the user has clicked on
		var to_submit = null;
		for(var i=0, c= that.search_items.length; i<c; i++){
			var item = that.search_items[i];
			if(item.id == id){ 
				to_submit = item;
				break;
			}
		}
		
		if(to_submit){
			// Build track message
			var new_item = that.prePostBuild(to_submit);
			var div = that.UIBuild(new_item);
			
			// Add track message to the bottom
			that.UIAppend(div);
			
			// Scroll to the bottom
			var height = $(that.selector).height();
			$(that.selector).parent().scrollTop(height);
			
			// Empty the message box
			$("form#track-form input").blur().val("Suggest a track...");
			$("#messages-suggestions").empty().hide();
			$("a#text-option").trigger("click");
			
			// POST message to everyone
			that.postAjax(new_item, function(response){
				that.postCallback(new_item, response);
			});
		}
		
		return false;
	})

}

MessageManager.prototype.submitListen = function(){	
	
	var that = this;
	// Listen to submit events in the messages form
	$("form#text-form").submit(function(){
		var message = {
			"text": $("#messages-field input").val(),
		}
		
		if(message.text.length > 0 && message.text != "Send a message..."){	
			// Build text message
			var new_item = that.prePostBuild(message);
			var div = that.UIBuild(new_item);
			
			// Add text message to the bottom
			that.UIAppend(div);
			
			// Scroll to the bottom
			var height = $(that.selector).height();
			$(that.selector).parent().scrollTop(height);			

			// Empty the message box
			$("#messages-field input").val("");

			// POST message to everyone
			that.postAjax(new_item, function(response){
				that.postCallback(new_item, response);
			});
		}
		
		return false;
	});
}


MessageManager.prototype.prePostBuild = function(input){
	
	// Build a comment key name
	var channel_id = this.client.channel_id;
	var created = PHB.now();
	var random = Math.floor(Math.random()*100).toString();
	var comment_key_name = channel_id + ".message." + created + random;
	var author_key_name = this.client.listener.key_name;
	var author_name = this.client.listener.name;
	var author_url = "/" + this.client.listener.shortname;
	
	// Text message
	if(input.text){
		var content = {
			key_name: comment_key_name,
			text: input.text,
			youtube_id: null,
			youtube_title: null,
			youtube_duration: null,
			author_key_name: author_key_name,
			author_name: author_name,
			author_url: author_url,
			created: created,
		}
	}
	// Track message
	else{
		var content = {
			key_name: comment_key_name,
			text: null,
			youtube_id: input.id,
			youtube_title: input.title,
			youtube_duration: input.duration,
			track_submitter_key_name: author_key_name,
			track_submitter_name: author_name,
			track_submitter_url: author_url,
			created: created,
		}
	}
	
	var new_item = this.serverToLocalItem(content)

	return new_item;	
}

MessageManager.prototype.UIBuild = function(item){

	var id = item.id;
	var content = item.content;
	var created = PHB.convert(item.created);
	
	if(content.text){
		var text = content.text
		var author_picture_url = "https://graph.facebook.com/"+ content.author_key_name + "/picture?type=square";
		var author_name = content.author_name;
		var author_url = content.author_url;
		
		var div = $("<div/>").addClass("item-wrapper").attr("id", id)
		div.append(
			$("<div/>")
				.addClass("item-wrapper-submitter")
				.append($("<img/>").attr("src", author_picture_url))
		)
		.append(
			$("<div/>")
				.addClass("item-wrapper-content")
				.append(
					$("<p/>")
						.append($("<a/>").attr("href", author_url).html(author_name))
						.append(" " + replaceURLWithHTMLLinks(text))
					)
				.append($("<div/>").addClass("item-time").html(created))
		)
	}
	else{
		var youtube_title = content.youtube_title;
		var youtube_duration = PHB.convertDuration(content.youtube_duration);
		var youtube_thumbnail = "https://i.ytimg.com/vi/" + content.youtube_id + "/default.jpg";	
		var track_submitter_picture_url = "https://graph.facebook.com/"+ content.track_submitter_key_name + "/picture?type=square";
		var track_submitter_name = content.track_submitter_name;
		var track_submitter_url = content.track_submitter_url;
		
		var div = $("<div/>").addClass("item-wrapper").attr("id", id)
		div.append(
			$("<div/>")
				.addClass("item-wrapper-submitter")
				.append($("<img/>").attr("src", track_submitter_picture_url))
		)
		.append(
			$("<div/>")
				.addClass("item-wrapper-content")
				.append(
					$("<p/>")
						.append($("<a/>").attr("href", track_submitter_url).html(track_submitter_name))
						.append(" suggested a track")
				)
				.append(
					$("<div/>")
						.addClass("item")
						.append(
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
						)
				)
				.append($("<div/>").addClass("item-time").html(created))
		)
		
		// For admins only 
		if(this.client.admin){
			var preview = "https://www.youtube.com/embed/" + content.youtube_id + "?autoplay=1"
			
			div.find(".item-subtitle").append(
				$("<div/>")
					.addClass("item-process")
					.append(
						$("<a/>")
							.addClass("btn")
							.attr("name", id)
							.html("Add")
					)
					.append(
						$("<a/>")
							.addClass("preview")
							.addClass("fancybox.iframe")
							.attr("href", preview)
					)
			)
		}
		
	}
				
	return div
}

MessageManager.prototype.UIAdd = function(new_item, previous_item){
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
		// Else, we have to append the item at the top
		this.UIPrepend(new_item_div);
	}
	
	// Scroll to the bottom
	var height = $(this.selector).height();
	$(this.selector).parent().scrollTop(height);
}

MessageManager.prototype.UIInsert = function(new_item_div, previous_item_selector){
	new_item_div.insertAfter(previous_item_selector)
}

MessageManager.prototype.newEvent = function(){
	var messages_status = $("#messages").hasClass("opened");
	var tab_status = this.focus;
	
	// Tab = current
	if(tab_status){
		// Chat window = opened
		if(messages_status){
			// Do nothing
		}
		else{
			// Display notification in the messages header
			this.unread_messages += 1;
			$("#messages-alert-number").html(this.unread_messages);
			$("#messages-alert").show();
		}
		
	}
	// Tab = not visible
	else{
		this.unread_messages += 1;
		// Display notification in the tab header
		document.title = this.client.host.name + " (" + this.unread_messages + ")";
		
		// Display notification in the messages header
		$("#messages-alert-number").html(this.unread_messages);
		$("#messages-alert").show();
	}
}

function replaceURLWithHTMLLinks(text) {
	words = text.split(" ");
	result = "";
	var re = /(?:(?:https?|ftp|file):\/\/|www\.|ftp\.)(?:\([-A-Z0-9+&@#\/%=~_|$?!:;,.]*\)|[-A-Z0-9+&@#\/%=~_|$?!:;,.])*(?:\([-A-Z+++0-9+&@#\/%=~_|$?!:;,.]*\)|[A-Z0-9+&@#\/%=~_|$])/i;
	var is_http = /^https?:\/\//i;

	for (var i = 0; i < words.length; i++) {
		word = words[i];
		// Is the word a URL?
		if (re.test(word)){
			new_word = re.exec(word)[0]

			// Does the URL start with http:// or https:// ?
			if(is_http.test(new_word)){
				new_word = "<a href="+new_word+" target='_blank'>"+new_word+"</a>";
			}else{
				new_word = "<a href=http://"+new_word+" target='_blank'>"+new_word+"</a>";
			};
			result = result+ new_word+" ";

		}else{
			result = result + word+" ";
		}

	};

    return result; 
}