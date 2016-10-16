document.addEventListener('DOMContentLoaded', function() {
	var state = false;
	chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
	  chrome.tabs.sendMessage(tabs[0].id, {getState: true}, function(response) {
	    state = response.state;

	    document.getElementById('enableTagging').checked = state;
	  });
	});


	document.getElementById('enableTagging').addEventListener('click', () => {
		chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
		  chrome.tabs.sendMessage(tabs[0].id, {colourize: true}, function(response) {
    	    document.getElementById('enableTagging').checked = response.state;
		  });
		});
	});

	document.getElementById('status').addEventListener('click', () => {
		chrome.tabs.create({url: 'dataviz.html'});
	});
});