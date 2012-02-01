// ---------------------------------------------------------------------------
// AIR MANAGER
// ---------------------------------------------------------------------------

function AirManager(station_client){
	this.station_client = station_client;
	this.air = false;
	
	this.ping();
}

AirManager.prototype = {
	
	ping: function(){
		var that = this;
		
		// Every 3 min request the server (start after 3 secs)
		setInterval(function(){
			if(!that.air){
				that.get();
			}
		}, 180000)

	},
	
	getData: function(){
		var shortname = this.station_client.station.shortname;
		var data = {
			shortname: shortname,
		}
		return data
	},
	
	get: function(){
		var data = this.getData();
		
		var that = this;
		$.ajax({
			url: "/api/air",
			type: "GET",
			dataType: "json",
			timeout: 60000,
			data: data,
			error: function(xhr, status, error) {
				PHB.log('An error occurred: ' + error + '\nPlease retry.');
			},
			success: function(json){
				that.getCallback(json)
			},
		});
	},
	
	getCallback: function(json){
		if(json.response){
			this.air = true;
			
			// Display on air &  station as connected
			$("#station-status span.btn").addClass("danger").html("On air")
			$("#station-status em").html("connected");
			
			// Update popup
			var content = json.content;
			var youtube_id = content.youtube_id;
			var youtube_thumbnail = "http://i.ytimg.com/vi/" + youtube_id + "/default.jpg";
			var youtube_title = content.youtube_title;
			$("#popup-onair span.clip").append($("<img/>").attr("src", youtube_thumbnail))
			$("#popup-onair .title span").html(youtube_title)
			
			// Display popup
			$.fancybox($("#popup-onair"), {
				topRatio: 0.4,
			});
			
		}
	},
		
}