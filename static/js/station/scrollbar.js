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
		
		var oldTotalHeight = this.totalHeight;
		
		var minBarHeight = 30;
		var maxBarHeight = 100;
		var me = $(this.divID);
		var bar = $(this.divID).parent().find(".slimScrollBar");
		
		var outerHeight = me.outerHeight();
		var newTotalHeight = me.prop("scrollHeight");
		var newBarHeight = Math.max(Math.min(0.8 * (outerHeight/ newTotalHeight) * outerHeight, maxBarHeight), minBarHeight);

		var oldBarHeight = bar.height();
		
		if(oldTotalHeight == 0){
			// Sometimes when the oldTotalHeight is 0, it's not really 0... so below is a hack to bypass that.
			if(oldBarHeight != 0){
				var ratio = newBarHeight/oldBarHeight;
				oldTotalHeight = newTotalHeight * ratio;

				var contentPosition = (oldTotalHeight - outerHeight) * parseInt(bar.position().top) / (outerHeight - oldBarHeight)
				var delta = contentPosition * (outerHeight - newBarHeight)/ (newTotalHeight - outerHeight);
			}
			else{
				delta = 0;
			}
		}
		else{
			var contentPosition = (oldTotalHeight - outerHeight) * parseInt(bar.position().top) / (outerHeight - oldBarHeight)
			var delta = contentPosition * (outerHeight - newBarHeight)/ (newTotalHeight - outerHeight);
		}
		
		// Update scrollbar size
		bar.css("height", newBarHeight+"px");
		
		//scroll the scrollbar
		bar.css({ top: delta + 'px' });
		
		this.totalHeight = newTotalHeight;
	}
	
}