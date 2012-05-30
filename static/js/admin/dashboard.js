(function(){
	$("#put-admin").live("click",function(){
		alert("Filling buffers !");

		$.ajax({
			url: "/admin/upgrade",
			type: "POST",
			dataType: "application/json",
			timeout: 60000,
			data: {},
			error: function(xhr, status, error) {
				console.log("An error occured");
			},
			success: function(json){
				console.log(json.response);
			},
		});
	});
})();