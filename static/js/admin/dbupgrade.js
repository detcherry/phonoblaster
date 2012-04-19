(function(){
	$(".btn").live("click",function(){
		alert("Starting Database Unifomisation!");
		$.ajax({
			url: "/admin/upgrade",
			type: "POST",
			contentType: "application/json",
			dataType: "text",
			timeout: 60000,
			data: '{}',
			error: function(xhr, status, error) {
				alert("An error occured");
			},
			success: function(json){
				console.log(json.response);
			},
		});
	});
})();