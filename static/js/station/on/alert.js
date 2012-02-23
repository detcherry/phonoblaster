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


function AlertManager(station_client, title, a){
	this.init = station_client.station.name;
	this.title = title;
	this.a = a;
	this.current = null;
	
	this.listen();
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
		
		this.show();
	},
	
	clear: function(){
		var previous_alert = this.current;
		if(previous_alert){
			clearInterval(previous_alert)
		}
		this.current = null;
		document.title = this.init;
	},
	
	listen: function(){
		var that = this;
		
		// Remove alert if focus on page
		$(window).focus(function(){
			that.clear();
		})
		
		var selector = this.a
		$(selector).click(function(){
			that.hide();
		})
	},
	
	show: function(){
		var link_selector = this.a
		$(link_selector).addClass("alert");
		
		var round_selector = this.a + " span.round"
		$(round_selector).show();
	},
	
	hide: function(){
		var link_selector = this.a
		$(link_selector).removeClass("alert");
				
		var round_selector = this.a + " span.round"
		$(round_selector).hide();
	},
}
