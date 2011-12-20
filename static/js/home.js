$(function(){
	var stationCreateManager = new StationCreateManager();
})

function StationCreateManager(){
	this.listen();
	this.page_id = null;
	this.page_name = null;
}

StationCreateManager.prototype = {
	
	listen: function(){
		var that = this;
		$(".contribution a.btn").click(function(){
			var obj = $(this);
			that.page_id = $(this).attr("id");
			that.page_name = $(this).parent().prev().children().first().html();

			// Display loader gif
			$(this).prev().css("visibility", "visible")
			
			/*
			setTimeout(function(){
				that.displayStationCreated(obj, true, true);
			}, 2000)*/
			
			
			// Make ajax call
			that.createStation(function(station_created, name_availability){
				that.displayStationCreated(obj, station_created, name_availability);
			})
			
			return false;
		})
	},
	
	createStation: function(callback){
		var that = this;
		if(this.page_id){
			$.ajax({
				url: "/station/create",
				type: "POST",
				dataType: "json",
				timeout: 60000,
				data: {
					page_id: that.page_id,
					/*page_shortname: that.page_shortname,*/
				},
				error: function(xhr, status, error) {
					phb.log('An error occurred: ' + error + '\nPlease retry.');
					callback.call(this, false, null)
				},
				success: function(json){
					//callback.call(this, json.station_created, json.name_availability)
					callback.call(this, json.station_created)
				},
			});
		}
	},
	
	displayStationCreated: function(obj, station_created, name_availability){
		phb.log("Callback called")
		
		// Hide loader gif
		obj.prev().css("visibility", "hidden");
		
		// Build text to display
		var repl = $("<span/>").addClass("btn");
		if(station_created){
			repl.addClass("success").html("Created!");
		}else{
			repl.addClass("danger").html("Error...");
		}
		
		// Replace link by text
		obj.replaceWith(repl);
		
		// Display popup if response positive
		if(station_created){
			var stationConfirmManager = new StationConfirmManager(this.page_id, this.page_name);
		}
	},
}