// ---------------------------------------------------------------------------
// SUGGESTION MANAGER
// ---------------------------------------------------------------------------

SuggestionManager.prototype = new TabManager();
SuggestionManager.prototype.constructor = SuggestionManager;

function SuggestionManager(station_client){
	this.station_client = station_client;
	this.suggestions = [];
}

SuggestionManager.prototype = {
	
	init: function(){
		PHB.log("Fetch suggestions")
	},
	
	listen: function(){
		
	},
	
}
