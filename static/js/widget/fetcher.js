function WidgetFetcher(identifier){
	this.identifier = identifier;
}

WidgetFetcher.prototype = {
	
	getTracks: function() {
		var that = this;
		
		tracks = [];
		$.ajax({
			url: "/plugin/widget/configure",
			type: "GET",
			dataType: "json",
			timeout: 60000,
			data: {
				identifier: that.identifier,
			},
			async:false,
			error: function(xhr, status, error) {
				console.log('An error occurred: ' + error + '\nPlease retry.');
			},
			success: function(json){
				if (json.status == "Yes") {
					console.log("Retrieving tracks");
					console.log(json);
					tracks = json.tracks;
				}else{
					console.log("No track");
				}
			},
		});	
		return tracks;
	},
	
	
	fetchNewTracks: function(caller,date_last_refresh){
		var that = this
		
		$.ajax({
			url: "/plugin/widget/update",
			type: "GET",
			dataType: "json",
			timeout: 60000,
			data: {
				identifier: that.identifier,
				date_last_refresh: date_last_refresh
			},
			error: function(xhr, status, error) {
				console.log('An error occurred: ' + error + '\nPlease retry.');
			},
			success: function(json){
				new_tracks = [];
				if (json.status == "Yes") {
					console.log("Some new songs");
					new_tracks = json.tracks;
				}else{
					console.log("No new song");
				}			
				caller.relaunchUpdater(new_tracks);
			},
		});
	},
	
	
	fetchHistory: function(){
		var that = this;
		var history = [];
		
		$.ajax({
			url: "/plugin/widget/history",
			type: "GET",
			dataType: "json",
			timeout: 60000,
			data: {
				identifier: that.identifier,
			},
			async:false,
			error: function(xhr, status, error) {
				console.log('An error occurred: ' + error + '\nPlease retry.');
			},
			success: function(json){
				if (json.status == "Yes") {
					console.log("Retrieving tracks history");
					console.log(json.tracks);
					history = json.tracks;
				}else{
					console.log("No track history");
				}
			},
		});
		
		return history;
	}
	
}