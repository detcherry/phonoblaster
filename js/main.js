$(function(){
	var tracklistController = new TracklistController();
	var youtubeController = new YoutubeController();
	var tracklistDisplayer = new TracklistDisplayer();
	
	tracklistController.init(youtubeController, tracklistDisplayer);
});

/* ----- TRACKLIST CONTROLLER ------*/

function TracklistController(){
	this.youtubeController = null;
	this.tracklistDisplayer = null;
	this.liveTrackID = null;
	this.liveTrackExpTime = null;
	this.liveTrackDuration = null;
}

TracklistController.prototype = {
	
	init: function(aYoutubeController, aTracklistDisplayer){
		console.log("Init Tracklist Controller");
		
		this.youtubeController = aYoutubeController;
		this.tracklistDisplayer = aTracklistDisplayer;
		
		this.playNext();
		
		var that = this;
		setInterval(function(){
			that.fetchNewTracks();
		},10000);
	},
	
	playNext: function(){
		console.log("Play Next Track")
		
		var liveTrack = $("#tracks").children().first();
		var liveTrackInfo = liveTrack.children().first();
		this.liveTrackID = liveTrackInfo.find(".id").html();
		
		if(this.liveTrackID){
			this.liveTrackExpTime = liveTrackInfo.find(".expiration_time").html();
			this.liveTrackDuration = parseInt(liveTrackInfo.find(".duration").html());
			
			videoStart = this.calculateVideoStart();
			timeOut = this.liveTrackDuration - videoStart;
			
			console.log("Next Track: " + this.liveTrackID);
			
			this.youtubeController.init(this.liveTrackID, videoStart);
		}
		else{
			console.log("No track found")
			
			this.liveTrackID = null;
			this.liveTrackExpTime = null;
			this.liveTrackDuration = null;
			timeOut = 10;
		}
			
		this.programNextVideo(timeOut);
	},
	
	calculateVideoStart: function(){		
		var dateConverter = new DateConverter()
		var ExpTimeDate = dateConverter.pythStringToJsDate(this.liveTrackExpTime);
		
		timezoneOffset = ExpTimeDate.getTimezoneOffset();
		var dateTimeNow = new Date();
		
		BeforeEnd = (ExpTimeDate - timezoneOffset*60*1000 - dateTimeNow)/1000;		
		videoStart = this.liveTrackDuration - parseInt(BeforeEnd);
		
		return videoStart;
	},
	
	programNextVideo: function(timeOut){
		var that = this;
		
		firstTimer = setTimeout(function(){
			that.nextVideo();
		},timeOut*1000);	
		
	},
	
	nextVideo: function(){
		this.tracklistDisplayer.removeAtTheTop(this.liveTrackID);
		
		var that = this;
		secondTimer = setTimeout(function(){
			that.playNext();
		},1000);
	},
	
	fetchNewTracks: function(){
		
		lastTrack = $("#tracks").children().last();
		lastTrackInfo = lastTrack.children().first();
		lastTrackAdditionTime = lastTrackInfo.find(".addition_time").html();
		
		if(lastTrackAdditionTime){
			additionTime = lastTrackAdditionTime;
		}
		else{
			additionTime = $("#last_request_time").html();
		}
		
		newRequestTime = this.getFormattedTime();
		$("#last_request_time").html(newRequestTime);
		console.log("Fetching new tracks at: " + newRequestTime);
		
		var that = this;
		$.ajax({
			url: "/",
			type: "POST",
			dataType: "json",
			timeout: 60000,
			data: {
				addition_time: additionTime,
			},
			error: function(xhr, status, error) {
				console.log('An error occurred: ' + error + '\nPlease retry.');
			},
			success: function(json){
				if(json.tracks){
					$.each(json.tracks, function(i) {
						track = json.tracks[i];
						title = track.title;
						id = track.id;
						thumbnail = track.thumbnail;
						duration = track.duration;
						addition_time = track.addition_time;
						expiration_time = track.expiration_time;

						that.tracklistDisplayer.addAtTheBottom(title, id, thumbnail, duration, addition_time, expiration_time);
					});
				}
			},
		});
	},
	
	getFormattedTime: function(){
		var date = new Date();
		var dateConverter = new DateConverter();
		formattedTime = dateConverter.jsDateToPythString(date);
		return formattedTime;
	},
	
}

