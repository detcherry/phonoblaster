/* -------- INITIALIZATION ------ */

$(function(){
	//Request a channel id and token
	$.ajax({
		url: "/channel/request",
		type: "POST",
		dataType: "json",
		timeout: 60000,
		data: {
			station_key: station_key,
		},
		error: function(xhr, status, error) {
			console.log('An error occurred: ' + error + '\nPlease retry.');
		},
		success: function(json){
			console.log(json);
			channel_id = json.channel_id;
			token = json.token
			
			//Create a channel
			channel = new goog.appengine.Channel(token);
			
			//Initialization
			socket = channel.open();
			socket.onopen = onOpened;
			socket.onmessage = onMessage;
			socket.onerror = onError;
			socket.onclose = onClose;
		},
	});
	
	function onOpened(){
		//do nothing
	}
	
	function onMessage(m){
		dispatcher.dispatch(JSON.parse(m.data));
	}
	
	function onError(){
		window.location.reload();
	}
	
	function onClose(){
		window.location.reload();
	}
	
	//Transforms all the links in target = _blank except the following links
	$("a").attr("target","_blank");
	$("#edit_station a").removeAttr("target");
	$("#volume a").removeAttr("target");
	$("a#shuffle").removeAttr("target");
	
	//Listen to volume events
	volume = true;
	$("#volume a").click(function(){
		if(volume){
			//turn it off
			try{ytplayer.mute();}
			catch(e){console.log(e);}
			volume = false;
			$("#volume img#on").css("display","none");
			$("#volume img#off").css("display","inline");
		}
		else{
			//turn it on
			try{ytplayer.unMute();}
			catch(e){console.log(e);}
			volume = true;
			$("#volume img#on").css("display","inline");
			$("#volume img#off").css("display","none");			
		}//*/
		return false;
	});
	
	//Listen to focus/blur events on the window
	$(window).focus(function(){
	    window_focus = true;
		old_title = document.title;
		re = new RegExp("[(]{1}[0-9]+[)]{1}","g");
		document.title = old_title.replace(re,"");
	})
	.blur(function(){
		window_focus = false;
	});
	//Set focus to true when the page had finished loading
	window_focus = true;
	
	//Trigger the Twipsy module
	$("img.user").twipsy({
		live: "true",
		offset: 3,
	});
	
	// GLOBAL VARIABLES ----> FOR THE YOUTUBE PLAYER
	YOUTUBE_ID = "";
	VIDEO_START = 0;
	
});

/* ------------- YOUTUBE PLAYER MANAGEMENT -------------- */

//Youtube PLAY & VOLUME & ERROR management
function onYouTubePlayerReady(playerId) {
	ytplayer = document.getElementById("ytplayer");
	
	// Puts handler in case the video does not work
	ytplayer.addEventListener("onError", "onPlayerError");
	
	// Triggers the video
	ytplayer.loadVideoById(YOUTUBE_ID, VIDEO_START);

	//If the volume had been turned off, mute the player
	if(!volume){
		ytplayer.mute();
	}
}


function onPlayerError(){	
	console.log("Error: track not working");
	
	// Raise video error
	dispatcher.tracklistManager.errorController.raise();
}

/* --------- DISPATCHER --------- */

function Dispatcher(){
	this.tracklistManager = new TracklistManager();
	this.chatController = new ChatController();
	this.listenerController = new ListenerController();
}

Dispatcher.prototype = {
	
	dispatch: function(data){
		console.log(data);
		if(data.type == "tracklist_init"){
			$("#youtube-player img").hide();
			$("#youtube-player p").show();
			this.tracklistManager.init(data.content);
		}
		if(data.type == "tracklist_new"){
			console.log("tracklist_new");
			this.tracklistManager.add(data.content);
		}	
		if(data.type == "tracklist_delete"){
			console.log("tracklist_delete");
			this.tracklistManager.remove(data.content);
		}
		if(data.type == "chat_init"){
			console.log("chat_init")
			this.chatController.init(data.content);
		}
		if(data.type == "chat_new"){
			console.log("chat_new");
			this.chatController.receive(data.content);
		}
		if(data.type == "chat_delete"){
			console.log("chat_delete");
			//etc
		}
		if(data.type == "listener_init"){
			console.log("listener_init");
			//Init the listeners list
			listeners = data.content;
			this.listenerController.init(listeners);
			
		}
		if(data.type == "listener_new"){
			console.log("listener_new");
			// Add a new listener to the list
			new_listener = data.content;
			this.listenerController.add(new_listener);
		}
		if(data.type == "listener_delete"){
			console.log("listener_delete");
			// Remove a listener from the list
			old_session_id = data.content.session_id;
			this.listenerController.remove(old_session_id);
			
		}
			
	},
}

