$(function(){
	// Drag and drop 
	var initial_position = null;
	var final_position = null;
	
	$("#buffer-tab .tab-content:nth-child(2)").sortable({
		
		items: ".item[id!=live]",
		
		// During sorting
		sort:function(event, ui){
			$(ui.helper).css("borderRight","1px solid #E1E1E1").css("borderLeft","1px solid #E1E1E1");
		},
		
		// Once sorting has stopped
		stop:function(event, ui){
			$(ui.item).css("borderRight","none").css("borderLeft","none")			
		},	
	});
})


// ---------------------------------------------------------------------------
// BUFFER MANAGER
// ---------------------------------------------------------------------------

BufferManager.prototype = new RealtimeTabManager();
BufferManager.prototype.constructor = BufferManager;

function BufferManager(station_client){
	this.init(station_client);
}

//-------------------------------- INIT -----------------------------------

BufferManager.prototype.init = function(station_client){
	RealtimeTabManager.call(this, station_client);
	
	// Settings
	this.url = "/api/buffer"
	this.data_type = "json"
	
	// UI Settings
	this.name = "#buffer-tab";
	this.selector = this.name + " .tab-content:nth-child(2)";
	
	// Additional attributes
	this.live_item = null;
	//this.youtube_manager = new YoutubeManager(400, 225);
		
	// Init Methods
	this.get();
	this.deleteListen();
}

//--------------------------------- GET -----------------------------------

BufferManager.prototype.noData = function(){
	// UI modifications
	$("#media").empty();
	$("#media").append($("<p/>").html("No live track."));
	
	$("#media-title").html("No current track")
	
	if(this.station_client.admin){
		// Open the recommandation manager
	}
}





