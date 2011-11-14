$(function(){
	
	onairController = new OnAirController();
	
})

function OnAirController(){
	// Attribute initialization
	this.fetchTime = Date.parse(new Date());
	this.limit = 180000; // 3 min
	this.displayer = new OnAirDisplayer();
	
	this.listen();
	this.update();
}

OnAirController.prototype = {
	
	program: function(){
		var that = this
		
		setTimeout(function(){
			displayState = $("#onair_tab").css("display")
			if(displayState == "block"){
				// Update the tab
				that.update()
			}
		}, this.limit)
		
	},
	
	listen: function(){
		var that = this;
		$("a#onair").bind("click",function(){
			dateTimeNow = Date.parse(new Date());
			if(dateTimeNow - that.fetchTime  > that.limit){
				that.update();	
			}
		})
	},
	
	update: function(){		
		// display loading indicator
		this.displayer.displayLoading();
		
		this.fetchTime = Date.parse(new Date());
		var that = this;
		
		// fetch the new stations on the air
		$.ajax({
			url: "/station/onair",
			type: "GET",
			dataType: "json",
			timeout: 60000,
			error: function(xhr, status, error) {
				phonoblaster.log('An error occurred: ' + error + '\nPlease retry.');
			},
			success: function(json){
				// remove loading indicator
				that.displayer.removeLoading();
				
				phonoblaster.log(json)
				filtered_items = that.filter(json.items)
				
				// display stations on the air
				that.displayer.display(filtered_items)
			},
		});
		
		// program the next update
		this.program();
	},
	
	// Remove the current station from the stations on the air
	filter: function(items){
		filtered_items = [];
		
		for(i=0, c=items.length; i<c; i++){
			item = items[i];
			if(item.station_identifier != station_id){
				filtered_items.push(item)
			}
		}
		
		return filtered_items
	},
	
}

function OnAirDisplayer(){
	//Init slimscroll
	this.scrollbar = new Scrollbar("#onair_tab #onair_items", "309px", "490px");
}

OnAirDisplayer.prototype = {
	
	displayLoading: function(){
		$("#onair_tab")
			.append(
				$("<img/>")
					.attr("src", "/static/images/small-ajax-loader.gif")
					.css("height", "30px")
					.addClass("loader")
			)
	},

	removeLoading: function(){
		$("#onair_tab img.loader").remove()
	},
	
	display: function(items){
		$("#onair_items").empty();
		
		if(items.length > 0){
			// Display items
			for(i=0, c=items.length; i<c; i++){
				item = items[i];
				this.add(item);
			}
			this.scrollbar.updateSize();
		}	
		else{
			$("#onair_items")
				.append(
					$("<div/>")
						.attr("id","onair_init")
						.html("No other station on the air yet")
				)
		}
		
	},
	
	add: function(item){
		$("#onair_items")
			.append(
				$("<div/>")
					.addClass("onair_item")
					.append(
						$("<div/>")
							.addClass("left")
							.append(
								$("<a/>")
									.attr("href", "/"+item.station_identifier)
									.addClass("img")
									.append(
										$("<img/>").attr("src", "/picture/view/"+item.station_thumbnail)
									)
							)
					)
					.append(
						$("<div/>")
							.addClass("right")
							.append(
								$("<a/>")
									.attr("href", "/"+item.station_identifier)
									.append($("<h5/>").html(item.station_identifier))
									.append($("<img/>").attr("src", item.youtube_thumbnail).addClass("img"))
									.append($("<p/>").addClass("title").append($("<span/>").html(item.youtube_title)))
							)
					)
			)
		
		
	},
	
}