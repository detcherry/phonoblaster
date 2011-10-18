/*-------- LATEST TRACKS MANAGER -------- */

function LatestTracksManager(tracklistManager){
	this.tracklistManager = tracklistManager;
	this.date_limit = parseInt(Date.parse(new Date()))/1000 + 3600;
	this.init();
}

LatestTracksManager.prototype = {

	init: function(){
		this.fetch();
	},

	fetch: function(){
		var that = this;
		
		$.ajax({
			url: "/playlist/latest",
			type: "POST",
			dataType: "json",
			timeout: 60000,
			data: {
				date_limit: that.date_limit,
			},
			error: function(xhr, status, error) {
				console.log('An error occurred: ' + error + '\nPlease retry.');
			},
			success: function(json){
				$("#latest .loader").remove();
				
				//Display tracks
				$.each(json.tracks, function(i){
					track = json.tracks[i];
					id = track.id;
					title = track.title;
					thumbnail = track.thumbnail;
					duration = track.duration
					
					that.display(id, title, thumbnail, duration)
				})
				
				//Check if additional tracks
				if(json.date_limit){
					$("#latest")
						.append(
							$("<a/>")
								.attr({
									"id":"fetch_old_tracks",
									"href":"",
								})
								.addClass("button")
								.html("Fetch older tracks")
						)
					
					that.date_limit = parseInt(json.date_limit);
				}
				
				// Listen to events on this tab
				that.listen();
				
			},
		});
		
	},
	
	display: function(id, title, thumbnail, duration){
		seconds = parseInt(duration,10) % 60;
		minutes = (parseInt(duration,10) - seconds)/60
		if(seconds < 10){
			seconds = "0"+ seconds.toString();
		}
		to_display = minutes.toString() + ":" + seconds;
		
		$("#latest")
			.append(
				$("<div/>")
					.addClass("track")
					.attr("id", id)
					.append(
						$("<div/>")
							.addClass("info")
							.append(
								$("<p/>")
									.addClass("id")
									.html(id)
							)
							.append(
								$("<p/>")
									.addClass("title")
									.html(title)
							)
							.append(
								$("<p/>")
									.addClass("thumbnail")
									.html(thumbnail)
							)
							.append(
								$("<p/>")
									.addClass("duration")
									.html(duration)
							)
					)
					.append(
						$("<img/>")
							.attr("src", thumbnail)
							.addClass("img")
					)
					.append(
						$("<div/>")
							.addClass("title")
							.append(
								$("<span/>")
									.html(title)
							)
					)
					.append(
						$("<div/>")
							.addClass("subtitle")
							.append(
								$("<div/>")
									.addClass("duration")
									.html(to_display)
							)
							.append(
								$("<a/>")
									.attr("href","")
									.addClass("add_to_buffer")
									.addClass("button")
									.html("Add to list")
							)
					)

			)
	},

	listen: function(){
		var that = this;
		
		// Reset listeners
		$("a.add_to_buffer").unbind("click");
		$("a#fetch_old_tracks").unbind("click");
		
		//Listen to add events
		$("a.add_to_buffer")
			.click(function(){				
				divResult = $(this).parent().parent();
				divInfo = divResult.find(".info");

				title = divInfo.find(".title").html();
				id = divInfo.find(".id").html();
				thumbnail = divInfo.find(".thumbnail").html();
				duration = divInfo.find(".duration").html();
				
				if(that.tracklistManager.tracklist.length < 9){
					$(this).replaceWith(
						$("<img/>")
							.attr("src","/static/images/small-ajax-loader.gif")
							.addClass("loader")
					)
					if(title && id && thumbnail && duration){
						that.addToTracklist(title, id, thumbnail, duration);
					}
				}
				else{
					console.log("Too many songs in the list");
					that.trackNotAdded(id);
				}
				
				return false;
			});
		
		//Listen to fetch events
		$("a#fetch_old_tracks")
			.click(function(){
				$(this).replaceWith(
					$("<div/>")
						.addClass("loader")
						.append(
							$("<img/>")
								.attr("src","/static/images/small-ajax-loader.gif")
								.addClass("loader")
						)
				);
				that.fetch();
				return false;
			})
	},
	
	addToTracklist: function(title, id, thumbnail, duration){
		var that = this;
		$.ajax({
			url: "/track/add",
			type: "POST",
			dataType: "json",
			timeout: 60000,
			data: {
				station_key: station_key,
				title: title,
				id: id,
				thumbnail: thumbnail,
				duration: duration,
				channel_id: channel_id,
			},
			error: function(xhr, status, error) {
				console.log('An error occurred: ' + error + '\nPlease retry.');
			},
			success: function(json){
				if(json.status == "Added"){						
					console.log("Your song has been added to the tracklist");
					that.trackAdded(id);
					that.displayAtTheTop(title, id, thumbnail, duration)
				}
				else{
					console.log("Already 10 songs in the list. Wait for a few minutes before submitting a new song");
					that.trackNotAdded(id);
				}
			},
		});
	},
	
	trackAdded: function(track_id){
		$("#latest #"+ track_id + " img.loader")
			.replaceWith(
				$("<a/>")
					.addClass("add_to_buffer")
					.addClass("success")
					.html("Added")
			)
	},
	
	displayAtTheTop: function(title, id, thumbnail, duration){
		seconds = parseInt(duration,10) % 60;
		minutes = (parseInt(duration,10) - seconds)/60
		if(seconds < 10){
			seconds = "0"+ seconds.toString();
		}
		to_display = minutes.toString() + ":" + seconds;
		
		$("#latest_tracks_paragraph")
			.after(
				$("<div/>")
					.addClass("track")
					.attr("id", id)
					.append(
						$("<div/>")
							.addClass("info")
							.append(
								$("<p/>")
									.addClass("id")
									.html(id)
							)
							.append(
								$("<p/>")
									.addClass("title")
									.html(title)
							)
							.append(
								$("<p/>")
									.addClass("thumbnail")
									.html(thumbnail)
							)
							.append(
								$("<p/>")
									.addClass("duration")
									.html(duration)
							)
					)
					.append(
						$("<img/>")
							.attr("src", thumbnail)
							.addClass("img")
					)
					.append(
						$("<div/>")
							.addClass("title")
							.append(
								$("<span/>")
									.html(title)
							)
					)
					.append(
						$("<div/>")
							.addClass("subtitle")
							.append(
								$("<div/>")
									.addClass("duration")
									.html(to_display)
							)
							.append(
								$("<a/>")
									.attr("href","")
									.addClass("add_to_buffer")
									.addClass("button")
									.html("Add to list")
							)
					)
			)
		
		// Listen to the add_to_buffer link that is on the track just added
		this.listen();
	},
	
	trackNotAdded: function(track_id){
		var that = this;
		$("#latest #"+ track_id + " a.add_to_buffer")
			.replaceWith(
				$("<a/>")
					.addClass("add_to_buffer")
					.addClass("danger")
					.html("List full")
			)

		setTimeout(function(){
			$("#latest #"+ track_id + " a.add_to_buffer")
				.remove();
				
			$("#latest #"+ track_id + " .subtitle")
				.append(
					$("<a/>")
						.attr("href","#")
						.addClass("add_to_buffer")
						.addClass("button")
						.html("Add to list")
				)
			
			that.listen()

		}, 1000)
	},

}