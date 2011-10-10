$(function(){
	new WidgetUpdater(identifier);
});

function WidgetUpdater(identifier){
	this.isFirstInit = true;
	this.num_listeners = 0;
	this.fetcher = new WidgetFetcher(identifier);
	this.tracks = [];
	this.track_history = [];
	this.init();
}

WidgetUpdater.prototype = {
	
	init: function(){
		
		//Get the timeout right depending on the existence of a current_song
		var timeout;
		if (this.isFirstInit) {
			timeout = 0
			this.isFirstInit = false;
		}
		else if (this.tracks.length > 0) {
			
			//Little work on the string for Safari support
			var str = this.tracks[0].expired.replace(/-/g,"/");
			var str_expired = new Date(str.substring(0,str.indexOf('.')));
			
			var expired = Date.parse(str_expired);
			var now = new Date();
			var gmt_current = Date.parse(now) + now.getTimezoneOffset()*60*1000;
			timeout = expired - gmt_current;
		}
		//If no song, we recheck 2mns later
		else timeout = 120000;
		
		var that = this;
		timer = setTimeout(function(){
				var content = that.fetcher.fetchContent(that);
			},
			timeout);
	},
	
	contentArrived: function(new_tracks,num_listeners){
		this.tracks = new_tracks;
		this.num_listeners = num_listeners;
		if (this.tracks.length == 0) {
			this.track_history = this.fetcher.fetchHistory(this);
		}
		else 
			new WidgetDisplayer(this.tracks,[],this.num_listeners);
		this.init();
	},
	
	
	historyArrived: function(history){
		new WidgetDisplayer([],history,this.num_listeners);
	}
	
}