/* ------------- CHAT CONTROLLER ------------- */

function ChatController(){
	this.user_id = user_id;
	this.user_public_name = user_public_name;
	this.user_fcbk_id = user_fcbk_id;
}

ChatController.prototype = {
	
	init: function(messages){
		var that = this;
		
		//Supposed to respond to the chat_init dispatch message
		
		for(i = 0, c = messages.length; i < c; i++){
			message = messages[i];
			this.display(message);
		}
		
		//Starts listening to submit events in the chat form
		$("form#chat")
			.submit(function(){
				content = $("input[id='chat_content']").val();
				if(content.length > 0){
					date = Date.parse(new Date())/1000;
					
					//Display message in the zone
					message = {
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
		
		//Data handling
		date = new Date(parseInt(message.added)*1000);
		hours = parseInt(date.getHours());
		if(hours < 10){
			hours = "0" + hours.toString()
		}
		
		minutes = parseInt(date.getMinutes());
		if(minutes < 10){
			minutes = "0" + minutes.toString();
		}
		date_to_display = hours +":"+minutes;
		
		//Links handling
		re = /(http:)\/\/(\w+:{0,1}\w*@)?(\S+)(:[0-9]+)?(\/|\/([\w#!:.?+=&%@!\-\/]))?/;
		occurrences = re.exec(message.text);
		try{
			link = occurrences.shift();
			newRe = new RegExp(link,"g");
			text_to_display = message.text.replace(newRe, "<a href=" + link + " target='_blank'>" + link + "</a>");
		}
		catch(e){
			//do nothing
			text_to_display = message.text;
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
			old_title = document.title;
			re = new RegExp("[(]{1}[0-9]+[)]{1}","g");
			array = re.exec(old_title);
			
			if(array){
				//number = parseInt(array[0]);
				//new_number = number + 1;
				//new_title = old_title.replace(re, new_number);
				number_between_brackets = array[0];
				re2 = new RegExp("[0-9]+","g");
				number = parseInt(re2.exec(number_between_brackets));
				new_number = number + 1;
				new_number_between_brackets = "("+ new_number + ")";
				new_title = old_title.replace(re, new_number_between_brackets);
			}
			else{
				console.log("just insert 1");
				new_title = "(1) " + old_title;
			}
			document.title = new_title;
		}
		
	}
	
}
