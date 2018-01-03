let apiURL = "https://water-logger.herokuapp.com";

function showLogger() {
	"use strict";
	document.getElementById("loggedOut").style.display = "none";
	document.getElementById("loggedIn").style.display = "block";
}

function hideLogger() {
	"use strict";
	document.getElementById("loggedOut").style.display = "block";
	document.getElementById("loggedIn").style.display = "none";
}

function today() {
	"use strict";
	let d = new Date();
	let todayClasses = document.querySelectorAll(".today");

	let i;
	for (i = 0; i < todayClasses.length; i += 1) {
		todayClasses[i].innerText = d.toDateString();
	}
}

function fillIntake() {
	"use strict";
	fetch(`${apiURL}/today`, {
		method: "GET",
		credentials: "include"
	}).then(function (response) {
		return response.json();
	}).then(function (data) {
		document.getElementById("todaysIntake").innerText = data.today.amount;
	});
}

function addWater() {
	"use strict";

	let water = {"water": document.getElementById("oz").value};

	fetch(`${apiURL}/today`, {
		method: "POST",
		credentials: "include",
		body: JSON.stringify(water)
	}).then(function (response) {
		if (response.status === 200) {
			fillIntake();
			document.getElementById("oz").value = 0;
		}
	});
}

function checkSession() {
	"use strict";
	fetch(`${apiURL}/today`, {
		method: "GET",
		credentials: "include"
	}).then(function (response) {
		if (response.status === 404 || response.status === 401) {
			hideLogger();
		} else if (response.status === 201 || response.status === 200) {
			showLogger();
		}

		return;
	});
}

function login() {
	"use strict";

	let username = document.getElementById("username");
	let password = document.getElementById("password");

	if (username.value !== "" && password !== "") {
		let loginInfo = {
			"username": username.value,
			"encrypted_password": password.value
		};

		fetch(`${apiURL}/authenticate`, {
			method: "POST",
			credentials: "include",
			body: JSON.stringify(loginInfo)
		}).then(function (response) {
			if ((response.status < 200 && response.status > 299) || (response.status === 404) || (response.status === 401)) {
				console.log("UNAUTHENTICATED");
			} else {
				showLogger();
			}
		});
	}
}

window.onload = function () {
	"use strict";
	today();
	fillIntake();
	checkSession();
};
