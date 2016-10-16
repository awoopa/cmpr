document.addEventListener('DOMContentLoaded', () => {
	var ctx = document.getElementById('wpmChart');

	getWPMData().then(wpmData => {

		var labels = [];
		var nums = [];
		wpmData.map(e => {
			labels.push(e.timestamp);
			nums.push(e.wpm);
		});

		var wpmChart = new Chart(ctx, {
			type: 'line',
			data: {
				labels: labels,
				datasets: [{
					label: 'Reading Speed',
					fill: false,
		            lineTension: 0.1,
		            backgroundColor: "rgba(75,192,192,0.4)",
		            borderColor: "rgba(75,192,192,1)",
		            borderCapStyle: 'butt',
		            borderDash: [],
		            borderDashOffset: 0.0,
		            borderJoinStyle: 'miter',
		            pointBorderColor: "rgba(75,192,192,1)",
		            pointBackgroundColor: "rgba(75,192,192,1)",
		            pointBorderWidth: 1,
		            pointHoverRadius: 5,
		            pointHoverBackgroundColor: "rgba(75,192,192,1)",
		            pointHoverBorderColor: "rgba(220,220,220,1)",
		            pointHoverBorderWidth: 2,
		            pointRadius: 5,
		            pointHitRadius: 10,
		            data: nums,
		            spanGaps: false,

				}]
			},
			options: {
				response: false,
				maintainAspectRatio: false,
				scales: {
					xAxes: [{
						type: 'time'
					}]
				}
			}
		});		
	})
});


function getWPMData() {
	return new Promise((resolve, reject) => {
		chrome.storage.local.get({'wpmData': []}, function (items) {
			if (chrome.runtime.lastError) {
				reject();
			};

			resolve(items.wpmData);
		})
	})
}
