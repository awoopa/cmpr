document.addEventListener('DOMContentLoaded', function() {
	document.getElementById('status').addEventListener('click', () => {
		chrome.tabs.create({url: 'dataviz.html'});
	})
});

function saveWPMData(wpm) {
	chrome.storage.local.get({'wpmData': []}, data => {
		var wpmData = data.wpmData;
		var c = new Date();
		var timestamp = c.getFullYear() + '-' + (c.getMonth() + 1) + '-' +
						c.getDate() + ' ' + c.getHours() + ':' + c.getMinutes() + ':' +
						c.getSeconds();
		wpmData.push({wpm, timestamp});
		chrome.storage.local.set({'wpmData': wpmData }, () => {
			chrome.storage.local.get('wpmData', res => {console.log(res)});
		})
	})
}