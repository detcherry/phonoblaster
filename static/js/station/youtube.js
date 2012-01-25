// ---------------------------------------------------------------------------
// YOUTUBE MANAGER
// ---------------------------------------------------------------------------

function YoutubeManager(){
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
			var videoURL = "http://www.youtube.com/apiplayer?version=3&enablejsapi=1&playerapiid=player1"
			swfobject.embedSWF(videoURL, "youtube-player", "510", "287", "8", null, null, params, atts);
		}
	},
	
	empty: function(){
		$("#player-wrapper").empty();
		$("#player-wrapper").append($("<div/>").attr("id","youtube-player"));
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
	PHB.log("Error: track not working");
}

$(function(){
	
	//Listen to volume events
	VOLUME = true;
	$("#volume a").click(function(){
		if(VOLUME){
			//turn it off
			try{ytplayer.mute();}
			catch(e){PHB.log(e);}
			VOLUME = false;
			$("#volume img#on").css("display","none");
			$("#volume img#off").css("display","inline");
		}
		else{
			//turn it on
			try{ytplayer.unMute();}
			catch(e){PHB.log(e);}
			VOLUME = true;
			$("#volume img#on").css("display","inline");
			$("#volume img#off").css("display","none");			
		}//*/
		return false;
	});
	
})