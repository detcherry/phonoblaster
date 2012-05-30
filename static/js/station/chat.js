// ---------------------------------------------------------------------------
// CHAT MANAGER
// ---------------------------------------------------------------------------

ChatManager.prototype = new RealtimeTabManager();
ChatManager.prototype.constructor = ChatManager;

function ChatManager(station_client){
	RealtimeTabManager.call(this, station_client);
	
	// Settings
	this.url = "/api/comments"
	this.data_type = "json"
	
	// UI Settings
	this.selector = "#chat-feed"
	
	// Init methods
	this.init();
	this.unread_messages = 0;
}

ChatManager.prototype.init = function(){
	this.toggleListen();
	this.inputListen();
	
	// Get latest messages
	this.getAjax();
}

ChatManager.prototype.toggleListen = function(){	
	var that = this;
	
	// Toggle chat interface
	$("#chat-header, #chat-alert").click(function(){
		var chat = $(this).parent();
		var status = chat.hasClass("opened")
		
		if(status){
			// Close the chat interface
			chat.removeClass("opened")
		}
		else{
			// Open the chat interface
			chat.addClass("opened")
			
			// Hide and reset notifications
			that.unread_messages = 0;
			$("#chat-alert").hide();
			$("#chat-alert-number").html(that.unread_messages);
			
			chat.removeClass("unread");
			$("#chat-title").html("Chat");
			
			// Scroll to the bottom
			var height = $(that.selector).height();
			$(that.selector).parent().scrollTop(height);
		}
	})
}

ChatManager.prototype.inputListen = function(){

	var that = this;
	
	// Listen to focus events in the chat form
	$("input#chat-input").focus(function(){
		var default_content = "Share the love..."
		var content = $(this).val()
		
		if(content == default_content){
			//Clear the input text
			$(this).val("")
		}
		
		// If user not authenticated, display popup
		if(!that.station_client.user){
			FACEBOOK.login();
			$(this).blur();
		}
	})
	
	// Listen to submit events in the chat form
	$("form#chat-form").submit(function(){
		var message = $("input[id='chat-input']").val();
		
		if(message.length > 0 && message != "Share the love..."){	
			// Build message
			var new_item = that.prePostBuild(message);
			var div = that.UIBuild(new_item);
			
			// Add message to the bottom
			that.UIAppend(div);
			
			// Scroll to the bottom
			var height = $(that.selector).height();
			$(that.selector).parent().scrollTop(height);			

			// Empty the message box
			$("input[id='chat-input']").val("");

			// POST message to everyone
			that.postAjax(new_item, function(response){
				that.postCallback(new_item, response);
			});
		}
		
		return false;
	});
}

ChatManager.prototype.newEvent = function(){
	var status = $("#chat").hasClass("opened");
	
	if(status){
		// do nothing
	}
	else{
		// display notification
		this.unread_messages += 1;
		$("#chat-alert-number").html(this.unread_messages);
		$("#chat-alert").show();
	}
}

ChatManager.prototype.prePostBuild = function(message){
	
	// Build a comment key name
	var channel_id = this.station_client.channel_id;
	if(channel_id){
		var created = PHB.now();
		var random = Math.floor(Math.random()*100).toString();
		var comment_key_name = channel_id + ".comment." + created + random;
	}
	else{
		var created = PHB.now();
		var random = Math.floor(Math.random()*100).toString();
		var comment_key_name = this.station_client.station.shortname + ".offline.comment." + created + random
	}

	
	if(this.station_client.admin){
		var author_key_name = this.station_client.station.key_name;
		var author_name = this.station_client.station.name;
		var author_url = "/" + this.station_client.station.shortname;
		var admin = true;
	}
	else{
		var author_key_name = this.station_client.user.key_name;
		var author_name = this.station_client.user.name;
		var author_url = "/user/" + this.station_client.user.key_name;
		var admin = false; 
	}
	
	// Build content
	var content = {
		key_name: comment_key_name,
		message: message,
		author_key_name: author_key_name,
		author_name: author_name,
		author_url: author_url,
		admin: admin,
		created: created,
	}
	
	var new_item = this.serverToLocalItem(content)

	return new_item;	
}

ChatManager.prototype.UIBuild = function(item){

	var id = item.id;
	var content = item.content;
	var created = PHB.convert(item.created);
	
	var author_picture_url = "https://graph.facebook.com/"+ content.author_key_name + "/picture?type=square";
	var author_name = content.author_name;
	var author_url = content.author_url;
	
	var message = content.message;
	
	var div = $("<div/>").addClass("im").attr("id", id)
	
	div.append(
		$("<div/>")
			.addClass("im-picture")
			.append(
				$("<a/>")
					.attr("href", author_url)
					.append($("<img/>").attr("src", author_picture_url))
			)
	)
	.append(
		$("<div/>")
			.addClass("im-content")
			.append(
				$("<div/>")
					.addClass("im-text")
					.append($("<a/>").attr("href", author_url).html(author_name))
					.append(" " + message)
			)
			.append($("<div/>").addClass("im-time").html(created))
	)
				
	return div
}

ChatManager.prototype.UIAdd = function(new_item, previous_item){
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

ChatManager.prototype.UIInsert = function(new_item_div, previous_item_selector){
	new_item_div.insertAfter(previous_item_selector)
}
