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
	this.previewListen();
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
	console.log("In serverToLocalItem TapeManager");
	var item = {
		id: content.id,
		name: content.name,
		content: content,
	}
	return item;
}

TapeManager.prototype.UIBuild = function(item){
	console.log("In UIBuild TapeManager");
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
	);
					
	return div;
}
