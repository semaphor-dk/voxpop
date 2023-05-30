/*jslint browser: true, plusplus: true, sloppy: true */
/* jshint -W100 */
(function() {
	'use strict';
	var allSse = [];
	let voxpopElements = document.querySelectorAll('*[data-voxpop-uuid*="-"]');
	voxpopElements.forEach(function (voxpopElm) {
		let hostPort = (voxpopElm.dataset.voxpopHost) ? `//${ voxpopElm.dataset.voxpopHost }` : '';
		let questionsUrl = `${ hostPort }/api/voxpops/${ voxpopElm.dataset.voxpopUuid }/questions`;
		renderVoxpop(voxpopElm, questionsUrl);
		var sse = new EventSource(`${ hostPort }/stream/questions/${ voxpopElm.dataset.voxpopUuid }/`, {withCredentials: true});
		allSse.push(sse);
		sse.onopen = function (evt) {
			updateConnectionStatus(voxpopElm, evt.target.readyState);
		};
		sse.onerror = function (evt) {
			updateConnectionStatus(voxpopElm, evt.target.readyState);
		};
		sse.addEventListener("new_question", function (evt) {
			let data = JSON.parse(evt.data);
			console.log(data);
			voxpopElm.insertAdjacentHTML("afterbegin", createHTMLforQuestion(data));
		});
		sse.addEventListener("new_vote", function (evt) {
			let data = JSON.parse(evt.data);
			let voteDisplayElm = document.querySelector(`div[data-voxpop-question-uuid="${ data.question_id }"] .votes span`);
			if (voteDisplayElm) {
				voteDisplayElm.innerText = data.vote_count;
			}
		});
		updateConnectionStatus(voxpopElm, sse.readyState);
	});

	function updateConnectionStatus(voxpopElm, state) {
		voxpopElm.className = ["connecting", "live", "disconnected"][state];
	}

	function createHTMLforQuestion(q) {
		return `<div data-voxpop-question-uuid="${ q.uuid }">
	<blockquote>${ q.text }</blockquote>
	<div class="DisplayName">- ${ q.display_name }</div>
	<div class="votes"><span>${q.vote_count || 0 }</span> votes</div>
	<button type="button" class="vote">Vote</button>
</div>\n`;
	}

	function renderVoxpop(voxpopElm, questionsUrl) {
		let xhr = new XMLHttpRequest();
		xhr.open("get", questionsUrl, true);
		xhr.withCredentials = true;
		xhr.onload = function () {
			if (this.status >= 200 && this.status < 300) {
				let questions = JSON.parse(xhr.response);
				let fragment = "\n";
				questions.forEach(function (q) {
					fragment += createHTMLforQuestion(q);
				});
				voxpopElm.innerHTML = fragment;
				voxpopElm.addEventListener('click', function (evt) {
					if (evt.target.classList.contains('vote')) {
						let questionUuid = evt.target.closest('div[data-voxpop-question-uuid]').dataset.voxpopQuestionUuid;
						let voxpopData = evt.target.closest('*[data-voxpop-uuid').dataset;
						let hostPort = (voxpopData.voxpopHost) ? `//${ voxpopData.voxpopHost }` : '';
						vote(`${hostPort}/api/voxpops/${voxpopData.voxpopUuid}/questions/${questionUuid}/vote`);
					}
				});
			}
		};
		xhr.onerror = function (evt) {
			console.log('XHR error:');
			console.dir(evt.target);
		};
		xhr.send();
	}

	function vote(endpoint) {
		console.log(endpoint);
		let xhr = new XMLHttpRequest();
		xhr.withCredentials = true;
		xhr.open("post", endpoint, true);
		xhr.onload = function () {
			if (this.status >= 200 && this.status < 300) {
				// Success
			}
		};
		xhr.onerror = function (evt) {
			console.log('XHR error:');
			console.dir(evt.target);
		};
		xhr.send();
	}

	window.addEventListener('beforeunload', function() {
		allSse.forEach(function (sse) {
			sse.close();
		});
	});
}());
