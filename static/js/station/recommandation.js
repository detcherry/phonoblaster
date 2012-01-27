// ---------------------------------------------------------------------------
// RECOMMANDATION MANAGER
// ---------------------------------------------------------------------------

RecommandationManager.prototype = new ScrollTabManager();
RecommandationManager.prototype.constructor = RecommandationManager;

function RecommandationManager(station_client){
	ScrollTabManager.call(this, station_client);
	
	// Settings
	this.url = "/api/history"
	this.data_type = "json"
	
	// UI Settings
	this.selector = "#recommandations-zone"
	
	// Init Method
	this.dispatch()
	this.processListen();
	this.closeListen();
}

RecommandationManager.prototype.dispatch = function(){
	var number_of_broadcasts = this.station_client.broadcasts_counter.count;
	if(number_of_broadcasts == 0){		
		// Call Facebook API to know which tracks the user has posted on his wall
	}
	else{		
		// Call history API to get the latest tracks broacast in the station
		this.get();
	}
}

// Collect the data necessary to GET items from the server
RecommandationManager.prototype.getData = function(){
	var shortname = this.station_client.station.shortname;
	var offset = PHB.now();
	var data = {
		shortname: shortname,
		offset: offset,
	}
	return data
}

RecommandationManager.prototype.get = function(){	
	var that = this;	
	var data = this.getData();
	
	// GET items
	$.ajax({
		url: that.url,
		type: "GET",
		dataType: that.data_type,
		timeout: 60000,
		data: data,
		error: function(xhr, status, error) {
			PHB.log('An error occurred: ' + error + '\nPlease retry.');
		},
		success: function(json){
			if(json.length > 0){
				// Update recommandation popup and display it
				$("#popup-recommandation h3 strong").html("Phonoblaster")
				$.fancybox($("#popup-recommandation"), {
					topRatio: 0.4,
					modal: true,
				});
				
				// Remove volume
				$("#volume a").trigger("click");
				
				that.empty(function(){
					that.getCallback(json);
				})
			}
		},
	});	
}

RecommandationManager.prototype.closeListen = function(){
	$("#popup-recommandation a.primary").click(function(){
		// Close popup
		$.fancybox.close(true);
		
		// Put volume back
		$("#volume a").trigger("click");
	})
}

RecommandationManager.prototype.serverToLocalItem = function(content){
	content["type"] = "track";
	content["track_admin"] = true;
	content["track_submitter_key_name"] = this.station_client.station.key_name;
	content["track_submitter_name"] = this.station_client.station.name;
	content["track_submitter_url"] = "/" + this.station_client.station.shortname;
	
	// Tracks fetched from Phonoblaster
	if(content.track_id){
		var item = {
			id: content.track_id,
			created: content.created,
			content: content,
		}
	}
	// Tracks fetched from Facebook + Youtube
	else{
		var item = {
			id: content.youtube_id,
			created: null,
			content: content,
		}
	}
	
	return item;	
}

RecommandationManager.prototype.UIBuild = function(item){
	var id = item.id;
	var content = item.content;
	
	var youtube_id = content.youtube_id;
	var youtube_title = content.youtube_title;
	var youtube_duration = PHB.convertDuration(content.youtube_duration)
	var youtube_thumbnail = "http://i.ytimg.com/vi/" + youtube_id + "/default.jpg";
	
	var process_action = "Queue!"
	
	var div = $("<div/>").addClass("item").attr("id",id)
	
	div.append(
		$("<span/>")
			.addClass("square")
			.append(
				$("<img/>")
					.attr("src", youtube_thumbnail)
			)
		)
		.append(
			$("<div/>")
				.addClass("title")
				.append(
					$("<span/>")
						.addClass("middle")
						.html(youtube_title)
				)
		)
		.append(
			$("<div/>")
				.addClass("subtitle")
				.append(
					$("<div/>")
						.addClass("duration")
						.html(youtube_duration)
				)
				.append(
					$("<div/>")
						.addClass("process-actions")
						.append(
							$("<a/>")
								.addClass("btn")
								.attr("name",id)
								.html(process_action)
						)
				)
		)
				
	return div;
}

