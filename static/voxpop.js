/*jslint browser: true, plusplus: true, sloppy: true */
/* jshint -W100 */
(function() {
	'use strict';
	let voxpopElements = document.querySelectorAll('*[data-voxpop-uuid');
	voxpopElements.forEach(function (voxpopElm) {
		let hostPort = (voxpopElm.dataset.voxpopHost) ? `//${ voxpopElm.dataset.voxpopHost }` : '';
		let questionsUrl = `${ hostPort }/api/voxpops/${ voxpopElm.dataset.voxpopUuid }/questions`;
		renderVoxpop(voxpopElm, questionsUrl);
		const sse = new EventSource(`${ hostPort }/api/voxpops/${ voxpopElm.dataset.voxpopUuid }/questions/events`);
		sse.onmessage = function (evt) {
			console.log(evt.data);
			voxpopElm.insertAdjacentHTML("beforeend", evt.data);
		};
	});

	function renderVoxpop(voxpopElm, questionsUrl) {
		let xhr = new XMLHttpRequest();
		xhr.open("get", questionsUrl, true);
		xhr.onload = function () {
			if (this.status >= 200 && this.status < 300) {
				let questions = JSON.parse(xhr.response);
				let fragment = "\n";
				questions.forEach(function (q) {
					fragment += `<div data-voxpop-question-uuid="${ q.uuid }">
	<blockquote>${ q.text }</blockquote>
	<div class="DisplayName">- ${ q.display_name }</div>
	<div class="votes"><span>${q.vote_count }</span> votes</div>
	<button type="button" class="vote">Vote</button>
</div>\n`;
				});
				voxpopElm.innerHTML = fragment;
				document.querySelectorAll('button.vote').forEach(function (voteButton) {
					voteButton.addEventListener('click', function (evt) {
						let questionUuid = evt.target.closest('div[data-voxpop-question-uuid]').dataset.voxpopQuestionUuid;
						let voxpopData = evt.target.closest('*[data-voxpop-uuid').dataset;
						let hostPort = (voxpopData.voxpopHost) ? `//${ voxpopData.voxpopHost }` : '';
						vote(`${hostPort}/api/voxpops/${voxpopData.voxpopUuid}/questions/${questionUuid}/vote`);
					});
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
}());
