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
		var maxBarHeight = 100;
		var me = $(this.divID);
		var bar = $(this.divID).parent().find(".slimScrollBar");
		
		outerHeight = me.outerHeight();
		newTotalHeight = me[0].scrollHeight;
		newBarHeight = Math.max(Math.min(0.8 * (outerHeight/ newTotalHeight) * outerHeight, maxBarHeight), minBarHeight);

		oldBarHeight = bar.height();
		
		// Calculate the old scroll height (inversely proportional to the scroll bar height)
		if(oldBarHeight != 0){
			ratio = newBarHeight/oldBarHeight;
			oldTotalHeight = newTotalHeight * ratio;
			
			contentPosition = (oldTotalHeight - outerHeight) * parseInt(bar.position().top) / (outerHeight - oldBarHeight)
			delta = contentPosition * (outerHeight - newBarHeight)/ (newTotalHeight - outerHeight);
			//delta = (oldTotalHeight - outerHeight) * (outerHeight - newBarHeight)/ (newTotalHeight - outerHeight);
		}
		else{
			delta = 0;
		}
		
		// Update scrollbar size
		bar.css("height", newBarHeight+"px");
		
		//scroll the scrollbar
		bar.css({ top: delta + 'px' });
	}
	
}