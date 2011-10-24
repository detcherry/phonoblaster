function WidgetFetcher(identifier){
	this.identifier = identifier;
}

WidgetFetcher.prototype = {
	
	fetchContent: function(caller) {
		var that = this;
		
		tracks = [];
		
		$.ajax({
			url: "/widget/configure",
			type: "GET",
			dataType: "json",
			timeout: 60000,
			data: {
				identifier: that.identifier
			},
			error: function(xhr, status, error) {
				console.log('An error occurred: ' + error + '\nPlease retry.');
			},
			success: function(json){
				if (json.status == "Yes") {
					tracks = json.tracks;
				}
				caller.contentArrived(tracks,parseInt(json.listeners));
			},
		});	
	},
	
	fetchHistory: function(caller){
		var that = this;
		var history = [];
		
		$.ajax({
			url: "/widget/history",
			type: "GET",
			dataType: "json",
			timeout: 60000,
			data: {
				identifier: that.identifier,
			},
			error: function(xhr, status, error) {
				console.log('An error occurred: ' + error + '\nPlease retry.');
			},
			success: function(json){
				if (json.status == "Yes") {
					history = json.tracks;
				}
				caller.historyArrived(history);
			},
		});
	}
	
}