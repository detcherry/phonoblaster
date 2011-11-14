/* --------- LIBRARY CONTROLLER -------*/

function LibraryController(tracklistManager){
	this.tracklistManager = tracklistManager;
	this.library = [];
	this.date_limit = Date.parse(new Date())/1000 ;
	this.uiLibraryController = new UILibraryController();
	
	// Fetch the latest tracks from the user library
	this.init();
}

LibraryController.prototype = {
	
	init: function(){
		// Listen to click events
		this.listen();
		
		// Fetch the latest tracks
		this.fetch();
	},
	
	fetch: function(){
		var that = this;
		
		$.ajax({
			url: "/user/"+ user_id +"/library",
			type: "POST",
			dataType: "json",
			timeout: 60000,
			data: {
				date_limit: that.date_limit,
			},
			error: function(xhr, status, error) {
				phonoblaster.log('An error occurred: ' + error + '\nPlease retry.');
			},
			success: function(json){
				// Add tracks received				
				that.add_old_tracks(json.tracks);
				
				//Check if additional tracks
				if(json.date_limit){
					$("#library")
						.append(
							$("<a/>")
								.attr({
									"id":"fetch_more_tracks",
									"href":"",
								})
								.addClass("button")
								.html("More tracks")
						)
					
					that.date_limit = parseInt(json.date_limit);
				}
			},
		});
		
	},
	
	// Add at the top
	add_new_tracks: function(tracks){
		var different_tracks = this.minify(tracks);
		
		// Display new tracks at the top
		this.uiLibraryController.add_new_tracks(different_tracks)
	},
	
	// Add at the bottom
	add_old_tracks: function(tracks){
		var different_tracks = this.minify(tracks);
		
		// Display new tracks at the bottom
		this.uiLibraryController.add_old_tracks(different_tracks)
	},
	
	// Minify a list of tracks to a list of unique tracks
	minify: function(tracks){
		var different_tracks = [];
		
		for(i=0, c=tracks.length; i<c; i++){
			var track = tracks[i]
			var already_there = false
			
			// Check if the track is already in the library
			for(j=0, d=this.library.length; j<d; j++){
				var library_track = this.library[j];
				if(track.id == library_track.id){
					already_there = true;
					break;
				}
			}
			
			// If it was not there add it to the library
			if(!already_there){
				this.library.push(track);
				different_tracks.push(track);
			}
		}
		
		return different_tracks;
	},
	
	// Listen to all types of events in the library tab
	listen: function(){
		var that = this;
		
		// Listen to fetch events
		$("a#fetch_more_tracks").live("click", function(){
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
		
		// Listen to click on add to buffer links
		$("a.add_to_buffer").live("click", function(){
			var obj = $(this);
			that.check_tracklist_room(obj, that.process_add_track);
			return false;
		});
		
		// Listen to fill events
		$("a.fill_buffer").live("click", function(){
			var obj = $(this);
			if(that.library.length > 0){
				that.check_tracklist_room(obj, that.process_fill_buffer);
			}
			else{
				var repl = $("<a/>").addClass("button").addClass("danger").html("No track");
				obj.replaceWith(repl);

				setTimeout(function(){
					repl.removeClass("danger").addClass("fill_buffer").html("Add the latest!");
				}, 1000)
			}
			return false;
		});
		
		// Listen to shuffle events
		$("a.shuffle_buffer").live("click", function(){
			var obj = $(this);
			if(that.library.length > 0){
				that.check_tracklist_room(obj, that.process_shuffle_buffer);
			}
			else{
				var repl = $("<a/>").addClass("button").addClass("danger").html("No track");
				obj.replaceWith(repl);

				setTimeout(function(){
					repl.removeClass("danger").addClass("shuffle_buffer").html("Shuffle!");
				}, 1000)
			}
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
			phonoblaster.log("Some room in the tracklist");

			var repl = $("<img/>").attr("src","/static/images/small-ajax-loader.gif").addClass("loader");
			obj.replaceWith(repl);			
			
			callback.call(this, repl, room_in_tracklist);
		}
		else{
			phonoblaster.log("Already 10 tracks in the list");
			$("#room_counter").popover("show")
			var origin_class = obj.attr("class");
			var origin_content = obj.html();
			
			var repl = $("<a/>").addClass("button").addClass("danger").html("Tracklist full");
			obj.replaceWith(repl);
			
			setTimeout(function(){
				$("#room_counter").popover("hide")
				repl.removeClass("button").removeClass("danger").addClass(origin_class).html(origin_content);
			}, 3000)	
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
				phonoblaster.log('An error occurred: ' + error + '\nPlease retry.');
				callback.call(this, false)
			},
			success: function(json){
				if(json.status == "Added"){						
					phonoblaster.log("Your songs have been added to the tracklist");
					callback.call(this, true)
				}
				else{
					phonoblaster.log("Already 10 songs in the list. Wait for a few minutes before submitting a new song");
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
				//It has to stay 30 sec displayed as "succes" so that people know what they've just added
			}, 30000)
			
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
		var number_of_library_tracks = this.library.length;
		
		// Make a loop to add as elements as possible
		var tracks_to_add = [];
		for(j=0, d=room_in_tracklist; j<d; j++){
			var index = j % number_of_library_tracks;
			tracks_to_add.push(this.library[index]);		
		}
		
		var that = this;
		this.add_to_buffer(tracks_to_add, function(response){
			that.callback_fill_buffer(obj, response);
		});
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
		var number_of_library_tracks = this.library.length;
	
		// Make a loop to add as elements as possible
		var tracks_to_add = [];
		var random_integers = [];
		for(j=0, d=room_in_tracklist; j<d; j++){
			var random_integer = Math.floor(Math.random()* number_of_library_tracks);
			var random_track = this.library[random_integer];
			var already_picked_up = false;
			
			// Make sure we don't pick up twice the same track
			for(k=0, e=random_integers.length; k<e; k++){
				if(random_integer == random_integers[k]){
					already_picked_up = true;
					break;
				}
			}
			
			if(!already_picked_up){
				tracks_to_add.push(random_track);
				random_integers.push(random_integer);
			}
		}
		
		var that = this;
		this.add_to_buffer(tracks_to_add, function(response){
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
}


/*---------- UI LIBRARY CONTROLLER --------*/

function UILibraryController(){
	
	//Scrollbar for this column
	this.scrollbar = new Scrollbar("#library_tab #library", "310px", "490px");
	
}

UILibraryController.prototype = {
	
	// Add at the top
	add_new_tracks: function(tracks){
		// Display tracks one by one
		for(i=0, c=tracks.length; i<c; i++){
			// Init variables
			track = tracks[i]
			var id = track.id;
			var title = track.title;
			var thumbnail = track.thumbnail;
			var duration = track.duration;
			
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
		}

		// Scrollbar update
		this.scrollbar.updateSize();
	},
	
	
	// Add at the bottom
	add_old_tracks: function(tracks){
		$("#library .loader").remove();
		
		// Display tracks one by one
		for(i=0, c=tracks.length; i<c; i++){
			// Init variables
			track = tracks[i]
			var id = track.id;
			var title = track.title;
			var thumbnail = track.thumbnail;
			var duration = track.duration;
			
			// Duration handling
			var seconds = parseInt(duration,10) % 60;
			var minutes = (parseInt(duration,10) - seconds)/60
			if(seconds < 10){
				seconds = "0"+ seconds.toString();
			}
			var to_display = minutes.toString() + ":" + seconds;
			
			// Add the new track at the bottom of the library list
			$("#library")
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
		}
		
		// Update scrollbar size
		this.scrollbar.updateSize();
	},
	
	
}