// ---------------------------------------------------------------------------
// COUNTER
// ---------------------------------------------------------------------------

function Counter(selector){
	this.selector = selector + " span.figure";
	this.count = parseInt($(this.selector).html(), 10);
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
		$(this.selector).html(this.count);
	},
	
}