// ---------------------------------------------------------------------------
// PLAYER MANAGER
// ---------------------------------------------------------------------------

function PlayerManager(buffer_manager){
	this.buffer_manager = buffer_manager;
	this.item = null;
	
	this.postListen();
	this.deleteListen();
}

PlayerManager.prototype = {
	
	init: function(item, start){
		this.item = item;
		
		// Triggers the player
		this.play(item, start);
		
		// Display info
		this.display(item);
		
		// Show progress
		var duration = item.content.duration;
		this.progress(start, duration);
	},
	
	play: function(item, start){
		// Stop current player
		this.stop();
		
		// Youtube player
		if(item.content.type == "youtube"){
			this.playYoutube(item, start);
		}
		// Soundcloud player
		else{
			this.playSoundcloud(item, start);
		}
		
		var timeout = item.content.duration - start;
		this.transition(timeout);
	},
	
	stop: function(){
		// Remove above layer
		this.removeAbove();
		// Stop Youtube streaming
		this.stopYoutube();
		// Stop Soundcloud streaming
		this.stopSoundcloud();
	},
	
	stopYoutube: function(){
		try{ytplayer.pauseVideo();}
		catch(e){}
	},
	
	stopSoundcloud: function(){
		try{SC.streamStopAll();}
		catch(e){}
	},
	
	hideSoundcloud: function(){
		$("#soundcloud-player").hide();
	},
	
	hideYoutube: function(){
		$("#media object").css("marginLeft","-1000px");
	},
	
	removeAbove: function(){
		$("#above-player").remove();
	},
		
	playYoutube: function(item, start){
		this.hideSoundcloud();
		
		var id = item.content.id;
		$("#media object").css("marginLeft","0px");			
		ytplayer.loadVideoById(id, start,"medium");	
	},
	
	playSoundcloud: function(item, start){
		this.hideYoutube();
		
		var id = item.content.id;
		var thumbnail = item.content.thumbnail;
		var re = new RegExp("large","g");
		var artwork = thumbnail.replace(re, "t300x300")
		
		SC.stream(
			"/tracks/" + id,
			{
				autoPlay: true,
				position: start * 1000,
			},
			function(sound){
				scplayer = sound;
								
				// Unlike Youtube player, volume needs to be refreshed for every Soundcloud song
				if(VOLUME){
					scplayer.setVolume(100);
				}
				else{
					scplayer.setVolume(0);
				}
			}
		)
		
		// Show soundcloud
		$("#soundcloud-player")
			.empty()
			.append(
				$("<img/>").attr("src", artwork)
			)
			.show()
	},
	
	transition: function(timeout){		
		setTimeout(function(){
			if(VOLUME){
				try{
					ytplayer.setVolume(80);
					scplayer.setVolume(80);
				}
				catch(e){}
			}
		}, (timeout-5)*1000)
		
		setTimeout(function(){
			if(VOLUME){
				try{
					ytplayer.setVolume(60);
					scplayer.setVolume(60);
				}
				catch(e){}
			}
		}, (timeout-4)*1000)
		
		setTimeout(function(){
			if(VOLUME){
				try{
					ytplayer.setVolume(40);
					scplayer.setVolume(40);
				}
				catch(e){}
			}
		}, (timeout-3)*1000)
		
		setTimeout(function(){
			if(VOLUME){
				try{
					ytplayer.setVolume(20);
					scplayer.setVolume(20);
				}
				catch(e){}
			}
		}, (timeout-2)*1000)
		
		setTimeout(function(){
			if(VOLUME){
				try{
					ytplayer.setVolume(0);
					scplayer.setVolume(0);
				}
				catch(e){}
			}
		}, (timeout-1)*1000)
		
		setTimeout(function(){
			if(VOLUME){	
				try{
					ytplayer.setVolume(100);
					scplayer.setVolume(100);
				}
				catch(e){}
			}
		}, (timeout)*1000)
	},
	
	display: function(item){
		var id = item.id;
		var content = item.content;
		var type = content.type;
		var title = content.title;
		var duration = PHB.convertDuration(content.duration);
		var thumbnail = content.thumbnail;
		var track_submitter_name = content.track_submitter_name;
		var track_submitter_url = content.track_submitter_url;
		var track_submitter_picture = "https://graph.facebook.com/" + content.track_submitter_key_name + "/picture?type=square";

		// Display the image
		$("#media-picture").empty().append($("<img/>").attr("src", thumbnail).addClass(type));

		// Display the title
		$("#media-title").html(title);

		// Display the submitter
		$("#media-submitter").empty();

		var mention = null;
		// If submitter different than host, display rebroadcast mention
		if(this.buffer_manager.client.host.key_name != content.track_submitter_key_name){
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
			var user = that.buffer_manager.client.listener
			
			if(!user){
				FACEBOOK.login()
			}
			else{
				var item = that.item;

				// Change icon
				var btn = $(this)
				that.toggle(btn)

				// POST new favorite to server
				that.postAjax(item, function(response){
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
	postAjax: function(item, callback){
		var data = this.postData(item);
		var that = this;

		$.ajax({
			url: "/api/likes",
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
			PHB.error("New favorite has not been stored.")
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

			that.deleteAjax(item, function(response){
				that.deleteCallback(btn, response)
			})

			$(this).blur();
			return false;
		})
	},
	
	deleteAjax: function(item, callback){
		var that = this;
		var delete_url = "/api/likes/" + item.content.track_id
		
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
	
}

$(function(){
	
	//Listen to volume events
	VOLUME = true;
	$("#media-volume a").click(function(){
		if(VOLUME){
			//turn it off
			try{ytplayer.mute();}
			catch(e){PHB.log(e);}
			try{scplayer.setVolume(0);}
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
			try{scplayer.setVolume(100);}
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
