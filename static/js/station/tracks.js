$(function(){
	var tracksBrowser = new TracksBrowser(current_station_name, offset)
});

function TracksBrowser(station_id, offset){
	this.station = station_id;
	this.offset = parseInt(offset);
	this.init();
}

TracksBrowser.prototype = {
	
	init: function(){
		firstDivTrack = $(".track").first();
		if(firstDivTrack.length > 0){
			firstTrackInfo = firstDivTrack.find(".info");
			track_id = firstTrackInfo.find(".id").html();
			track_title = firstTrackInfo.find(".title").html();
			this.play(track_id, track_title, false);
		}
		this.listen();
	},
	
	play: function(id, title, autoplay){
		$("#station_track").empty();
		$("#station_track").append(
			$("<div/>").attr("id","youtube_player")
		);
		
		var videoURL = "http://www.youtube.com/e/" + id + "?enablejsapi=1&playerapiid=ytplayer";
		if(autoplay){
			videoURL += "&autoplay=1";
		}
		var params = { allowScriptAccess: "always"};
		var atts = { id: "myytplayer" };
		swfobject.embedSWF(videoURL, "youtube_player", "425", "356", "8", null, null, params, atts);
		
		$("#middle-column h3").html(title)
	},
	
	listen: function(){
		var that = this;
		
		// Play events
		$("a.play_old_track")
			.click(function(){
				divTrack = $(this).parent();
				divInfo = divTrack.find(".info");
				
				title = divInfo.find(".title").html();
				id = divInfo.find(".id").html();
				
				that.play(id, title, true);
				return false;
			});
		
		// Fetch events
		$("a#fetch_old_tracks")
			.click(function(){
				$(this).replaceWith(
					$("<img/>")
						.attr("src","/static/images/small-ajax-loader.gif")
						.addClass("loader")
				);
				that.fetch();
				return false;
			})
	},
	
	fetch: function(){
		var that = this;
		$.ajax({
			url: "/" + that.station + "/tracks",
			type: "POST",
			dataType: "json",
			timeout: 60000,
			data: {
				station : that.station,
				offset: that.offset,
			},
			error: function(xhr, status, error) {
				console.log('An error occurred: ' + error + '\nPlease retry.');
			},
			success: function(json){
				$("#tracks_history img.loader").remove();
				$.each(json.tracks, function(i){
					track = json.tracks[i];
					id = track.id;
					title = track.title;
					thumbnail = track.thumbnail;
					
					that.display(id, title, thumbnail)
				})
				
				if(json.tracks.length == 10){
					$("#tracks_history")
						.append(
							$("<a/>")
								.attr({
									"id":"fetch_old_tracks",
									"href":"",
								})
								.addClass("button")
								.html("Fetch older tracks")
						)
				}
				
				that.offset = parseInt(json.offset);
				that.listen();
			},
		});
		
	},
	
	display: function(id, title, thumbnail_url){
		$("#tracks_history")
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
					)
					.append(
						$("<img/>")
							.attr("src", thumbnail_url)
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
						$("<a/>")
							.attr("href","")
							.addClass("play_old_track")
							.addClass("button")
							.html("Play track")
					)
			)
		
		
	},
	
}

