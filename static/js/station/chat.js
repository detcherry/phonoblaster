/* ------------- CHAT CONTROLLER ------------- */

function ChatController(){
	this.user_id = user_id;
	this.user_public_name = user_public_name;
	this.user_fcbk_id = user_fcbk_id;
	
	// Slim scroll for the chat
	this.scrollbar = new Scrollbar("#conversation", "500px", "114px")
}

ChatController.prototype = {
	
	init: function(messages){
		var that = this;
		
		//Supposed to respond to the chat_init dispatch message
		for(i = 0, c = messages.length; i < c; i++){
			var message = messages[i];
			this.display(message);
		}
		
		//Starts listening to focus events in the chat form
		$("#typebox input#chat_content")
			.focus(function(){
				//Clear the input text
				$(this).val("")
			})
		
		//Starts listening to submit events in the chat form
		$("form#chat")
			.submit(function(){
				var content = $("input[id='chat_content']").val();
				if(content.length > 0){
					date = Date.parse(new Date())/1000;
					
					//Display message in the zone
					var message = {
						text: content,
						author_id : that.user_id,
						author_fcbk_id: that.user_fcbk_id,
						author_public_name: that.user_public_name,
						added: date,
					}		
					that.display(message);
					
					//Empty the chat box
					$("input[id='chat_content']").val("");
					
					//Send the message to the world
					that.send(content);
				}
				return false;
			})
	},
	
	receive: function(content){
		//Supposed to respond to the chat_new dispatch message
		this.display(content);
	},
	
	send: function(content){
		$.ajax({
			url: "/message/add",
			type: "POST",
			dataType: "json",
			timeout: 60000,
			data: {
				station_key: station_key,
				channel_id: channel_id,
				text: content,
			},
			error: function(xhr, status, error) {
				console.log('An error occurred: ' + error + '\nPlease retry.');
			},
			success: function(json){
				if(json.status == "Added"){					
					//Do nothing. Message has already been displayed!
					console.log("Message sent to everyone: "+ content)
				}
			},
		});
		
	},
	
	display: function(message){
		//Date handling
		var date = new Date(parseInt(message.added)*1000);
		var hours = parseInt(date.getHours());
		if(hours < 10){
			hours = "0" + hours.toString()
		}
		var minutes = parseInt(date.getMinutes());
		if(minutes < 10){
			minutes = "0" + minutes.toString();
		}
		var date_to_display = hours +":"+minutes;
		
		//Links handling
		var re = /(http:)\/\/(\w+:{0,1}\w*@)?(\S+)(:[0-9]+)?(\/|\/([\w#!:.?+=&%@!\-\/]))?/;
		var occurrences = re.exec(message.text);
		try{
			var link = occurrences.shift();
			var newRe = new RegExp(link,"g");
			var text_to_display = message.text.replace(newRe, "<a href=" + link + " target='_blank'>" + link + "</a>");
		}
		catch(e){
			//do nothing
			var text_to_display = message.text;
		}
		
		//Display messages in the chat zone
		$("#conversation")
			.prepend(
				$("<div/>")
					.addClass("message")
					.append(
						$("<div/>")
							.addClass("author")
							.append(
								$("<a/>")
									.attr("target","_blank")
									.attr("href", "/user/" + message.author_id)
									.html(message.author_public_name)
							)
					)
					.append(
						$("<div/>")
							.addClass("content")
							.html(text_to_display)
					)
					.append(
						$("<div/>")
							.addClass("date")
							.html(date_to_display)
					)
			)
		
		
		//If the window is not focused, put a number in the title
		if(!window_focus){
			console.log("have to display something");
			var old_title = document.title;
			var re = new RegExp("[(]{1}[0-9]+[)]{1}","g");
			var array = re.exec(old_title);
			
			//If there is already a number in the title. Add +1
			if(array){
				var number_between_brackets = array[0];
				var re2 = new RegExp("[0-9]+","g");
				var number = parseInt(re2.exec(number_between_brackets));
				var new_number = number + 1;
				var new_number_between_brackets = "("+ new_number + ")";
				var new_title = old_title.replace(re, new_number_between_brackets);
			}
			else{
				//Else, put (1) in the title
				var new_title = "(1) " + old_title;
			}
			document.title = new_title;
		}
		
		//Update slimscroll
		this.scrollbar.updateSize();
	}
	
}
