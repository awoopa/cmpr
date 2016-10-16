document.addEventListener('DOMContentLoaded', function() {
	document.getElementById('status').textContent = getWPMData();
});


function getWPMData() {
	chrome.storage.local.get({'wpmData': []}, data => {
		var wpmData = data.wpmData;
		return wpmData;
	})
}

function saveWPMData(wpm) {
	chrome.storage.local.get({'wpmData': []}, data => {
		var wpmData = data.wpmData;
		wpmData.push({wpm, timestamp: Date.now()});
		chrome.storage.local.set({'wpmData': wpmData }, () => {
			chrome.storage.local.get('wpmData', res => {console.log(res)});
		})
	})
}