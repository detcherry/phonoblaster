// ---------------------------------------------------------------------------
// AIR MANAGER
// ---------------------------------------------------------------------------

function AirManager(station_client){
	this.station_client = station_client;
	this.air = true;
	
	this.get();
}

AirManager.prototype = {
	
	getData: function(){
		var shortname = this.station_client.station.shortname;
		var offset = PHB.now();
		
		var data = {
			shortname: shortname,
			offset: offset,
		}
		return data
	},
	
	get: function(){
		var data = this.getData();
		
		var that = this;
		$.ajax({
			url: "/api/recommandations",
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
		if(json){
			var items = json
			$.each(items, function(index, content){
				if(index<9){
					var youtube_id = content.youtube_id;
					var youtube_title = content.youtube_title;
					var youtube_thumbnail = "http://i.ytimg.com/vi/" + youtube_id + "/default.jpg";
					$("#popup-offair #broadcasts")
						.append(
							$("<span/>")
								.addClass("clip")
								.append(
									$("<img/>").attr("src", youtube_thumbnail)
								)
						)
				}
			})
			
			// Display popup
			$.fancybox($("#popup-offair"), {
				topRatio: 0.4,
				modal: true,
			});
		}
		
	},
	
	
	
}