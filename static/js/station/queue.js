// ---------------------------------------------------------------------------
// QUEUE MANAGER
// ---------------------------------------------------------------------------


function QueueManager(station_client){
	// Reference useful to access the other managers from the queue manager
	this.station_client = station_client;
	this.queue = null;
	this.init();
}

QueueManager.prototype = {
	
	init: function(){
		PHB.log("Fetch queue")
	},
	
	listen: function(){
		
	},
	
}
