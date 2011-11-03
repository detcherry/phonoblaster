$(function(){
	
	//Handles picture upload
	var pictureUploader = new PictureUploader();
	
	//Handles identifier (available or not, display station URL)
	var stationIDManager = new StationIDManager();
	
	//Handles submit
	var submitHandler = new SubmitHandler();
});

/* --------------- PICTURE UPLOADER -------------------- */

function PictureUploader(){
	this.init();
}

PictureUploader.prototype = {
	
	init: function(){
		var that = this;
		
		//We listen to any image upload
		$("input[id='picture']")
			.bind("change", function(event){
				that.triggerUpload()
			})
		
		//We change the way it's submitted	
		var options = {
			success: that.showResponse,
			dataType: "json",
			timeout: 60000,
		};
		$("#picture_upload")
			.bind("submit",function(){
				$(this).ajaxSubmit(options);
				return false;	
			});
	},
	
	triggerUpload: function(){
		this.startLoadingAnimation();
		$("#picture_upload").submit();
	},
	
	startLoadingAnimation: function(){		
		$("#picture_upload img")
			.show();
	},
	
	//Post submit Callback 
	showResponse: function(responseText, statusText, xhr, $form){ 
		//Stop Loading animation
		$("#picture_upload img")
			.hide();
		
		$("#picture_upload .error")
			.remove();
			
		$("#image_wrapper")
			.empty();
		
		json = responseText;
		
		try{
			if(json.upload_error){
				$("input[id='picture']")
					.parent()
					.prepend(
						$("<div/>")
							.addClass("error")
							.html(json.upload_error)
					)
			}
			else{
				//Find if some images had already been uploaded to the blobstore
				var existing_picture_input = $("input[id='blob_key']");
				var existing_thumbnail_input = $("input[id='thumbnail_blob_key']");

				if(existing_picture_input.attr("value")){
					var existing_picture_blob_key = existing_picture_input.attr("value");
					var existing_thumbnail_blob_key = existing_thumbnail_input.attr("value");

					//Delete the existing picture from the blobstore
					$.ajax({
						url: "/picture/delete",
						type: "POST",
						dataType: "json",
						timeout: 30000,
						data: {
							blob_key : existing_picture_blob_key,
						},
						success: function(json){
							existing_picture_input.remove();
						},
						error: function(xhr, status, error) {
							console.log('An error occurred: ' + error + '\nPlease retry.');
						}
					});

					//Delete the existing thumbnail from the blobstore
					$.ajax({
						url: "/picture/delete",
						type: "POST",
						dataType: "json",
						timeout: 30000,
						data: {
							blob_key : existing_thumbnail_blob_key,
						},
						success: function(json){
							existing_thumbnail_input.remove();
						},
						error: function(xhr, status, error) {
							console.log('An error occurred: ' + error + '\nPlease retry.');
						}
					});

				}

				//Insert in the 2nd form an hidden field with the blob key
				$("#create_station")
					.append(
						$("<input/>")
							.css("display","none")
							.attr({
								"type":"text",
								"name":"blob_key",
								"id":"blob_key",
								"value":json.blob_key,
							})
					)
					.append(
						$("<input/>")
							.css("display","none")
							.attr({
								"type":"text",
								"name":"thumbnail_blob_key",
								"id":"thumbnail_blob_key",
								"value":json.thumbnail_blob_key,
							})					
					);

				//Insert the image in the form
				$("#image_wrapper")
					.prepend(
						$("<div/>")
							.attr("id","thumbnail")
							.append(
								$("<img/>")
									.attr("src",json.thumbnail_url)
									.addClass("img")
							)
							.append(
								$("<span/>")
									.html("Thumbnail")
							)
					)
					.prepend(
						$("<div/>")
							.attr("id","image")
							.append(
								$("<img/>")
									.css("max-width","200px")
									.css("max-height","200px")
									.attr("src",json.image_url)
									.addClass("img")
							)
							.append(
								$("<span/>")
									.html("Image")
							)
					);


			}

			//Reinitialize the form destination in case the user would like to change the picture
			$("#picture_upload")
				.attr("action", json.blobstore_url)
		}
		catch(e){
			$("#picture_upload img")
				.remove();
			
			$("input[id='picture']")
				.parent()
				.prepend(
					$("<div/>")
						.addClass("error")
						.html("An error occured. Please refresh this page.")
				);
		}
		
	},
	
}

/*---------------- STATION ID MANGER --------------------*/

function StationIDManager(){
	this.stationID = ""
	this.init();
}

StationIDManager.prototype = {
	
	init: function(){
		var that = this;
		$("input[id='identifier']")
			.bind("keyup",function(event){
				that.keyUpHandler();
			});
	},
	
	keyUpHandler: function(){
		var re = new RegExp("[^a-zA-Z0-9_]","g");
		var oldInputValue = $("input[id='identifier']").val();
		var newInputValue = oldInputValue.replace(re,"");
		
		this.stationID = newInputValue.toLowerCase();
		$("input[id='identifier']").val(this.stationID);
		
		if(this.stationID.length > 3){
			this.checkIfAvailable();
		}
		else{
			$("#availability")
				.css("color","red")
				.html("More than 3 characters");
		}
		
		this.displayNewURL();	
	},

	checkIfAvailable: function(){
		$("#availability")
			.css("color","black")
			.html('<img src="/static/images/small-ajax-loader.gif" class="loader"/>Checking if available');
		
		$.ajax({
			url: "/station/check",
			type: "POST",
			dataType: "json",
			timeout: 60000,
			data: {
				station_id : this.stationID,
			},
			success: function(json){
				if(json.available == "True"){
					$("#availability")
						.css("color","green")
						.html("Available");
				}
				else{
					$("#availability")
						.css("color","red")
						.html("Not available");
				}
			},
			error: function(xhr, status, error) {
				console.log('An error occurred: ' + error + '\nPlease retry.');
			},
		});
		
	},
	
	displayNewURL: function(){
		$("em#station_id")
			.html(this.stationID);
	},
	
}

/* ---------------- SUBMIT HANDLER ------------------- */

function SubmitHandler(){
	this.init()
}

SubmitHandler.prototype = {
	
	init: function(){
		var that = this;
		$("input[type='submit']")
			.bind("click", function(){
				if(that.everythingOk()){
					//Do nothing
				}
				else{
					$(this)
						.parent()
						.find(".error")
						.remove();
					
					$(this)
						.parent()
						.prepend(
							$("<div/>")
								.addClass("error")
								.html("Please, give us a picture and a correct identifier for your station.")
						);
					return false;
				}
			})
	},
	
	everythingOk: function(){
		var pictureOk = false;
		var thumbnailOk = false;
		var identifierOk = false;
		
		if($("input[id='blob_key']").attr("value")){
			pictureOk = true;
		}
		
		if($("input[id='thumbnail_blob_key']").attr("value")){
			thumbnailOk = true;
		}
		
		var station_id_availability = $("#availability").html();
		if(station_id_availability == "Available"){
			identifierOk = true;
		}
		
		if(pictureOk && thumbnailOk && identifierOk){
			return true;
		}
		else{
			return false;
		}
		
	}
	
}
