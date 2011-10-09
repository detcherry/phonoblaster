$(function(){
	
	//Fetch tracks in the playlist and tracks history
	var fetcher = new WidgetFetcher(identifier);
	var tracks = fetcher.getTracks();
	var history = fetcher.fetchHistory();	
	
	var displayer = new WidgetDisplayer(tracks,history);
	displayer.setUpProgressBar();
	
	//Class to update the widget
	new WidgetUpdater(tracks,identifier);
				
});

