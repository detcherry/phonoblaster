// ---------------------------------------------------------------------------
// LIBRARY MANAGER
// ---------------------------------------------------------------------------

LibraryManager.prototype = new ScrollTabManager();
LibraryManager.prototype.constructor = LibraryManager;

function LibraryManager(station_client){
	ScrollTabManager.call(this, station_client);
	
	// Settings
	this.url = "api/library";
	this.data_type = "json";
	this.offset = PHB.now();
	
	// UI Settings
	this.name = "#library-tab";	
	this.selector = this.name + " .tab-items"
	
	// Init methods
	this.getListen();
	this.previewListen();
	this.processListen();
	this.scrollListen();
}

LibraryManager.prototype.serverToLocalItem = function(content){
	content["type"] = "track";
	
	if(this.station_client.admin){
		content["track_admin"] = true;
		content["track_submitter_key_name"] = this.station_client.station.key_name;
		content["track_submitter_name"] = this.station_client.station.name;
		content["track_submitter_url"] = "/" + this.station_client.station.shortname;
	}
	else{
		content["track_admin"] = false;
		content["track_submitter_key_name"] = this.station_client.user.key_name;
		content["track_submitter_name"] = this.station_client.user.name;
		content["track_submitter_url"] = "/user/" + this.station_client.user.key_name;
	}
	
	var item = {
		id: content.track_id,
		created: content.track_created,
		content: content,
	}
	return item;
}