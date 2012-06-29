$(function(){
	WELCOME_MANAGER = new WelcomeManager()
})

function WelcomeManager(){
	this.scrollListen();
}

WelcomeManager.prototype = {
	
	scrollListen: function(){
		var that = this;
		$(window).scroll(function(){

			var y = $(window).scrollTop()		

			// Slide 1: light gets turned on
			if(y>$("#slide1a").position().top){
				$("#slide1b").show()
			}
			else{
				$("#slide1b").hide()
			}
			
			var scrollStart2 = $("#slide2a").position().top - $("#slide2a").height()/2;
			var scrollEnd2 = $("#slide2a").position().top + $("#slide2a").height()
			that.move("#slide2b", "backgroundPositionX", scrollStart2, scrollEnd2, -$(window).width(), $(window).width())

			// Slide 3
			var scrollStart3 = $("#slide3a").position().top - $("#slide3a").height();
			var scrollEnd3 = $("#slide3a").position().top;
			that.move("#slide3b", "backgroundPositionY", scrollStart3, scrollEnd3, $(window).height(), 0)
			that.move("#slide3c", "backgroundPositionX", scrollStart3, scrollEnd3, -$(window).width(), 0)
			that.move("#slide3d", "backgroundPositionX", scrollStart3, scrollEnd3, $(window).width(), 0)
			that.move("#slide3e", "backgroundPositionY", scrollStart3, scrollEnd3, $(window).height(), 0)

			var state = y % 100

			// Slide 5: medal rotating
			if(state < 33){
				$("#slide5b").show()
				$("#slide5c").hide()
				$("#slide5d").hide()
			}
			else if(state < 66){
				$("#slide5b").hide()
				$("#slide5c").show()
				$("#slide5d").hide()
			}
			else{
				$("#slide5b").hide()
				$("#slide5c").hide()
				$("#slide5d").show()
			}

			// Slide 6: Youtube / Soundcloud
			var y5 = $("#slide6a").position().top + 200;
			if(y<y5){
				$("#slide6b").hide();
			}
			else{
				$("#slide6b").show();
			}

			// Slide 7: board shining
			if(state<50){
				$("#slide7b").hide();
			}
			else{
				$("#slide7b").show();
			}
			
			// Slide 8: crowd getting closer
			var scrollStart8 = $("#slide8a").position().top - $("#slide8a").height();
			var scrollEnd8 = $("#slide8a").position().top;
			that.move("#slide8b", "backgroundPositionX", scrollStart8, scrollEnd8, -$(window).width(), 0)
			that.move("#slide8c", "backgroundPositionX", scrollStart8, scrollEnd8, $(window).width(), 0)
			that.move("#slide8d", "backgroundPositionY", scrollStart8, scrollEnd8, $(window).width(), 0)
			
			// Slide 9: discover music 
			var scrollStart9 = $("#slide9a").position().top - $("#slide9a").height();
			var scrollEnd9 = $("#slide9a").position().top;
			that.move("#slide9b", "backgroundPositionY", scrollStart9, scrollEnd9, -$(window).width(), 0)
			
			// Slide 11: bring their friends
			var scrollStart11 = $("#slide11a").position().top - $("#slide11a").height();
			var scrollEnd11 = $("#slide11a").position().top;
			that.move("#slide11c", "backgroundPositionX", scrollStart11, scrollEnd11, $(window).width(), 0)
			
			if($(window).scrollTop() > scrollEnd11){
				$("#slide11b").show()
			}
			else{
				$("#slide11b").hide()
			}
			
		})
	},
	 
	move: function(selector, property, scroll_start, scroll_end, value_start, value_end){
		var position = $(window).scrollTop();
		
		if(position > scroll_start){
			if(position < scroll_end){
				var value = (value_end - value_start) * (position - scroll_start)/(scroll_end - scroll_start) + value_start
				this.convert(property, value, function(p, v){
					$(selector).css(p, v)
				})				
			}
			else{
				this.convert(property, value_end, function(p, v){
					$(selector).css(p, v)
				})
			}
		}
		else{
			this.convert(property, value_start, function(p, v){
				$(selector).css(p, v)
			})			
		}	
	},
	
	convert: function(property, value, callback){
		var final_property = property;
		var final_value = value;
		if(property == "backgroundPositionX"){
			final_property = "backgroundPosition";
			final_value = value.toString() + "px 0px"		
		}
		else if(property == "backgroundPositionY"){
			final_property = "backgroundPosition";
			final_value = "center " + value.toString() + "px"
		}
		
		callback(final_property, final_value)
	}	
}
