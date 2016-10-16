var timerStart;
var numWords;
function colourize() {
	var html = document.documentElement.innerHTML;
	console.log("colourize()");

	numWords = Math.random() * 100 + 10;

	timerStart = Date.now();
}

chrome.runtime.onMessage.addListener(
	function(request, sender, sendResponse) {
		console.log(request.colourize);
		if (request.colourize === true) {
		  colourize();
		  console.log('COLOURIZING');
		} else if (request.colourize === false) {
		    var timer = Date.now() - timerStart;
			var wpm = Math.round((numWords/(timer/1000))*60);
			console.log(`WPM: ${wpm}`)
			chrome.runtime.sendMessage({wpm: wpm});
		}
});