/* --------- TRACKLIST MANAGER ------------ */

function TracklistManager(){
	this.tracklist = [];
	this.uiTracklistController = new UITracklistController();
	this.youtubeController = new YoutubeController();
	
	this.errorController = new ErrorController(this);
	
	if(allowed_to_post){
		this.searchController = new YoutubeSearch(this);
		this.latestTracksManager = new LatestTracksManager(this);
	}
}

TracklistManager.prototype = {
	
	init: function(tracklist){
		console.log("Init Track Manager")
		this.tracklist = tracklist;
		this.uiTracklistController.display(this.tracklist);
		this.uiTracklistController.listen();
		this.playNext();
	},
	
	add: function(tracklist){
		for(i=0, c=tracklist.length; i<c; i++){
			track = tracklist[i];
			this.tracklist.push(track);
			this.uiTracklistController.add(track);
			this.uiTracklistController.listen();

			//Add +1 to the number of tracks counter
			number_of_tracks = parseInt($("#number_of_tracks").html(),10) + 1;
			$("#number_of_tracks").html(number_of_tracks);
		}
	},
	
	remove: function(phonoblaster_id){
		var that = this		
		for(i=0, c = that.tracklist.length; i<c; i++){
			track = that.tracklist[i];
			if(track.phonoblaster_id == phonoblaster_id){
				//Expiration of tracks after the track deleted should occur earlier
				offset = parseInt(track.duration,10);
				
				for(j = i, c = that.tracklist.length; j < c; j++){
					that.tracklist[j].expired = parseInt(that.tracklist[j].expired, 10) - offset;
				}				
				//Remove the track from the tracklist
				that.tracklist.splice(i,1);
				
				//Remove the track from the UI
				that.uiTracklistController.remove(phonoblaster_id)
				
				//Substract 1 to the number of tracks counter
				number_of_tracks = parseInt($("#number_of_tracks").html(),10) - 1;
				$("#number_of_tracks").html(number_of_tracks);
				
				break;
			}
		}		
	},
	
	playNext: function(){
		console.log("Trying to play a new track");
		this.new_track = this.tracklist.shift();
		if(this.new_track){	
			this.uiTracklistController.removeCross(this.new_track.phonoblaster_id);
					
			expired_at = parseInt(this.new_track.expired,10);
			datetime_now = Date.parse(new Date());
			duration = parseInt(this.new_track.duration,10);
			
			time_out = expired_at - datetime_now/1000;
			video_start = duration - time_out;
			
			// Put track in the error controller
			this.errorController.addTrack(this.new_track);
			
			console.log("▶ New track launched: "+ this.new_track.title + " at " + video_start.toString() +" sec")	
			this.youtubeController.init(this.new_track.id, video_start);
			this.displayInformation(video_start);
			this.displayProgress(video_start, this.new_track.duration);
		}
		else{
			console.log("No track found")
			document.title = station_id;
			time_out = 5;
		}
		this.programNextVideo(time_out)
	},
	
	programNextVideo: function(time_out){
		var that = this;
		
		first_timer = setTimeout(function(){
			that.nextVideo();
		},time_out*1000);		
	},
	
	nextVideo: function(){		
		if(this.new_track){
			this.uiTracklistController.remove(this.new_track.phonoblaster_id);
		}		
		var that = this;
		second_timer = setTimeout(function(){
			that.playNext();
		},1000);
	},
	
	displayInformation: function(video_start){
		seconds = parseInt(video_start,10) % 60;
		minutes = (parseInt(video_start,10) - seconds)/60
		if(seconds < 10){
			seconds = "0"+ seconds.toString();
		}
		to_display = minutes.toString() + ":" + seconds;
			
		document.title = "▶ "+ this.new_track.title;
		$("#conversation")
			.prepend(
				$("<div/>")
					.addClass("announcement")
					.html("▶ "+ this.new_track.title + " at " + to_display)
			)
		
	},
	
	displayProgress: function(video_start, duration){
		x = parseInt(video_start*500/duration);
		$('#filler').css('width', x.toString() + 'px');
		$('#filler').animate({
			width:'500px',
		},parseInt(duration - video_start)*1000,'linear');
	},	
	
}

/* ------ UI TRACKLIST CONTROLLER -------- */

function UITracklistController(){
	//Init slimscroll
	this.scrollbar = new Scrollbar("#tracks_tab #tracks", "309px", "510px");
}


