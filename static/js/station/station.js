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
		dispatcher.dispatch(json_parse(m.data));
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
	
});

/* ------------- VOLUME MANAGEMENT -------------- */

//Youtube Volume Management
function onYouTubePlayerReady(playerId) {
    ytplayer = document.getElementById("myytplayer");

	//If the volume had been turned off, mute the player
	if(!volume){
		ytplayer.mute();
	}
}

/* --------- DISPATCHER --------- */

function Dispatcher(){
	this.tracklistManager = new TracklistManager();
	this.chatController = new ChatController();
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
			//Init the number of listeners
			number_of_listeners = data.content;
			$("#number_of_listeners").html(number_of_listeners);
		}
		if(data.type == "listener_new"){
			console.log("listener_new");
			//Add +1 to the number of listeners counter
			number_of_listeners = parseInt($("#number_of_listeners").html(),10) + 1;
			$("#number_of_listeners").html(number_of_listeners);			
		}
		if(data.type == "listener_delete"){
			console.log("listener_delete");
			//Add -1 to the number of listeners counter
			number_of_listeners = parseInt($("#number_of_listeners").html(),10) - 1;
			$("#number_of_listeners").html(number_of_listeners);		
		}
			
	},
}

/* --------- TRACKLIST MANAGER ------------ */

function TracklistManager(){
	this.tracklist = [];
	this.uiTracklistController = new UITracklistController();
	this.youtubeController = new YoutubeController();
	this.searchController = new YoutubeSearch(this);
	this.shuffleController = new ShuffleController(this);
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
			
			console.log("▶ New track launched: "+ this.new_track.title + " at " + video_start.toString() +" sec")	
			this.youtubeController.init(this.new_track.id, video_start);
			this.displayInformation(video_start);
			
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
	
}

/* ------ UI TRACKLIST CONTROLLER -------- */

function UITracklistController(){
}


UITracklistController.prototype = {
	
	display: function(tracklist){
		for(i = 0, c = tracklist.length; i < c; i++){
			track = tracklist[i];
			this.add(track);
		}
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
										.attr("src", "http://graph.facebook.com/" + track.submitter_fcbk_id + "/picture?type=square")
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
				},
				error: function(xhr, status, error) {
					console.log('An error occurred: ' + error + '\nPlease retry.');
				},
				success: function(json){
					if(json.status == "deleted"){						
						console.log("Your song has been removed from the tracklist");
					}
					else{
						console.log("Your song hasn't been remove from the tracklist");
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
		
		var videoURL = "http://www.youtube.com/e/" + youtubeID + "?enablejsapi=1&autoplay=1&controls=0&playerapiid=ytplayer&start=" + videoStart;
		var params = { allowScriptAccess: "always"};
		var atts = { id: "myytplayer" };
		swfobject.embedSWF(videoURL, "youtube_player", "425", "356", "8", null, null, params, atts);
		
	},
	
	empty: function(){
		$("#live-video").empty();
		$("#live-video").append(
			$("<div/>").attr("id","youtube_player")
		);
	},
	
}
