// ---------------------------------------------------------------------------
// YOUTUBE MANAGER
// ---------------------------------------------------------------------------

function YoutubeManager(width, height){
	this.width = width.toString();
	this.height = height.toString();
}

YoutubeManager.prototype = {
	
	init: function(youtubeID, videoStart){
		
		YOUTUBE_ID = youtubeID;
		VIDEO_START = videoStart;
		
		// Player already loaded
		try{
			ytplayer.loadVideoById(YOUTUBE_ID, VIDEO_START);
			PHB.log("Player already loaded");
		}
		// Player not loaded yet
		catch(e){
			this.empty();
					
			PHB.log("Player not loaded yet")
			var params = { 
				allowScriptAccess: "always",
				wmode: "transparent"
			};
			var atts = { id: "ytplayer" };
			var videoURL = "https://www.youtube.com/apiplayer?version=3&enablejsapi=1&playerapiid=player1"
			swfobject.embedSWF(videoURL, "youtube-player", this.width, this.height, "8", null, null, params, atts);
		}
	},
	
	empty: function(){
		$("#media").empty();
		$("#media").append($("<div/>").attr("id","youtube-player"));
	},
	
}

//Youtube PLAY & VOLUME & ERROR management
function onYouTubePlayerReady(playerId) {
	ytplayer = document.getElementById("ytplayer");
	
	// Puts handler in case the video does not work
	ytplayer.addEventListener("onError", "onPlayerError");
	
	// Triggers the video
	ytplayer.loadVideoById(YOUTUBE_ID, VIDEO_START);

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
	$("#media-volume").click(function(){
		if(VOLUME){
			//turn it off
			try{ytplayer.mute();}
			catch(e){PHB.log(e);}
			VOLUME = false;
			$(this).removeClass("unmuted").addClass("muted");
		}
		else{
			//turn it on
			try{ytplayer.unMute();}
			catch(e){PHB.log(e);}
			VOLUME = true;
			$(this).removeClass("muted").addClass("unmuted");
		}
		return false;
	});
	
})