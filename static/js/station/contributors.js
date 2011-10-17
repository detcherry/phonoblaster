$(function(){
	var deleteManager = new DeleteManager();
	var fcbkRequestsManager = new FcbkRequestsManager();
});

/*------ FACEBOOK REQUESTS AND CONTRIBUTORS MANGER ----- */

function FcbkRequestsManager(){
	this.init()
}

FcbkRequestsManager.prototype = {
	
	init: function(){
		that = this;
		$("a[id='invite']")
			.bind("click", function(){
				that.displayLoadingIndicator();
				FB.ui({
					method: 'apprequests',
					message: 'You should come and post tracks to the radio station I just created: http://phonoblaster.com/' + current_station_name,
					exclude_ids: exclude_ids,
				},
				function(response){
					if(response && response.to){
						that.store(response.request, response.to);
					}
					else{
						that.removeLoadingIndicator();
					}
					return false;
				});
				return false;
			});
	},
	
	store: function(request, recipient_ids){
		recipients = recipient_ids.join(',');
		
		$.ajax({
			url: "/contribution/add",
			type: "POST",
			dataType: "json",
			timeout: 60000,
			data: {
				station_key: station_key,
				recipient_ids: recipients,
				request_id: request,
			},
			success: function(json){
	        	window.location.reload();
			},
			error: function(xhr, status, error) {
				console.log('An error occurred: ' + error + '\nPlease retry.');
			},
		});	
			
	},
	
	displayLoadingIndicator: function(){
		$("#middle-column h3")
			.prepend(
				$("<img/>")
					.attr("src", "/static/images/small-ajax-loader.gif")
					.css({
						"display":"block",
						"float":"left",
						"margin-right":"5px",
						"height":"15px",
						"border":"none"
					})
			);
	},
	
	removeLoadingIndicator: function(){
		$("#middle-column h3 img").remove()
	},
	
}

/* ----------- DELETE CONTRIBUTORS MANAGER  ------- */

function DeleteManager(){
	this.init()
}

DeleteManager.prototype = {
	
	init: function(){
		that = this;
		$("a[id='contributor-delete']")
			.bind("click", function(){				
				// Put loading indicator
				$(this)
					.find("#cross")
					.css("display","none")
				$(this)
					.find("#loader")
					.css("display","block")
				
				contribution_key = $(this).attr("name");
				
				// Send delete request
				$.ajax({
					url: "/contribution/delete",
					type: "POST",
					dataType: "json",
					timeout: 60000,
					data: {
						contribution_key: contribution_key,
					},
					success: function(json){
			        	window.location.reload();
					},
					error: function(xhr, status, error) {
						console.log('An error occurred: ' + error + '\nPlease retry.');
					},
				});	
				
				return false;			
			});
	},
	
	
}
