// ---------------------------------------------------------------------------
// BACKGROUND MANAGER
// ---------------------------------------------------------------------------

BackgroundManager.prototype = new RealtimeTabManager();
BackgroundManager.prototype.constructor = BackgroundManager;

function BackgroundManager(client){
	this.init(client);
}

BackgroundManager.prototype.init = function(client){
	RealtimeTabManager.call(this, client);
	
	// Settings
	this.url = "/api/background"
	this.data_type = "json"
	
	// Init methods
	this.uploadListen();
	
	// Init background size and listen to resize events
	this.resize();
	this.resizeListen();
}

BackgroundManager.prototype.resize = function(){
	var bgImg = $("#background img");
	
	var imgwidth = bgImg.width();
	var imgheight = bgImg.height();
	
	var winwidth = $(window).width();
	var winheight = $(window).height();
	
	var widthratio = winwidth / imgwidth;
	var heightratio = winheight / imgheight;
	
	var widthdiff = heightratio * imgwidth;
	var heightdiff = widthratio * imgheight;
	
	if(heightdiff>winheight){
		bgImg.css({
			width: winwidth+'px',
			height: heightdiff+'px'
		});
    }
	else{
		bgImg.css({
			width: widthdiff+'px',
			height: winheight+'px'
		});
	}
	
	bgImg.css("opacity","1")
}

BackgroundManager.prototype.resizeListen = function(){
	
	var that = this
	$(window).resize(function(){
		that.resize();
	});
	
}

BackgroundManager.prototype.uploadListen = function(){
		
	// We listen to any image upload
	$("input[id='picture']").bind("change", function(event){
		
		// Something is submitted
		if($(this).val()){
			// Show loader
			$("#station-background img.loader").css("visibility", "visible");

			// Submit
			$("form#edit-background").submit();
		}
	})
	
	var that = this
	// We listen to any form submit event
	$("form#edit-background").bind("submit",function(){
		$(this).ajaxSubmit({
			success: that.uploadCallback,
			dataType: "json",
			timeout: 60000,
		});
		
		return false;	
	});
	
}

BackgroundManager.prototype.uploadCallback = function(responseText, statusText, xhr, form){
	
	// Hide loader
	$("#station-background img.loader").css("visibility", "hidden");
	
	var json = responseText;
	
	try{
		if(json.response){
			var full = json.src_full;			
			
			// Display new background
			CLIENT.background_manager.display(full);
		}
		else{
			if(json.error == 1){
				var message = "Picture too big.";
			}
			else if(json.error == 2){
				var message = "Only .jpeg, .jpg, .png, .gif pictures."
			}
			else{
				var message = "No picture uploaded."
			}
			
			// Display error message
			PHB.error(message);
		}
		
		// Reinitialize the form destination in case the user would like to change the picture
		$("form#edit-background").attr("action", json.blobstore_url)
	}
	catch(e){
		PHB.error("Please reload the page.")
	}	
}

BackgroundManager.prototype.pushNew = function(new_background){
	var current_background = $("#background img").attr("src")
	if(current_background != new_background){
		this.display(new_background)
	}
}

BackgroundManager.prototype.display = function(url){		
	var that = this;
	$("#background img").attr("src", url).removeAttr("style").load(function(){
		that.resize();
	})
}
