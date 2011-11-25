$(function(){
	oauth = {
		loginClick: function() {
			oauth.win = window.open('/oauth/request',
									'OAuthTwitterRequest',
									'width=800,height=450,modal=yes,alwaysRaised=yes'
									);
			if(!oauth.win) return true;
			return false;
		},
		logoutClick: function(){
			$.getJSON('/oauth/logout', function(){
				// Necessary to put a settimeout otherwise the cookie is not removed
				setTimeout(function(){
					window.location.reload();
				},0);
			});
		}
	};
	$("a.login").click(function(){
		oauth.loginClick();
		return false;
	});
	$("a.logout").click(function(){
		oauth.logoutClick();
		return false;
	})
})