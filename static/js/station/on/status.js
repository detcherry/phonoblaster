// ---------------------------------------------------------------------------
// STATUS MANAGER
// ---------------------------------------------------------------------------

function StatusManager(station_client){
	this.station_client = station_client;
	this._status = "not on air";
	this.latest_signal_time = PHB.now();
	
	this.init();
	if(this.station_client.admin){
		this.listen();
	}
}

StatusManager.prototype = {
	
	init: function(){
		var that = this;
		setInterval(function(){
			var live_item = that.station_client.queue_manager.live_item;
			if(live_item){
				that.setStatus("on air")
			}
			else{
				that.setStatus("not on air")
			}
		}, 1000)
	},
	
	new: function(status){
		if(!this.station_client.admin){
			this.setStatus(status);
		}
	},
	
	setStatus: function(new_status){
		this._status = new_status;
		this.displayStatus();
	},
	
	listen: function(){
		var that = this;
		$("input#comment").focus(function(){
			that.postStatus("commenting");
		})
		
		$("input#comment").keyup(function(){
			that.postStatus("commenting");
		})
		
		$("input#comment").blur(function(){
			that.postStatus("on air")
		})

		$("input#search").focus(function(){
			that.postStatus("searching")
		})
		
		$("input#search").keyup(function(){
			that.postStatus("searching")
		})
		
		$("input#search").blur(function(){
			that.postStatus("on air")
		})
		
		$("ul#tabs a").click(function(){
			var href = $(this).attr("href");
			var status = null;
			if(href == "#queue-tab"){
				 status = "on air"
			}
			if(href == "#suggestions-tab"){
				status = "looking at people suggestions"
			}
			if(href == "#favorites-tab"){
				status = "looking at its favorite tracks"
			}
			if(href == "#library-tab"){
				status = "looking at its latest broadcasts"
			}
			that.postStatus(status);
		})
	},
	
	postStatus: function(new_status){
		this.setStatus(new_status);
		
		if(this.station_client.admin){
			
			var that = this
			var people_connected = that.station_client.session_manager.sessions_counter;
			// If more than one person connected
			if(people_connected.length > 0){
				
				// Rate limit the number of messages sent per second: max 1 every 10 seconds
				if(PHB.now() - this.latest_signal_time > 10){
					this.latest_signal_time = PHB.now();
					PHB.log("post status")

					// Ajax call
					$.ajax({
						url: "/api/status",
						type: "POST",
						dataType: "json",
						timeout: 60000,
						data: {
							shortname: that.station_client.station.shortname,
							content: that._status,
						},
						error: function(xhr, status, error) {
							PHB.log('An error occurred: ' + error + '\nPlease retry.');
						},
						success: function(json){},
					});
				}
			}
				
		}
	},
	
	displayStatus: function(){
		var that = this;
		$("#station-status em").html(that._status);
	},
	
}