UITracklistController.prototype = {
	
	display: function(tracklist){
		for(i = 0, c = tracklist.length; i < c; i++){
			track = tracklist[i];
			this.add(track);
		}
		this.scrollbar.updateSize();
	},
	
	add: function(track){
		seconds = parseInt(track.duration,10) % 60;
		minutes = (parseInt(track.duration,10) - seconds)/60
		if(seconds < 10){
			seconds = "0"+ seconds.toString();
		}
		to_display = minutes.toString() + ":" + seconds;
		
		$("#tracks").append(
			$("<div/>")
				.addClass("track")
				.attr("id", track.phonoblaster_id)
				.append(
					$("<img/>")
						.attr("src",track.thumbnail)
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
							$("<div/>")
								.addClass("submitter")
								.html("Added by")
						)
						.append(
							$("<a/>")
								.attr("href", "/user/"+ track.submitter_id)
								.attr("target","_blank")
								.addClass("submitter")
								.append(
									$("<img/>")
										.attr({
											"src": "http://graph.facebook.com/" + track.submitter_fcbk_id + "/picture?type=square",
											"class": "user",
											"title": track.submitter_public_name,
										})
								)
						)
				)
		)
		
		this.addCross(track);
	},
	
	addCross: function(track){
		if(track.submitter_fcbk_id == user_fcbk_id){
			$("#tracks #" + track.phonoblaster_id + " .title")
				.prepend(
					$("<img/>")
						.attr("src", "/static/images/small-ajax-loader.gif")
						.css({
							"float": "right",
							"margin":"0px",
							"height":"12px",
							"width":"12px",
							"display":"none",
						})
				)
				.prepend(
					$("<a/>")
						.addClass("close")
						.attr("href","")
						.html("×")
				)
		}
	},
	
	removeCross: function(phonoblaster_id){
		$("#tracks #" + phonoblaster_id + " a.close").remove()
		$("#tracks #" + phonoblaster_id + " .title img").remove()
	},
	
	remove: function(phonoblaster_id){
		$("#" + phonoblaster_id).remove();
	},
	
	listen: function(){
		//In case there were previous links bound to an event handler
		$("a.close").unbind("click");
		
		$("a.close").click(function(){
			cross = $(this);
			img = $(this).parent().find("img");
			phonoblaster_id = $(this).parent().parent().attr("id");
			
			cross.hide();
			img.show();
			
			$.ajax({
				url: "/track/delete",
				type: "POST",
				dataType: "json",
				timeout: 60000,
				data: {
					id: phonoblaster_id,
					station_key: station_key,
				},
				error: function(xhr, status, error) {
					console.log('An error occurred: ' + error + '\nPlease retry.');
				},
				success: function(json){
					if(json.status == "Deleted"){						
						console.log("Your song has been removed from the tracklist");
					}
					else{
						console.log("Your song hasn't been remove from the tracklist");
						img.hide();
					}
				},
			});
			
			return false;
		})
	}
	
}

/* --------- YOUTUBE CONTROLLER ---------- */

function YoutubeController(){
}

YoutubeController.prototype = {
	
	init: function(youtubeID, videoStart){
		this.empty();
		
		var params = { allowScriptAccess: "always"};
		var atts = { id: "ytplayer" };
		var videoURL = "http://www.youtube.com/apiplayer?version=3&enablejsapi=1&playerapiid=player1"
		swfobject.embedSWF(videoURL, "youtube_player", "425", "356", "8", null, null, params, atts);
		
		YOUTUBE_ID = youtubeID;
		VIDEO_START = videoStart;
		
	},
	
	empty: function(){
		$("#live-video").empty();
		$("#live-video")
			.append(
				$("<div/>").attr("id","youtube_player")
			)
			.append(
				$("<div/>")
					.attr("id","progression_bar")
					.append(
						$("<div/>").attr("id", "filler")
					)
			);
	},
	
}

/* ---------- LISTENER CONTROLLER ---------- */

function ListenerController(){
	this.listeners = []
	this.duplicate_listeners = []
}

