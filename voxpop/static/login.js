/*jslint browser: true, plusplus: true, sloppy: true */
/*global */
/* jshint -W100 */

function getVoxpopConfig(voxpopUuid) {
	var xmlhttp = new XMLHttpRequest();
	xmlhttp.open( "GET", `/api/voxpops/{{ voxpopUuid }}`, false );
	xmlhttp.withCredentials = true;
	xmlhttp.send();
	if(xmlhttp.readyState == 4) {
		var resp = JSON.parse(xmlhttp.responseText);
	}
	for (var i in resp[0]) {
		if (i == "allow_anonymous") {
			var allow_anonymous = resp[0][i];
		}
	}
	return allow_anonymous;
}

function get_user_status() {
	var xmlhttp = new XMLHttpRequest();
	xmlhttp.open( "GET", "/api/voxpops/whoami", false );
	xmlhttp.withCredentials = true;
	xmlhttp.send();
	if(xmlhttp.readyState == 4) {
		var resp = JSON.parse(xmlhttp.responseText);
	}
	for (var i in resp) {
		if (i == "display_name") {
			return true;
		}
	}
	return false;
}

function login(token) {
	var xmlhttp = new XMLHttpRequest();
	xmlhttp.withCredentials = true;
	var url = '/api/voxpops/login';
	xmlhttp.open('POST', url, true);
	xmlhttp.send(JSON.stringify({ "token": token.split("#")[1] }));
	if(xmlhttp.readyState == 4) {
		var resp = JSON.parse(xmlhttp.responseText);
		console.log(resp);
	}
}

(function () {
	if (!getVoxpopConfig()) {
		console.log("Anonymous not allowed");
		if (!get_user_status()) {
			console.log("Not logged in");
			if (window.location.hash) {
				var hash = window.location.hash;
				console.log("Logging in with: " + hash);
				login(window.location.hash);
				history.pushState("", document.title, window.location.pathname + window.location.search);
				console.log("sleeping...");
				ms => new Promise(r => setTimeout(r, ms));
				if (get_user_status()) {
					console.log("You are now logged in with #jwt-token");
					return;
				}
				throw new Error('Invalid token');
			}
			alert("You are not logged in.");
			// Needs to be a variable.
			window.location.replace(`https://logon.semaphor.dk?url=${document.location}/login&js=1`);
			return;
		}
		console.log("You are logged in already!");
		return;
	}
	console.log("Anonymous allowed");
}());
