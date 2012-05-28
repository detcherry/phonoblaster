// ---------------------------------------------------------------------------
// YOUTUBE MANAGER
// ---------------------------------------------------------------------------

function YoutubeManager(buffer_manager){
	this.buffer_manager = buffer_manager;
	this.item = null;
	
	this.scrollListen();
	this.postListen();
	this.deleteListen();
}

YoutubeManager.prototype = {
	
	init: function(item, start){
		this.item = item;
		
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
			
			// Reset fav icon if necessary
			$("#media-fav a").removeClass("unfav").addClass("fav").addClass("tuto").attr("data-original-title", "Favorite this track")
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
	
	postListen: function(){
		var that = this;

		$("a.fav").live("click", function(){
			var user = that.buffer_manager.station_client.user
			
			if(!user){
				FACEBOOK.login()
			}
			else{
				var item = that.item;

				// Change icon
				var btn = $(this)
				that.toggle(btn)

				// POST new favorite to server
				that.post(item, function(response){
					that.postCallback(btn, response)
				})

				// Post action to FACEBOOK
				that.postAction(item);
			}
			
			$(this).blur();
			return false;
			
		})
	},
	
	toggle: function(btn){
		if(btn.hasClass("fav")){
			btn.removeClass("fav").addClass("unfav").addClass("tuto").attr("data-original-title", "Unfavorite this track");
		}
		else{
			btn.removeClass("unfav").addClass("fav").addClass("tuto").attr("data-original-title", "Favorite this track");
		}
	},
	
	// Build data to POST
	postData: function(item){
		var data = {
			content: JSON.stringify(item.content),
		}
		return data
	},
	
	// POST request to server
	post: function(item, callback){
		var data = this.postData(item);
		var that = this;

		$.ajax({
			url: "/api/favorites",
			type: "POST",
			dataType: "json",
			timeout: 60000,
			data: data,
			error: function(xhr, status, error) {
				callback(false)
			},
			success: function(json){
				callback(json.response);
			},
		});
	},
	
	postCallback: function(btn, response){
		if(!response){
			this.toggle(btn);
			PHB.error("New favorite has not been stored")
		}
	},
	
	postAction: function(item){
		var track_url = PHB.site_url + "/track/" + item.content.track_id;

		var obj = { "track": track_url };
		var extra = {};
		var expires_in = 0;
		var action = "favorite";	

		FACEBOOK.putAction(action, obj, extra, expires_in);
	},
	
	deleteListen: function(){
		var that = this;

		$("a.unfav").live("click", function(){
			// Clone live item
			var item = that.item;

			// Change icon
			var btn = $(this)
			that.toggle(btn)

			that.delete_item(item, function(response){
				that.deleteCallback(btn, response)
			})

			$(this).blur();
			return false;
		})
	},
	
	delete_item: function(item, callback){
		var that = this;
		var delete_url = "/api/favorites/" + item.content.track_id
		
		$.ajax({
			url: delete_url,
			type: "DELETE",
			dataType: "json",
			timeout: 60000,
			error: function(xhr, status, error) {
				callback(false)
			},
			success: function(json){
				callback(json.response);
			},
		});
	},
	
	deleteCallback: function(btn, response){
		if(!response){
			btn.removeClass("fav").addClass("unfav");
			PHB.error("Favorite has not been deleted.")
		}
	},
	
	scrollListen: function(){
		$(window).scroll(function(){
			
			var scrollTop = $(this).scrollTop();
			var margin = scrollTop - 125;
			if(margin > 0){
				$("#no-scrolling-box").css("position","fixed").css("top","20px")
			}			
			else{
				var top = 145 - scrollTop;
								
				// Difference between Mozilla and other browsers
				if(BROWSER_DETECT.browser == "Mozilla"){
					$("#no-scrolling-box").css("top",top+"px")
				}
				else{
					$("#no-scrolling-box").css("position","static")
				}
				
			}
			
		})
	},
}

//Youtube PLAY & VOLUME & ERROR management
function onYouTubePlayerReady(playerId) {
	ytplayer = document.getElementById("ytplayer");
	
	// Puts handler in case the video does not work
	ytplayer.addEventListener("onError", "onPlayerError");
	
	// Triggers the video
	ytplayer.loadVideoById(YOUTUBE_ID, START);

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
	
	// Browser Detect Script
	BROWSER_DETECT = {
		init: function () {
			this.browser = this.searchString(this.dataBrowser) || "An unknown browser";
			this.version = this.searchVersion(navigator.userAgent)
				|| this.searchVersion(navigator.appVersion)
				|| "an unknown version";
			this.OS = this.searchString(this.dataOS) || "an unknown OS";
		},
		searchString: function (data) {
			for (var i=0;i<data.length;i++)	{
				var dataString = data[i].string;
				var dataProp = data[i].prop;
				this.versionSearchString = data[i].versionSearch || data[i].identity;
				if (dataString) {
					if (dataString.indexOf(data[i].subString) != -1)
						return data[i].identity;
				}
				else if (dataProp)
					return data[i].identity;
			}
		},
		searchVersion: function (dataString) {
			var index = dataString.indexOf(this.versionSearchString);
			if (index == -1) return;
			return parseFloat(dataString.substring(index+this.versionSearchString.length+1));
		},
		dataBrowser: [
			{
				string: navigator.userAgent,
				subString: "Chrome",
				identity: "Chrome"
			},
			{ 	string: navigator.userAgent,
				subString: "OmniWeb",
				versionSearch: "OmniWeb/",
				identity: "OmniWeb"
			},
			{
				string: navigator.vendor,
				subString: "Apple",
				identity: "Safari",
				versionSearch: "Version"
			},
			{
				prop: window.opera,
				identity: "Opera",
				versionSearch: "Version"
			},
			{
				string: navigator.vendor,
				subString: "iCab",
				identity: "iCab"
			},
			{
				string: navigator.vendor,
				subString: "KDE",
				identity: "Konqueror"
			},
			{
				string: navigator.userAgent,
				subString: "Firefox",
				identity: "Firefox"
			},
			{
				string: navigator.vendor,
				subString: "Camino",
				identity: "Camino"
			},
			{		// for newer Netscapes (6+)
				string: navigator.userAgent,
				subString: "Netscape",
				identity: "Netscape"
			},
			{
				string: navigator.userAgent,
				subString: "MSIE",
				identity: "Explorer",
				versionSearch: "MSIE"
			},
			{
				string: navigator.userAgent,
				subString: "Gecko",
				identity: "Mozilla",
				versionSearch: "rv"
			},
			{ 		// for older Netscapes (4-)
				string: navigator.userAgent,
				subString: "Mozilla",
				identity: "Netscape",
				versionSearch: "Mozilla"
			}
		],
		dataOS : [
			{
				string: navigator.platform,
				subString: "Win",
				identity: "Windows"
			},
			{
				string: navigator.platform,
				subString: "Mac",
				identity: "Mac"
			},
			{
				   string: navigator.userAgent,
				   subString: "iPhone",
				   identity: "iPhone/iPod"
		    },
			{
				string: navigator.platform,
				subString: "Linux",
				identity: "Linux"
			}
		]

	};
	BROWSER_DETECT.init();
		
})


