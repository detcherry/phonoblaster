/* --------- SCROLLBAR CONTROLLER -------------*/

function Scrollbar(divID, divWidth, divHeight){
	this.divID = divID;
	$(this.divID).slimScroll({
        width: divWidth,
		height: divHeight,
	});
}

Scrollbar.prototype = {
	
	updateSize: function(){
		
		var minBarHeight = 30;
		var me = $(this.divID)
		outerHeight = me.outerHeight()
		scrollHeight = me[0].scrollHeight
		newHeight = Math.max(0.8 * (outerHeight/ scrollHeight) * outerHeight, minBarHeight);
		
		// Update size of the scrollbar due to size changes with the div
		$(this.divID).parent().find(".slimScrollBar").css("height", newHeight+"px");
		
	}
	
}