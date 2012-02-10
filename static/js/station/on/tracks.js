// ---------------------------------------------------------------------------
// TRACKS MANAGER
// ---------------------------------------------------------------------------

TracksManager.prototype = new ScrollTabManager();
TracksManager.prototype.constructor = TracksManager;

function TracksManager(station_client){
	ScrollTabManager.call(this, station_client);
	
	// Settings
	this.url = "api/tracks";
	this.data_type = "json";
	this.offset = PHB.now();
	
	// UI Settings
	this.name = "#tracks-tab";	
	this.selector = this.name + " .tab-items"
	
	// Init methods
	this.getListen();
	this.previewListen();
	this.processListen();
	this.scrollListen();
}

TracksManager.prototype.getData = function(){
	var shortname = this.station_client.station.shortname;
	var offset = this.offset;
	var data = {
		shortname: shortname,
		offset: offset,
	}
	return data
}

TracksManager.prototype.serverToLocalItem = function(content){
	content["type"] = "track";
	content["track_submitter_key_name"] = this.station_client.station.key_name;
	content["track_submitter_name"] = this.station_client.station.name;
	content["track_submitter_url"] = "/" + this.station_client.station.shortname;
	
	var item = {
		id: content.track_id,
		created: content.track_created,
		content: content,
	}
	
	return item;
}