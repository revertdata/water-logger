let apiURL = "https://water-logger.herokuapp.com";

let startNumbering = false;
let daysCount = 1;
let currProgress = 0;

function fillMonths() {
	"use strict";

	// Month name, DOW month starts, number of days in month \\
	let monthsNames = {0: ["January", 1, 31], 1: ["Februrary", 4, 28], 2: ["March", 4, 31], 3: ["April", 0, 30], 4: ["May", 2, 31], 5: ["June", 5, 30], 6: ["July", 0, 31], 7: ["August", 3, 31], 8: ["September", 6, 30], 9: ["October", 1, 31], 10: ["November", 4, 30], 11: ["December", 6, 31]};
	
	let months = document.querySelectorAll(".month");
	let dowNames = ["S", "M", "T", "W", "R", "F", "S"];

	let d = new Date();

	for (let i=0; i <= d.getMonth(); i++) {
		let currMonth = months[i];
		
		let monthTitle = document.createElement("h2");
		monthTitle.innerText = monthsNames[i][0];

		currMonth.appendChild(monthTitle);
		currMonth.appendChild(document.createElement("hr"));

		let weekDays = document.createElement("div");

		fetch(`${apiURL}/logs/${monthsNames[i][0]}`, {
				method: "GET"
		}).then(function (response) {
			return response.json();
		}).then(function (data) {

			for (let l=0; l < 7; l++) {
				let dow = document.createElement("div");
				dow.className = "row dow";
				dow.innerText = dowNames[l];
				weekDays.appendChild(dow);
			}

			currMonth.appendChild(weekDays);

			for (let j=0; j < 6; j++) {
				let week = document.createElement("div");
				week.className = "row week";

				for (let k=0; k < 7; k++) {
					let day = document.createElement("div");
					day.className = "row day";

					if (j == 0 && k == monthsNames[i][1]) {
						startNumbering = true;
					}

					if (startNumbering && daysCount <= monthsNames[i][2]) {
						day.className += " dayInMonth";

						let monthInfo = data['logs'];

						for (let n=0; n < monthInfo.length; n++) {
							if (monthInfo[n]['did'] == daysCount) {
								if (monthInfo[n]['amount'] != 0) {
									day.innerText = monthInfo[n]['amount'];
									day.className += " filled";
								}
							}
						}

						if (daysCount == d.getDate()) {
							day.className += " today";
						}

						if (day.innerText >= 50) {
							day.className += " goalMet";
							currProgress++;
						}

						day.id = `${monthsNames[i][0]}-${daysCount}`;
						daysCount++;
					} else {
						startNumbering = false;
						daysCount = 1;
					}

					week.appendChild(day);
				}

				currMonth.appendChild(week);
			}
		}).then(function() {
			document.getElementById("goalProgress").innerText = currProgress;
		})
	}

	for (let o = d.getMonth()+1; o < 12 - d.getMonth(); o++) {
		months[o].style.display = "none";
	}
}

fillMonths();