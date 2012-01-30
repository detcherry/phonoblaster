// ---------------------------------------------------------------------------
// COUNTER
// ---------------------------------------------------------------------------


function Counter(selector){
	this.selector = selector;
	this.count = parseInt($(selector + " strong.number").html(), 10);
	this.display();
}

Counter.prototype = {
	
	increment: function(){
		this.count++;
		this.display()
	},
	
	decrement: function(){
		this.count--;
		this.display()
	},
	
	display: function(){
		var units = this.count % 1000;
		var thousands_plus = (this.count - units)/1000;
		var thousands = thousands_plus % 1000
		var millions_plus = (thousands_plus - thousands)/1000
		
		if(millions_plus >0){
			var total = millions_plus.toString()
			if(millions_plus < 10){
				total += "," + thousands.toString()
			}
			var to_display = total.slice(0,3) + "m"
		}
		else{
			if(thousands > 0){
				var total = thousands.toString()
				if(thousands < 10){
					total += "," + units.toString()					
				}
				var to_display = total.slice(0,3) + "k"
			}
			else{
				var to_display = units;
			}
		}
		
		$(this.selector + " strong.number")
			.css("visibility", "visible")
			.html(to_display);
	},
	
}