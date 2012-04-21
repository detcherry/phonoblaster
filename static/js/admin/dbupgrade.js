(function(){
	$("#track-up").live("click",function(){
		alert("Starting Track Unifomisation!");

		$.ajax({
			url: "/admin/upgrade",
			type: "POST",
			dataType: "application/json",
			timeout: 60000,
			data: {type:"track"},
			error: function(xhr, status, error) {
				console.log("An error occured");
			},
			success: function(json){
				console.log(json.response);
			},
		});
	});


	$("#air-up").live("click",function(){
		alert("Starting Air Unifomisation!");

		$.ajax({
			url: "/admin/upgrade",
			type: "POST",
			dataType: "application/json",
			timeout: 60000,
			data: {type:"air"},
			error: function(xhr, status, error) {
				console.log("An error occured");
			},
			success: function(json){
				console.log(json.response);
			},
		});
	});


	$("#suggestion-up").live("click",function(){
		alert("Starting Database Unifomisation!");

		$.ajax({
			url: "/admin/upgrade",
			type: "POST",
			dataType: "application/json",
			timeout: 60000,
			data: {type:"suggestion"},
			error: function(xhr, status, error) {
				console.log("An error occured");
			},
			success: function(json){
				console.log(json.response);
			},
		});
	});
})();