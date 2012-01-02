// ---------------------------------------------------------------------------
// STATUS MANAGER
// ---------------------------------------------------------------------------

function StatusManager(station_client){
	// Reference useful to access the admin status of the current user
	this.station_client = station_client;
	this.status = null;
	this.init();
}

StatusManager.prototype = {
	
	init: function(){
		PHB.log("Listening to status events if user is admin")
	},
	
	setStatus: function(new_status){
		this.status = new_status;
		this.displayStatus();
	},
	
	displayStatus: function(){
		PHB.log("Display status")
	},
	
}