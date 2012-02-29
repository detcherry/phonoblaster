// ---------------------------------------------------------------------------
// EMBEDDED YOUTUBE MANAGER
// ---------------------------------------------------------------------------

function EmbeddedYoutubeManager(onStateChangeManager, width, height){
	this.width = width.toString();
	this.height = height.toString();
	ON_STATE_CHANGE_MANAGER = onStateChangeManager;
}

EmbeddedYoutubeManager.prototype = {
	
	init: function(youtube_id){
		
		YOUTUBE_ID = youtube_id;
		
		// Player already loaded
		try{
			ytplayer.loadVideoById(YOUTUBE_ID);
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
			var videoURL = "https://www.youtube.com/v/" + YOUTUBE_ID + "?version=3&enablejsapi=1&playerapiid=player1"
			swfobject.embedSWF(videoURL, "youtube-player", this.width, this.height, "8", null, null, params, atts);
		}
		
	},
	
	empty: function(){
		$("#media").empty();
		$("#media").append($("<div/>").attr("id","youtube-player"));
	},
	
}

function onYouTubePlayerReady(playerId) {
	ytplayer = document.getElementById("ytplayer");
	
	// Puts handler in case the video does not work
	ytplayer.addEventListener("onError", "onPlayerError");
	
	// Put handler for video state changes
	ytplayer.addEventListener("onStateChange", "onPlayerStateChange")
	
	// Triggers the video
	ytplayer.loadVideoById(YOUTUBE_ID);
}

function onPlayerError(){	
	PHB.log("Error: Youtube Track not working");
}

function onPlayerStateChange(new_state){	
	// Video ended
	if(new_state == 0){		
		ON_STATE_CHANGE_MANAGER.nextVideo();
	}
}


