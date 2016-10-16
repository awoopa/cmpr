document.addEventListener('DOMContentLoaded', function() {
	var state = false;
	chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
	  chrome.tabs.sendMessage(tabs[0].id, {getState: true}, function(response) {
	    state = response.state;

	    document.getElementById('enableTagging').checked = state;

    	chrome.tabs.sendMessage(tabs[0].id, {getSummary: true}, function (summaries) {
    	    var summary = document.getElementById('summary-holder');

		    summaries.summary.forEach(e => {
		    	var el = document.createElement('li');
		    	el.innerText = e;
		    	summary.appendChild(el);
		    })
    	});
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

	document.getElementById('speak').addEventListener('click', () => {
		chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
		  chrome.tabs.sendMessage(tabs[0].id, {getText: true}, function(response) {
		  });
		});
	})
});