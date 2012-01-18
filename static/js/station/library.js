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
	var item = {
		id: content.track_id,
		created: content.track_created,
		content: content,
	}
	return item;
}