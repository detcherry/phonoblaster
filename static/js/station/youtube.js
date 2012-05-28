// ---------------------------------------------------------------------------
// YOUTUBE MANAGER
// ---------------------------------------------------------------------------

function YoutubeManager(){
}

YoutubeManager.prototype = {
	
	init: function(item, start){
		YOUTUBE_ID = item.content.youtube_id;
		START = start;
		var duration = item.content.youtube_duration;
		
		// Triggers the player
		this.play(YOUTUBE_ID, START);
		
		// Display information
		this.display(item);
		
		// Show progress
		this.progress(start, duration)
	},
	
	play: function(youtube_id, start){
		// Player already loaded
		try{
			ytplayer.loadVideoById(youtube_id, start);
			setTimeout(function(){
				// If medium quality available
				if(ytplayer.getAvailableQualityLevels().indexOf("medium") != -1){
					ytplayer.setPlaybackQuality("medium");
				}
			},1000)
			
			PHB.log("Player already loaded");
		}
		// Player not loaded yet
		catch(e){					
			PHB.log("Player not loaded yet")
			var params = { 
				allowScriptAccess: "always",
				wmode: "transparent"
			};
			var atts = { id: "ytplayer" };
			var videoURL = "https://www.youtube.com/apiplayer?version=3&enablejsapi=1&playerapiid=player1"
			swfobject.embedSWF(videoURL, "youtube-player", 400, 225, "8", null, null, params, atts);
		}
	},
	
	display: function(item){
		var id = item.id;
		var content = item.content;
		var type = content.type;

		var youtube_title = content.youtube_title;
		var youtube_duration = PHB.convertDuration(content.youtube_duration);
		var youtube_thumbnail = "https://i.ytimg.com/vi/" + content.youtube_id + "/default.jpg";

		var track_submitter_name = content.track_submitter_name;
		var track_submitter_url = content.track_submitter_url;
		var track_submitter_picture = "https://graph.facebook.com/" + content.track_submitter_key_name + "/picture?type=square";

		// Display the image
		$("#media-picture").empty().append($("<img/>").attr("src", youtube_thumbnail));

		// Display the title
		$("#media-title").html(youtube_title);

		// Put the item id in the div
		$("#media-id").html(id);

		// Display the submitter
		$("#media-submitter").empty();

		var mention = null;
		if(type == "suggestion"){
			mention = "Suggested by"
		}
		if(type == "favorite"){
			mention = "Rebroadcast of"
		}

		if(mention){
			// Display the submitter
			$("#media-submitter")
				.append(
					$("<a/>")
						.attr("href", track_submitter_url)
						.attr("target", "_top")
						.append(
							$("<img/>")
								.attr("src", track_submitter_picture)
								.addClass("tuto")
								.attr("data-original-title", track_submitter_name)
						)
				)
				.append($("<span/>").html(mention))
		}

		// Show favorite button
		if(content.track_id){
			$("#media-fav").css("visibility","visible")
		}
	},
	
	progress: function(start, duration){
		var width = $("#media-bar").width()

		var x = parseInt(start*width/duration);
		$('#media-bar-filler').css('width', x.toString() + 'px');

		$("#media-bar-filler").clearQueue();
		$('#media-bar-filler').animate({
			width: width.toString()+"px",
		}, (duration - start)*1000,'linear');

	},
}

//Youtube PLAY & VOLUME & ERROR management
function onYouTubePlayerReady(playerId) {
	ytplayer = document.getElementById("ytplayer");
	
	// Puts handler in case the video does not work
	ytplayer.addEventListener("onError", "onPlayerError");
	
	// Triggers the video
	ytplayer.loadVideoById(YOUTUBE_ID, START);
	setTimeout(function(){
		// If medium quality available
		if(ytplayer.getAvailableQualityLevels().indexOf("medium") != -1){
			ytplayer.setPlaybackQuality("medium");
		}
	},1000)

	//If the volume had been turned off, mute the player
	if(!VOLUME){
		ytplayer.mute();
	}
}

function onPlayerError(){	
	PHB.log("Error: Youtube Track not working");
}

$(function(){
	
	//Listen to volume events
	VOLUME = true;
	$("#media-volume a").click(function(){
		if(VOLUME){
			//turn it off
			try{ytplayer.mute();}
			catch(e){PHB.log(e);}
			VOLUME = false;
			$(this)
				.removeClass("unmuted")
				.addClass("muted")
				.attr("data-original-title", "Unmute the player");
		}
		else{
			//turn it on
			try{ytplayer.unMute();}
			catch(e){PHB.log(e);}
			VOLUME = true;
			$(this)
				.removeClass("muted")
				.addClass("unmuted")
				.attr("data-original-title", "Mute the player");
		}
		return false;
	});
	
})