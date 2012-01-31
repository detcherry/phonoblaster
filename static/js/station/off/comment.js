// ---------------------------------------------------------------------------
// COMMENT MANAGER
// ---------------------------------------------------------------------------

CommentManager.prototype = new ScrollTabManager();
CommentManager.prototype.constructor = CommentManager;

function CommentManager(station_client){
	ScrollTabManager.call(this, station_client)
	
	// Settings
	this.url = "/api/comments"
	this.data_type = "json"
	
	// UI Settings
	this.selector = "#comments-zone"
	
	// Init method
	this.get()
}

CommentManager.prototype.getData = function(){
	var shortname = this.station_client.station.shortname;
	var data = {
		shortname: shortname,
	}
	return data
}

CommentManager.prototype.serverToLocalItem = function(content){
	var item = {
		id: content.key_name,
		created: content.created,
		content: content,
	}
	return item;
}

CommentManager.prototype.UIBuild = function(item){	
	
	var id = item.id;
	var content = item.content;
	var created = PHB.convert(item.created);
	
	var author_picture_url = "https://graph.facebook.com/"+ content.author_key_name + "/picture?type=square";
	var author_name = content.author_name;
	var author_url = content.author_url;
	
	var message = content.message;
	
	var div = $("<div/>").addClass("comment").attr("id", id)
		
	div.append(
		$("<img/>")
			.attr("src", author_picture_url)
			.addClass("user")
			.addClass("tuto") // Twipsy
			.attr("data-original-title", author_name) // Twipsy
	)
	.append(
		$("<div/>")
			.addClass("content")
			.append(
				$("<p/>")
					.append($("<a/>").attr("href", author_url).html(author_name))
					.append(" " + message)
			)
	)
	.append($("<div/>").addClass("border"))
	.append($("<div/>").addClass("time").html(created))

	return div;
}