ListenerController.prototype = {
	
	init: function(listeners){
		for(i = 0, c = listeners.length; i < c; i++){
			listener = listeners[i];
			this.add(listener);
		}
	},
	
	add: function(new_listener){
		
		duplicate = false;
		//Check if user logged in not already in listener list
		if(new_listener.phonoblaster_id){
			for(j = 0, d = this.listeners.length; j<d; j++){
				listener = this.listeners[j]
				// In the case below there is a duplicate
				if(listener.phonoblaster_id == new_listener.phonoblaster_id){
					duplicate = true;
				}
			}
		}

		// If duplicate, put in duplicate list
		if(duplicate){
			this.duplicate_listeners.push(new_listener);
		}
		// Else, it's ok (this case also handles when user not logged in)
		else{
			this.listeners.push(new_listener);
			
			//Change the number of listeners
			this.update_number_of_listeners();

			this.display(new_listener);
			
		}
		
	},
	
	remove: function(old_session_id){
		
		new_listeners_list = [];
		new_duplicate_list = [];
		
		in_listeners = false;
		
		// Check which listener it is
		for(i = 0, c = this.listeners.length; i<c; i++){
			listener = this.listeners[i]
			if(old_session_id == listener.session_id){
				// Remove listener from UI
				$("#listener_items #" + old_session_id).remove();
				
				listener_to_delete = listener
				
				// Check if also in duplicate
				for(j = 0, d = this.duplicate_listeners.length; j<d; j++){
					duplicate_listener = this.duplicate_listeners[j];
					// If also in duplicate, add it in the listeners list and display it
					if(listener_to_delete.phonoblaster_id == duplicate_listener.phonoblaster_id){
						new_listeners_list.push(duplicate_listener)
												
						// Display on the UI
						this.display(duplicate_listener);
					}
					// Or just copy to the future duplicate list
					else{
						new_duplicate_list.push(duplicate_listener)
					}
				}
				
				// The listener to remove has been found in the listeners list
				in_listeners = true;
				
			}
			// Or just copy to the future listeners list
			else{
				new_listeners_list.push(listener)
			}
		}
		
		// Look in the duplicate list if not found in the listeners list
		if(!in_listeners){
			// reset the duplicate list again
			new_duplicate_list = [];
			
			for(k = 0, e = this.duplicate_listeners.length; k<e; k++){
				duplicate_listener = this.duplicate_listeners[k];
				
				if(duplicate_listener.session_id == old_session_id){
					//do nothing
				}
				// Just copy it to the future duplicate list
				else{
					new_duplicate_list.push(duplicate_listener)
				}
			}
			
		}
		
		// Do all the updates
		this.listeners = new_listeners_list;
		this.duplicate_listeners = new_duplicate_list;
		this.update_number_of_listeners();

	},
	
	update_number_of_listeners: function(){
		number_of_listeners = this.listeners.length;
		$("#number_of_listeners").html(number_of_listeners);
	},
	
	display: function(new_listener){
		
		if(new_listener.phonoblaster_id){
			//Display logged in listener
			$("#listener_items")
				.append(
					$("<a/>")
						.attr({
							"id": new_listener.session_id,
							"href": "/user/"+ new_listener.phonoblaster_id,
							"target": "_blank",
						})
						.append(
							$("<img/>")
								.attr({
									"src": "http://graph.facebook.com/" + new_listener.facebook_id + "/picture?type=square",
									"title": new_listener.public_name,
									"class": "user",
								})
						)
				)
		}
		else{
			//Display unknown listener
			$("#listener_items")
				.append(
					$("<a/>")
						.attr("id", new_listener.session_id)
						.append(
							$("<img/>").attr("src", "/static/images/unknown-listener.png")
						)
				)
		}	
		
	}
	
}

/* --------------- ERROR CONTROLLER ------------------ */

function ErrorController(tracklistManager){
	this.working_tracks = [];
	this.tracklistManager = tracklistManager;
}

ErrorController.prototype = {
	
	addTrack: function(newTrack){
		console.log("track added in the working tracks")
		this.working_tracks.push(newTrack);
	},
	
	raise: function(){
		
		// Empty div and display GIF for a few seconds...
		this.displayTransitionImage();

		console.log(this.working_tracks);
		// Removes the last video of the working videos array!
		track_not_working = this.working_tracks.pop()
		
		// Calculate the time out (the time before the video was supposed to end)
		expired_at = parseInt(track_not_working.expired,10);
		datetime_now = Date.parse(new Date());
		duration = parseInt(track_not_working.duration,10);
		time_out = expired_at - datetime_now/1000;

		// Retrieves the last video working
		if(this.working_tracks.length == 0){
			// El Guincho - Bombay is our standard track (in case there is no other working tracks in the array)
			replacing_track = {
				"id": "-CreEuaS8QY",
				"duration": "269",
			}
		}
		else{
			replacing_track = this.working_tracks[this.working_tracks.length - 1];
			if(replacing_track.duration > track_not_working.duration){
				//it's ok
			}
			else{
				replacing_track = {
					"id": "-CreEuaS8QY",
					"duration": "269",
				}
			}
		}
		
		image_display_time = 5;
		
		// Calculate the video start
		video_start = replacing_track.duration - time_out + image_display_time;

		var that = this;
		setTimeout(function(){
			// Init video player
			that.tracklistManager.youtubeController.init(replacing_track.id, video_start);
			// Display progress
			that.tracklistManager.displayProgress(video_start, replacing_track.duration);
		}, image_display_time * 1000);

		
	},
	
	displayTransitionImage: function(){
		$("#live-video").empty();
		
		$("#live-video")
			.append(
				$("<img/>")
					.attr("src","/static/images/video-error.png")
					.css("paddingLeft","1px")
			)
	},
	
	
}