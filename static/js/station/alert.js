// ---------------------------------------------------------------------------
// ALERT MANAGER
// ---------------------------------------------------------------------------

$(function(){
	$(window).focus(function(){
		FOCUS = true;
	})
	$(window).blur(function(){
		FOCUS = false;
	})
	FOCUS = true;
})


function AlertManager(station_client, title, li){
	this.init = station_client.station.name;
	this.title = title;
	this.li = li;
	this.current = null;
}

AlertManager.prototype = {
	
	alert: function(){
		// Clear previous alert
		this.clear();
		
		// Set new alert in the document title
		var that = this;
		if(!FOCUS){
			var new_alert = setInterval(function(){
				if(document.title != that.init){
					document.title = that.init;
				}
				else{
					document.title = that.title;
				}
			}, 2000)
			this.current = new_alert;
		}
		
		// Remove alert if focus on page
		$(window).focus(function(){
			that.clear();
		})
	},
	
	clear: function(){
		var previous_alert = this.current;
		if(previous_alert){
			clearInterval(previous_alert)
		}
		this.current = null;
		document.title = this.init;
	},
}
