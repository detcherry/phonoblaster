/* --------- SCROLLBAR CONTROLLER -------------*/

function Scrollbar(divID, divWidth, divHeight){
	this.divID = divID;
	$(this.divID).slimScroll({
        width: divWidth,
		height: divHeight,
	});
	
	this.totalHeight = 0;
}

Scrollbar.prototype = {
	
	updateSize: function(){
		
		oldTotalHeight = this.totalHeight;
		
		var minBarHeight = 30;
		var maxBarHeight = 100;
		var me = $(this.divID);
		var bar = $(this.divID).parent().find(".slimScrollBar");
		
		outerHeight = me.outerHeight();
		newTotalHeight = me.prop("scrollHeight");
		newBarHeight = Math.max(Math.min(0.8 * (outerHeight/ newTotalHeight) * outerHeight, maxBarHeight), minBarHeight);

		oldBarHeight = bar.height();
		
		if(oldTotalHeight == 0){
			// Sometimes when the oldTotalHeight, it's not really 0... so below is a hack to bypass that.
			if(oldBarHeight != 0){
				ratio = newBarHeight/oldBarHeight;
				oldTotalHeight = newTotalHeight * ratio;

				contentPosition = (oldTotalHeight - outerHeight) * parseInt(bar.position().top) / (outerHeight - oldBarHeight)
				delta = contentPosition * (outerHeight - newBarHeight)/ (newTotalHeight - outerHeight);
			}
			else{
				delta = 0;
			}
		}
		else{
			contentPosition = (oldTotalHeight - outerHeight) * parseInt(bar.position().top) / (outerHeight - oldBarHeight)
			delta = contentPosition * (outerHeight - newBarHeight)/ (newTotalHeight - outerHeight);
		}
		
		// Update scrollbar size
		bar.css("height", newBarHeight+"px");
		
		//scroll the scrollbar
		bar.css({ top: delta + 'px' });
		
		this.totalHeight = newTotalHeight;
	}
	
}