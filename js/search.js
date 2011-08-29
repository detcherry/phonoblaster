$(function(){
	var youtube = new YoutubeSearch();
	youtube.init();
});

/*------- YOUTUBE SEARCH -------*/

function YoutubeSearch(){
}

YoutubeSearch.prototype = {
	
	init: function(){
		var that = this;
		
		$("form")
			.submit(function(){
				content = $("input[id='search_content']").val()
				that.makeQuery(content)
				return false;
			});
	},
	
	makeQuery: function(content){
		var that = this;
		that.removeResults();
		
		var youtube_search_api_url = "https://gdata.youtube.com/feeds/api/videos?q=";
		var parameters ="&max-results=10&v=2&alt=jsonc&callback=?";
		var url = youtube_search_api_url + encodeURIComponent(content) + parameters;	
			
		$.getJSON(
			url,
			function(json){
				//Generate the results on the page
				if(json.data.items){
					$.each( json.data.items, function(i) {
						item = json.data.items[i];TrackAdder
						that.generateResult(item)
					});
				}
				
				//Enable click listening
				var tracklist = new TrackAdder();
				tracklist.init();
			})
			.error(function() { alert("error"); });		
	},
	
	removeResults: function(){
		$("#content").empty();
	},
	
	generateResult: function(item){
		$("<div/>")
			.addClass("result")
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
					.attr({
						"class":"thumbnail",
						"src":item.thumbnail.sqDefault
					})
			)
			.append(
				$("<p/>")
					.html(item.title)
			)
			.append(
				$("<a/>")
					.html("Add to tracklist")
					.attr("href","#")
					.addClass("add")
			)
			.appendTo("#content");
	},
	
}

/*------- TRACKLIST MANAGER -------*/

function TrackAdder(){
}

TrackAdder.prototype = {
	
	init: function(){
		var that = this;
		
		$("a.add")
			.click(function(){
				divResult = $(this).parent();
				divInfo = divResult.children().first();
				
				title = divInfo.find(".title").html();
				id = divInfo.find(".id").html();
				thumbnail = divInfo.find(".thumbnail").html();
				duration = divInfo.find(".duration").html();
				
				that.addToTracklist(title, id, thumbnail, duration);
				
				return false;
			});
	},
	
	addToTracklist: function(title, id, thumbnail, duration){
		$.ajax({
			url: "/add",
			type: "POST",
			dataType: "json",
			timeout: 60000,
			data: {
				title: title,
				id: id,
				thumbnail: thumbnail,
				duration: duration,
			},
			error: function(xhr, status, error) {
				alert('An error occurred: ' + error + '\nPlease retry.');
			},
			success: function(json){
				if(json.status == "added"){
					alert("Your song has been added to the tracklist");
				}
				else{
					alert("Already 10 songs in the list. Wait for a few minutes before submitting a new song");
				}
			},
		});
	},
	
	
}