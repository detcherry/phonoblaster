/*-------- LATEST TRACKS MANAGER -------- */

function LatestTracksManager(tracklistManager){
	this.tracklistManager = tracklistManager;
	this.date_limit = parseInt(Date.parse(new Date()))/1000 + 3600;
	
	//Scrollbar for this column
	this.scrollbar = new Scrollbar("#latest_tab #latest", "310px", "510px");
	
	this.init();
}

LatestTracksManager.prototype = {

	init: function(){
		// Listen to click events
		this.listen();
		
		// Fetch the latest tracks
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
				
				// Scrollbar update
				that.scrollbar.updateSize();
			},
		});
		
	},
	
	display: function(id, title, thumbnail, duration){
		// Duration handling
		var seconds = parseInt(duration,10) % 60;
		var minutes = (parseInt(duration,10) - seconds)/60
		if(seconds < 10){
			seconds = "0"+ seconds.toString();
		}
		var to_display = minutes.toString() + ":" + seconds;
		
		$("#latest")
			.append(
				$("<div/>")
					.addClass("track")
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
		
		// Listen to click on add to buffer links
		$("a.add_to_buffer").live("click", function(){
			var obj = $(this);
			that.check_tracklist_room(obj, that.process_add_track);
			return false;
		});
		
		// Listen to fetch events
		$("a#fetch_old_tracks").live("click", function(){
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
		});
		
		// Listen to fill events
		$("a.fill_buffer").live("click", function(){
			var obj = $(this);
			that.check_tracklist_room(obj, that.process_fill_buffer);
			return false;
		});
		
		// Listen to shuffle events
		$("a.shuffle_buffer").live("click", function(){
			var obj = $(this);
			that.check_tracklist_room(obj, that.process_shuffle_buffer);
			return false;
		});
		
	},
	
	check_tracklist_room: function(obj, callback){
		// Determine how many tracks I can add
		var tracklist_length = this.tracklistManager.tracklist.length;
		if(this.tracklistManager.new_track){
			tracklist_length += 1;
		}
		var room_in_tracklist = 10 - tracklist_length;
		
		if(room_in_tracklist > 0){
			console.log("Some room in the tracklist");

			var repl = $("<img/>").attr("src","/static/images/small-ajax-loader.gif").addClass("loader");
			obj.replaceWith(repl);			
			
			callback.call(this, repl, room_in_tracklist);
		}
		else{
			console.log("Already 10 tracks in the list");
			var origin_class = obj.attr("class");
			var origin_content = obj.html();
			
			var repl = $("<a/>").addClass("button").addClass("danger").html("Tracklist full");
			obj.replaceWith(repl);
			
			setTimeout(function(){
				repl.removeClass("button").removeClass("danger").addClass(origin_class).html(origin_content);
			}, 1000)	
		}
	},
	
	process_add_track: function(obj, room_in_tracklist){
		var div_result = obj.parent().parent();
		var div_info = div_result.find(".info");

		var title = div_info.find(".title").html();
		var id = div_info.find(".id").html();
		var thumbnail = div_info.find(".thumbnail").html();
		var duration = div_info.find(".duration").html();
		
		var new_track = {
			"title": title,
			"id": id,
			"thumbnail": thumbnail,
			"duration": duration,
		}
		var tracks_to_add = [];
		tracks_to_add.push(new_track);
		
		var that = this;
		this.add_to_buffer(tracks_to_add, function(response){
			that.display_at_the_top(tracks_to_add);
			that.callback_add_to_buffer(obj, response);
		});
	},
	
	add_to_buffer: function(tracks_to_add, callback){
		$.ajax({
			url: "/track/add",
			type: "POST",
			dataType: "json",
			timeout: 60000,
			data: {
				station_key: station_key,
				tracks: JSON.stringify(tracks_to_add),
				channel_id: channel_id,
			},
			error: function(xhr, status, error) {
				console.log('An error occurred: ' + error + '\nPlease retry.');
				callback.call(this, false)
			},
			success: function(json){
				if(json.status == "Added"){						
					console.log("Your song has been added to the tracklist");
					callback.call(this, true)
				}
				else{
					console.log("Already 10 songs in the list. Wait for a few minutes before submitting a new song");
					callback.call(this, false)
				}
			},
		});
		
	},
	
	callback_add_to_buffer: function(obj, response){		
		if(response){
			repl = $("<a/>").addClass("button").addClass("success").html("Added");
			obj.replaceWith(repl);
			
			setTimeout(function(){
				obj = repl;
				obj.removeClass("success").addClass("add_to_buffer").html("Add to list")
			}, 1000)
			
		}
		else{
			repl = $("<a/>").addClass("button").addClass("danger").html("Error");
			obj.replaceWith(repl);
			
			setTimeout(function(){
				obj = repl;
				obj.removeClass("danger").addClass("add_to_buffer").html("Add to list")
			}, 1000)
		}
		
	},
	
	process_fill_buffer: function(obj, room_in_tracklist){		
		// Collect the unique tracks collection of the latest tracks
		var unique_tracks = this.collect_tracks_in_latest_playlist(room_in_tracklist);
	
		// Make a loop to add as elements as possible
		var tracks_to_add = [];
		for(j=0, d=room_in_tracklist; j<d; j++){
			var index = j % unique_tracks.length
			tracks_to_add.push(unique_tracks[index])			
		}
		
		var that = this;
		this.add_to_buffer(tracks_to_add, function(response){
			that.display_at_the_top(tracks_to_add);
			that.callback_fill_buffer(obj, response);
		});
	},
	
	collect_tracks_in_latest_playlist: function(number_of_elements){
		var unique_tracks = [];
		
		var counter = 0;
		$("#latest .track").each(function(index){
			if(counter < number_of_elements){
				var div_info = $(this).find(".info");
				
				var id = div_info.find(".id").html();
				var title = div_info.find(".title").html();
				var thumbnail = div_info.find(".thumbnail").html();
				var duration = div_info.find(".duration").html();
				
				track = {
					"title": title,
					"id": id,
					"thumbnail": thumbnail,
					"duration": duration,
				}
				
				var unique = true
				for(i=0, c=unique_tracks.length; i<c; i++){
					var unique_track = unique_tracks[i]
					if(unique_track["id"] == track["id"]){
						unique = false
						break;
					}
				}
				
				// If track is unique add it to the unique tracks array
				if(unique){
					unique_tracks.push(track);
				}
				
				counter++
			}
			// We have found enough tracks
			else{
				return false;
			}
		})
		
		return unique_tracks;
	},
	
	callback_fill_buffer: function(obj, response){
		
		if(response){
			var repl = $("<a/>").addClass("button").addClass("success").html("Added")
			obj.replaceWith(repl)
			
			setTimeout(function(){
				obj = repl;
				obj.removeClass("success").addClass("fill_buffer").html("Add the latest!")
			}, 2000)
		}
		else{
			var repl = $("<a/>").addClass("button").addClass("danger").html("Tracklist full")
			obj.replaceWith(repl)
			
			setTimeout(function(){
				obj = repl;
				obj.removeClass("danger").addClass("fill_buffer").html("Add the latest!")
			}, 2000)
		}
		
	},
	
	process_shuffle_buffer: function(obj, room_in_tracklist){
		var number_of_tracks_in_the_latest_playlist = $("#latest .track").size();
		
		// Collect the unique tracks collection of all latest tracks displayed
		var unique_tracks = this.collect_tracks_in_latest_playlist(number_of_tracks_in_the_latest_playlist);
		
		// Make a loop to add as elements as possible
		var tracks_to_add = [];
		for(j=0, d=room_in_tracklist; j<d; j++){			
			var random_integer = Math.floor(Math.random()* unique_tracks.length);
			var random_track = unique_tracks[random_integer];
			
			tracks_to_add.push(random_track)			
		}
		
		var that = this;
		this.add_to_buffer(tracks_to_add, function(response){
			that.display_at_the_top(tracks_to_add);
			that.callback_shuffle_buffer(obj, response);
		});
	},
	
	callback_shuffle_buffer: function(obj, response){
		
		if(response){
			repl = $("<a/>").addClass("button").addClass("success").html("Added")
			obj.replaceWith(repl)
			
			setTimeout(function(){
				obj = repl;
				obj.removeClass("success").addClass("shuffle_buffer").html("Shuffle!")
			}, 2000)
		}
		else{
			repl = $("<a/>").addClass("button").addClass("danger").html("Tracklist full")
			obj.replaceWith(repl)
			
			setTimeout(function(){
				obj = repl;
				obj.removeClass("danger").addClass("shuffle_buffer").html("Shuffle!")
			}, 2000)
		}
		
	},
	
	display_at_the_top: function(tracks){
		
		for(i=0, c=tracks.length; i<c; i++){
			track = tracks[i];
			
			// Duration handling
			var seconds = parseInt(track.duration,10) % 60;
			var minutes = (parseInt(track.duration,10) - seconds)/60
			if(seconds < 10){
				seconds = "0"+ seconds.toString();
			}
			var to_display = minutes.toString() + ":" + seconds;

			$("#latest_tracks_paragraph")
				.after(
					$("<div/>")
						.addClass("track")
						.append(
							$("<div/>")
								.addClass("info")
								.append(
									$("<p/>")
										.addClass("id")
										.html(track.id)
								)
								.append(
									$("<p/>")
										.addClass("title")
										.html(track.title)
								)
								.append(
									$("<p/>")
										.addClass("thumbnail")
										.html(track.thumbnail)
								)
								.append(
									$("<p/>")
										.addClass("duration")
										.html(track.duration)
								)
						)
						.append(
							$("<img/>")
								.attr("src", track.thumbnail)
								.addClass("img")
						)
						.append(
							$("<div/>")
								.addClass("title")
								.append(
									$("<span/>")
										.html(track.title)
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
		}

		// Scrollbar update
		this.scrollbar.updateSize();

	},

}