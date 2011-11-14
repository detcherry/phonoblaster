/*------- YOUTUBE SEARCH -------*/

function YoutubeSearch(tracklistManager){
	this.tracklistManager = tracklistManager;
	
	// Slim scroll for the chat
	this.scrollbar = new Scrollbar("#search_tab #search_results", "310px", "445px")
		
	this.init();
}

YoutubeSearch.prototype = {
	
	init: function(){
		var that = this;
		
		//Listen to search events
		$("form#search")
			.submit(function(){
				var content = $("input[id='search_content']").val();
				that.removeResults();
				that.makeQuery(content);
				return false;
			});
		
		//Listen to keyboard events (except when user presses 'enter' because otherwise it makes 2 queries)
		$("form#search")
			.bind("keyup",function(event){
				if(event.keyCode != 13){
					$(this).submit();
				}
			})
	},
	
	makeQuery: function(content){		
		var that = this;
				
		var youtube_search_api_url = "https://gdata.youtube.com/feeds/api/videos?q=";
		var parameters ="&max-results=20&format=5&v=2&alt=jsonc&callback=?";
		var url = youtube_search_api_url + encodeURIComponent(content) + parameters;	
			
		$.getJSON(
			url,
			function(json){
				//Generate the results on the page
				if(json.data.items){
					$.each( json.data.items, function(i) {
						var item = json.data.items[i];
						that.generateResult(item);
					});
					
					that.listen();
					that.scrollbar.updateSize();
				}
			})
			.error(function() { phonoblaster.log("error"); });		
	},
	
	removeResults: function(){
		$("#search_results").empty();
	},
	
	generateResult: function(item){
		$("#search_results")
			.append(
				$("<div/>")
					.addClass("search_result")
					.attr("id", item.id)
					.append(
						$("<div/>")
							.addClass("info")
							.append(
								$("<p/>")
									.addClass("title")
									.html(item.title)
							)
							.append(
								$("<p/>")
									.addClass("id")
									.html(item.id)
							)
							.append(
								$("<p/>")
									.addClass("thumbnail")
									.html(item.thumbnail.sqDefault)
							)
							.append(
								$("<p/>")
									.addClass("duration")
									.html(item.duration)
							)
					)
					.append(
						$("<img/>")
							.attr("src",item.thumbnail.sqDefault)
							.addClass("img")
					)
					.append(
						$("<p/>")
							.addClass("title")
							.append(
								$("<span/>")
									.html(item.title)	
							)
					)
					.append(
						$("<a/>")
							.html("Add to list")
							.attr("href","#")
							.addClass("add_track")
							.addClass("button")
					)			
			);
	},
	
	listen: function(){
		var that = this;
		
		// Reset listeners
		$("a.add_track").unbind("click");
		
		//Listen to add events
		$("a.add_track")
			.click(function(){				
				var divResult = $(this).parent();
				var divInfo = divResult.find(".info");

				var title = divInfo.find(".title").html();
				var id = divInfo.find(".id").html();
				var thumbnail = divInfo.find(".thumbnail").html();
				var duration = divInfo.find(".duration").html();
				
				if(that.tracklistManager.tracklist.length < 9){
					$(this).replaceWith(
						$("<img/>")
							.attr("src","/static/images/small-ajax-loader.gif")
							.addClass("loader")
					)
					if(title && id && thumbnail && duration){
						that.addToTracklist(title, id, thumbnail, duration);
					}
				}
				else{
					phonoblaster.log("Too many songs in the list");
					that.trackNotAdded(id);
				}
				
				return false;
			});
	},
	
	addToTracklist: function(title, id, thumbnail, duration){		
		var that = this;
		var tracks_to_add = [];
		var track = {
			"title": title,
			"id": id,
			"thumbnail": thumbnail,
			"duration": duration,
		}
		tracks_to_add.push(track);
		
		$.ajax({
			url: "/track/add",
			type: "POST",
			dataType: "json",
			timeout: 60000,
			data: {
				station_key: station_key,
				tracks: JSON.stringify(tracks_to_add),
				channel_id: channel_id,
			},
			error: function(xhr, status, error) {
				phonoblaster.log('An error occurred: ' + error + '\nPlease retry.');
			},
			success: function(json){
				if(json.status == "Added"){						
					phonoblaster.log("Your song has been added to the tracklist");
					that.trackAdded(id);
					track = {
						"title": title,
						"id": id,
						"thumbnail": thumbnail,
						"duration": duration,
					}
					var tracks_to_add = [track];
					that.tracklistManager.libraryController.add_new_tracks(tracks_to_add);
				}
				else{
					phonoblaster.log("Already 10 songs in the list. Wait for a few minutes before submitting a new song");
					that.trackNotAdded(id); //to refactor does not work correctly in this case...
				}
			},
		});
	},
	
	trackAdded: function(track_id){
		$("#search_results #"+ track_id + " img.loader")
			.replaceWith(
				$("<a/>")
					.addClass("add_track")
					.addClass("success")
					.html("Added")
			)
	},
	
	trackNotAdded: function(track_id){
		var that = this;
		$("#search_results #"+ track_id + " a.add_track")
			.replaceWith(
				$("<a/>")
					.addClass("add_track")
					.addClass("danger")
					.html("List full")
			)
		$("#room_counter").popover("show")

		setTimeout(function(){
			$("#search_results #"+ track_id + " a.add_track")
				.remove();
				
			$("#search_results #"+ track_id)
				.append(
					$("<a/>")
						.attr("href","#")
						.addClass("add_track")
						.addClass("button")
						.html("Add to list")
				)
			
			$("#room_counter").popover("hide")
			
			that.listen()

		}, 3000)
	},

	
}
