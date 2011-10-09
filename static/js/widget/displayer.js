function WidgetDisplayer(tracks,track_history){
	this.tracks = tracks;
	this.track_history = track_history;
	this.display();
}

WidgetDisplayer.prototype = {
	
	display: function(){
		
		var that = this;
		
		$('div.songs').empty();
		
		if (that.tracks.length == 0){
			$('div.button').children('a').attr('class','button');
			$('div.button').children('a').text('Off Air');
			
			
			$('div.songs').append(
				$('<div/>')
					.addClass('no_song')
					.html('<span id="title"><b>Recently played</b></span>')
				);
			
			$('div.no_song').append(
				$('<div/>')
					.addClass('left_column')
				).append(
					$('<div/>')
						.addClass('right_column')
				);
			
			for (var i = 0; i < that.track_history.length; i++) {
				
				var track_name = that.track_history[i].youtube_title.replace(/['"]/g,'');
				
				var div = i <= 2 ? 'left_column' : 'right_column';
				
				$('div.'+div).append(
					$("<div/>")
						.addClass('next_history')
						.append(
							$("<div/>")
								.addClass('next_history_content')
								.append(
									$("<img/>")
										.attr("src",that.track_history[i].youtube_thumbnail_url)
										.attr("id","next_history_thumbnail")
								)
								.append(
									$("<div/>")
										.addClass('info')
										.html('<span class="current_track_title">'+track_name+'</span>')
								)
						)
				);
				
			}	
			
		}
		
		else {
			
			$('div.button').children('a').attr('class','button danger');
			$('div.button').children('a').text('On Air');
			
			var current_track_name = that.tracks[0].youtube_title.replace(/['"]/g,'');
			
			$('div.songs').append(
					$("<div/>")
						.addClass('current_song')
						.append(
							$("<img/>")
								.attr("src",that.tracks[0].youtube_thumbnail_url)
								.attr("id","current_song")
							)
							.append(
								$("<div/>")
									.addClass('info')
									.append(
										$("<div/>")
										.addClass('current_track_name')
										.html('<b class="current_track_title">'+current_track_name+'</b>')
									)
									.append(
										$("<div/>")
										.addClass('playing')
										.append(
											$('<div/>')
												.addClass('filler')
											)
									)
						)
			);
					
			if (that.tracks.length > 1){
				$('div.songs').append(
					$('<div/>')
						.addClass('next_songs')
					);
			}
		
			
			for (var i = 1; i < Math.min(3,that.tracks.length); i++) {
				
				var track_name = that.tracks[i].youtube_title.replace(/['"]/g,'');
				$('div.next_songs').append(
						$("<div/>")
							.addClass('next_song')							
							.append(
								$("<img/>")
									.attr("src",that.tracks[i].youtube_thumbnail_url)
									.attr("id","next_song_thumbnail")
							)			
							.append(
								$("<div/>")
									.addClass('next_song_content')
									.append(
										$("<div/>")
											.addClass('info')
											.html(track_name)
									)
							)
				);
					
			}
		
		}
					
		if (that.tracks.length > 0) {

			var now = new Date();
			var gmt_current = Date.parse(now) + now.getTimezoneOffset()*60*1000;

			var elapsed = tracks[0].youtube_duration*1000 - (Date.parse(tracks[0].expired) - gmt_current);

			var x = parseInt(elapsed*130/(tracks[0].youtube_duration*1000));

			$('div.filler').css('width',x+'px');

			$('div.filler').animate({
				width:'130px'
			},parseInt(tracks[0].youtube_duration)*1000-elapsed,'linear');
				
		}
	},
	
	
	setUpProgressBar: function() {
		if (this.tracks.length > 0) {

			var now = new Date();
			var gmt_current = Date.parse(now) + now.getTimezoneOffset()*60*1000;

			//Little work on the string for Safari support
			var str = this.tracks[0].expired.replace(/-/g,"/");
			var str_expired = new Date(str.substring(0,str.indexOf('.')));

			var elapsed = this.tracks[0].youtube_duration*1000 - (Date.parse(str_expired) - gmt_current);

			var x = parseInt(elapsed*130/(this.tracks[0].youtube_duration*1000));

			$('div.filler').css('width',x+'px');

			$('div.filler').animate({
				width:'130px'
			},parseInt(tracks[0].youtube_duration)*1000-elapsed,'linear');
		}
	}
	
}