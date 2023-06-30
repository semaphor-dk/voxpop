/*jslint browser: true, plusplus: true, sloppy: true */
/* jshint -W100 */
(function() {
	'use strict';
	var allSse = [];
	let voxpopElements = document.querySelectorAll('*[data-voxpop-uuid*="-"]');
	let newQuestionsElement = document.getElementById('newQuestions');
	let approvedQuestionsElement = document.getElementById('approvedQuestions');
	voxpopElements.forEach(function (voxpopElm) {
//		let questionsUrl = `${ hostPort }/api/voxpops/${ voxpopElm.dataset.voxpopUuid }/questions`;
//		renderVoxpop(voxpopElm, questionsUrl);
		let isModerated = voxpopElm.dataset.hasOwnProperty('voxpopIsModerated');
		var sse = new EventSource(`/stream/${ voxpopElm.dataset.voxpopUuid }/questions/`, {withCredentials: true});
		allSse.push(sse);
		sse.onopen = function (evt) {
			updateConnectionStatus(voxpopElm, evt.target.readyState);
		};
		sse.onerror = function (evt) {
			updateConnectionStatus(voxpopElm, evt.target.readyState);
		};
		sse.addEventListener("new_question", function (evt) {
			let data = JSON.parse(evt.data);
			((isModerated) ? newQuestionsElement : approvedQuestionsElement).insertAdjacentHTML("beforeend", createHTMLforQuestion(data));
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

	let questionLists = document.getElementById('adminQuestionLists');
	questionLists.addEventListener('click', function (evt) {
		if (evt.target.tagName !== 'BUTTON') return;
		let csrfmiddlewaretoken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;
		let state = evt.target.dataset.state;
		let questionId = evt.target.closest('[data-voxpop-question-uuid]').dataset.voxpopQuestionUuid;
		let xhr = new XMLHttpRequest();
		xhr.withCredentials = true;
		xhr.open("PATCH", `${questionId}?state=${state}`, true);
		xhr.setRequestHeader('X-CSRFToken', csrfmiddlewaretoken);
		xhr.onload = function () {
			if (this.status >= 200 && this.status < 300) {
				location.reload();
			}
		};
		xhr.onerror = function (evt) {
			console.log('XHR error:');
			console.dir(evt.target);
		};
		xhr.send();
	});

	function createHTMLforQuestion(q) {
		return `<div data-voxpop-question-uuid="${ q.uuid }">
	<blockquote>${ q.text }</blockquote>
	<div class="displayName">${ q.display_name }</div>
	<div class="votes"><span>${q.vote_count || 0 }</span> votes</div>
	<div class="createdAt">${ q.created_at }</div>
    <div class="questionActions">
        <button type="button" data-state="approved">Approve</button>
        <button type="button" data-state="answered">Mark as answered</button>
        <button type="button" data-state="discarded">Discard</button>
    </div>
</div>\n`;
	}

/*
	function renderVoxpop(voxpopElm, questionsUrl) {
		let xhr = new XMLHttpRequest();
		xhr.open("get", questionsUrl, true);
		xhr.withCredentials = true;
		xhr.onload = function () {
			if (this.status >= 200 && this.status < 300) {
				let questions = JSON.parse(xhr.response);
				let fragment = "\n";
				questions.approved.forEach(function (q) {
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
*/
	window.addEventListener('beforeunload', function() {
		allSse.forEach(function (sse) {
			sse.close();
		});
	});

	document.querySelectorAll('button.copyToClipboard').forEach(function (copyButtonElm) {
		copyButtonElm.addEventListener('click', function (evt) {
			navigator.clipboard.writeText(evt.target.nextElementSibling.innerText);
		});
	});
}());
