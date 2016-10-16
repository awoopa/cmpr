document.addEventListener('DOMContentLoaded', function() {
	document.getElementById('enableTagging').addEventListener('click', () => {
		var state = document.getElementById('enableTagging').checked;
		chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
		  chrome.tabs.sendMessage(tabs[0].id, {colourize: state}, function(response) {
		    //console.log(response.farewell);
		  });
		});
	});

	document.getElementById('status').addEventListener('click', () => {
		chrome.tabs.create({url: 'dataviz.html'});
	});
});