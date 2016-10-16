var timerStart;
var numWords;
function colourize() {
	var html = document.documentElement.innerHTML;
	console.log("colourize()");

	fetch('http://52.43.238.240:5000/convert_html', {
		method: 'POST',
		body: JSON.stringify({
			page: html,
			host: window.location.origin,
			host_rel: window.location.pathname
		})
	}).then(res => {
		res.json().then(data => {
			document.documentElement.innerHTML = data.html;
			numWords = data.count;
			timerStart = Date.now();
		})
	})
}

var state = false;

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
	if (request.getState) {
		sendResponse({state: state});
	}
});


chrome.runtime.onMessage.addListener(
	function(request, sender, sendResponse) {
		if (request.colourize) {
			if (!state) {
			  colourize();
			  console.log('COLOURIZING');
			} else {
			    var timer = Date.now() - timerStart;
				var wpm = Math.round((numWords/(timer/1000))*60);
				console.log(`WPM: ${wpm}`)
				chrome.runtime.sendMessage({wpm: wpm});
			}
			state = !state;
			sendResponse({state:state});
		}
});