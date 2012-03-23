// ---------------------------------------------------------------------------
// TAPE MANAGER
// ---------------------------------------------------------------------------

TapeManager.prototype = new ScrollTabManager();
TapeManager.prototype.constructor = TapeManager;

function TapeManager(station_client){
	ScrollTabManager.call(this, station_client);
	this.init();
}

TapeManager.prototype.init = function(){
	// Settings
	this.url = "/api/tapes";
	this.data_type = "json";
	this.offset = null;
	
	// UI Settings
	this.name = "#tapes-tab";
	this.selector = this.name + " .tab-items";
	
	// Init methods
	this.getListen();
	this.processListen();
	this.scrollListen();
}

TapeManager.prototype.getData = function(){
	var shortname = this.station_client.station.shortname;
	var data = {
		shortname: shortname,
	};
	return data;
}

TapeManager.prototype.serverToLocalItem  = function(content){
	var item = {
		id: content.id,
		name: content.name,
		content: content,
	}
	return item;
}

TapeManager.prototype.UIBuild = function(item){
	var id = item.id;
	var tape_name = item.name;
	var content = item.content;

	var tape_thumbnail = "/static/images/default_tape_thumbnail.png";
	
	
	var div = $("<div/>").addClass("item").attr("id",id);
	div.append(
		$("<div/>")
			.addClass("item-picture")
			.append($("<img/>").attr("src", tape_thumbnail))
	)
	.append(
		$("<div/>")
			.addClass("item-title")
			.append($("<span/>").addClass("middle").html(tape_name))
	)
	.append(
		$("<div/>")
			.addClass("item-subtitle")
				.append(
						$("<div/>")
							.addClass("item-process")
							.append(
								$("<a/>")
									.addClass("btn")
									.attr("name", id)
									.html("Open")
									.addClass("tuto")
									.attr("data-original-title", "Open track list")
								)

					)
	);
					
	return div;
}

TapeManager.prototype.processListen = function(){
	var that = this;

	var process_selector = this.selector + " .item-process a.btn";
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

		this.process(btn, to_submit);
		return false;			
	});
}

TapeManager.prototype.process = function(btn, to_submit){
	
	$.ajax({
		url: that.url,
		type: "GET",
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
