$(function(){
	// Drag and drop 
	var initial_position = null;
	var final_position = null;
	
	$("#buffer-tab .tab-content:nth-child(2)").sortable({
		
		items: ".item[id!=live]",
		
		// During sorting
		sort:function(event, ui){
			$(ui.helper).css("borderRight","1px solid #E1E1E1").css("borderLeft","1px solid #E1E1E1");
		},
		
		// Once sorting has stopped
		stop:function(event, ui){
			$(ui.item).css("borderRight","none").css("borderLeft","none")
			
		},
		
	});
	
})


	
