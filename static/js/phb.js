$(function(){
	PHB = new PhB();
})

// Global object
function PhB(){
	this.facebook_app_id = FACEBOOK_APP_ID;
	this.version = VERSION;
	this.site_url = SITE_URL;
	this.time_delta = null;
}
PhB.prototype = {
	// Workaround for Firefox 3.6 and older versions
	log: function(content){
		if(console){
			console.log(content);
		}
	},
	
	// Fetch time on the server (because we can never trust the local clock...)
	time: function(callback){
		var that = this;
		$.ajax({
			url: "/api/now",
			type: "GET",
			dataType: "json",
			timeout: 60000,
			error: function(xhr, status, error){
				that.log(error);
			},
			success: function(json){
				var time = json.time;
				that.time_delta = Date.parse(new Date())/1000 - time;
				callback();
			},
		});
	},
	
	now: function(){
		var now = Date.parse(new Date())/1000 - this.time_delta;
		return now;
	},
	
	error: function(error){
		this.popup(
			$("<div/>")
				.addClass("phb-popup-error")
				.append($("<img/>").attr("src", "/static/images/icon.png"))
				.append($("<p/>").html(error + " <br/><br/>Please try again later."))
			,{
			autoSize: false,
			width: 400,
			maxWidth: 400,
			height: 100,
			maxHeight: 100,
			topRatio: 0.3,
		});
	},
	
	// Trigger a popup containing HTML
	popup: function(html, options){
		$.fancybox(html, options);
	},
	
	// Converts seconds since epoch into a human readable time
	convert: function(time){					
		var date = new Date(parseInt(time)*1000);
		var hours = parseInt(date.getHours());
		if(hours < 10){
			hours = "0" + hours.toString()
		}
		var minutes = parseInt(date.getMinutes());
		if(minutes < 10){
			minutes = "0" + minutes.toString();
		}
		
		var displayed_time = hours +":"+minutes;
		return displayed_time;					
	},
	
	// Converts seconds of a duration into a human readable duration
	convertDuration: function(duration){
		var seconds = parseInt(duration,10) % 60;
		var minutes = (parseInt(duration, 10) - seconds)/60
		if(seconds < 10){
			seconds = "0"+ seconds.toString();
		}
		var displayed_duration = minutes.toString() + ":" + seconds;
		return displayed_duration;
	},
	
}