/* ------ YOUTUBE PLAYER -------- */

function YoutubeController(){
}

YoutubeController.prototype = {
	
	init: function(youtubeID, videoStart){
		this.empty();
		
		var videoURL = "http://www.youtube.com/e/" + youtubeID + "?enablejsapi=1&autoplay=1&controls=0&playerapiid=ytplayer&start=" + videoStart;
		var params = { allowScriptAccess: "always"};
		var atts = { id: "myytplayer" };
		swfobject.embedSWF(videoURL, "youtube_player", "425", "356", "8", null, null, params, atts);
	},
	
	empty: function(){
		$("#live object").remove();
		$("#live").append(
			$("<div/>").attr("id","youtube_player")
		);
	},
	
}

/* ---- TRACKLIST DISPLAYER ----- */

function TracklistDisplayer(){
}

TracklistDisplayer.prototype = {
	
	removeAtTheTop: function(liveTrackID){
		if(liveTrackID == null){
			//Don't do anything
		}
		else{
			htmlID = "#" + liveTrackID;
			$(htmlID).first().remove();

			console.log("Track removed from the playlist: "+ liveTrackID);
		}

	},
	
	addAtTheBottom: function(title, id, thumbnail, duration, addition_time, expiration_time){		
		$("#tracks").append(
			$("<div/>")
				.addClass("track")
				.attr("id",id)
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
								.addClass("addition_time")
								.html(addition_time)
						)
						.append(
							$("<p/>")
								.addClass("expiration_time")
								.html(expiration_time)
						)
						.append(
							$("<p/>")
								.addClass("duration")
								.html(duration)
						)
				)
				.append(
					$("<img/>")
						.addClass("thumbnail")
						.attr("src",thumbnail)
				)
				.append(
					$("<p/>")
						.addClass("title")
						.html(title)
				)
				.append(
					$("<p/>")
						.addClass("duration")
						.html(duration + " sec")
				)
		)
		
		console.log("New track added to the list: " + title);
	},
	
}

/* -------- DATE CONVERTER ------ */

function DateConverter(){
}

DateConverter.prototype = {
	
	jsDateToPythString: function(aDate){
		// PythonString of a Date: 2011-08-22 13:36:56.794000
		var year = aDate.getUTCFullYear().toString();
		
		//In Javascript months are from 0 to 11
		var month = aDate.getUTCMonth() + 1;
		if(month < 10){
			month = "0" + month.toString();
		}
		var day = aDate.getUTCDate().toString();
		if(day.length == 1){
			day = "0" + day;
		}
		var hours = aDate.getUTCHours().toString();
		if(hours.length == 1){
			hours = "0" + hours;
		}
		var minutes = aDate.getUTCMinutes().toString();
		if(minutes.length == 1){
			minutes = "0" + minutes;
		}
		
		var seconds = aDate.getUTCSeconds().toString();
		if(seconds.length == 1){
			seconds = "0" + seconds;
		}
		
		var microseconds = aDate.getUTCMilliseconds().toString()+"000";
		if(microseconds.length == 4){
			microseconds = "00" + microseconds;
		}
		else if(microseconds.length == 5){
			microseconds = "0" + microseconds;
		}
		
		pythonDate = year + "-" + month + "-" + day + " " + hours + ":" + minutes + ":" + seconds + "." + microseconds;
		return pythonDate;
	},
	
	pythStringToJsDate: function(aString){
		// PythonString of a Date: 2011-08-22 13:36:56.794000
		year = aString.substr(0,4);
		month = aString.substr(5,2);
		
		//In Javascript, month digits are from 0 to 11
		if(month.substr(0,1) == "0"){
			month = month.substr(1,1);
		}
		month = parseInt(month) - 1
		
		day = aString.substr(8,2);
		hours = aString.substr(11,2);
		minutes = aString.substr(14,2);
		seconds = aString.substr(17,2);
		milliseconds = aString.substr(20,3);
				
		jsDate = new Date(year, month, day, hours, minutes, seconds, milliseconds);
		return jsDate;
	},
	
}
