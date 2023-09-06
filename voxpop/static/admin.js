/*jslint browser: true, plusplus: true, sloppy: true */
/* jshint -W100 */
(function() {
	'use strict';
	let allSse = [];
	let voxpopElements = document.querySelectorAll('*[data-voxpop-uuid*="-"]');
	var adminQuestionLists = {
		'new': document.getElementById('newQuestions'),
		'approved': document.getElementById('approvedQuestions'),
		'discarded': document.getElementById('discardedQuestions'),
		'answered': document.getElementById('answeredQuestions')
	};
	voxpopElements.forEach(function (voxpopElm) {
		let isModerated = voxpopElm.dataset.hasOwnProperty('voxpopIsModerated');
		var sse = new EventSource('questions/stream', {withCredentials: true});
		allSse.push(sse);
		sse.onopen = function (evt) {
			updateConnectionStatus(voxpopElm, evt.target.readyState);
		};
		sse.onerror = function (evt) {
			updateConnectionStatus(voxpopElm, evt.target.readyState);
		};
		sse.addEventListener("new_question", function (evt) {
			let data = JSON.parse(evt.data);
			adminQuestionLists[(isModerated) ? 'new' : 'approved'].insertAdjacentElement("afterbegin", createHTMLforQuestion(data));
		});
		sse.addEventListener("new_vote", function (evt) {
			let data = JSON.parse(evt.data);
			let questionElm = document.querySelector(`div[data-voxpop-question-uuid="${ data.question_id }"]`);
			let voteDisplayElm = questionElm.querySelector('.votes span');
			if (voteDisplayElm) {
				voteDisplayElm.innerText = data.vote_count;
				let parent = questionElm.parentElement;
				let sorted = sortQuestionsByVotes(parent.children);
				parent.replaceChildren(...sorted);
			}
		});
		sse.addEventListener("question_state_update", function (evt) {
			let data = JSON.parse(evt.data);
			let questionElm = document.querySelector(`div[data-voxpop-question-uuid="${ data.question_id }"]`);
			if (questionElm) {
				let listElement = adminQuestionLists[data.state];
				let firstChild = listElement.firstElementChild;
				if (firstChild) {
					firstChild.before(questionElm);
				} else {
					listElement.appendChild(questionElm);
				}
			}
		});
		updateConnectionStatus(voxpopElm, sse.readyState);
	});

	function sortQuestionsByVotes(questionsColl) {
		let questions = Array.from(questionsColl);
		questions.forEach(function (questionElm) {
			if(questionElm.hasAttribute("data-voxpop-question-uuid")) {
				questionElm.votes = parseInt(questionElm.querySelector('.votes span').innerText, 10);
			} else {
				questionElm.votes = -10; // For the form element.
			}
		});
		return questions.sort((a, b) => b.votes - a.votes);
	}

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
		xhr.onerror = function (evt) {
			console.log('XHR error:');
			console.dir(evt.target);
		};
		xhr.send();
	});

	function createHTMLforQuestion(question) {
		const template = document.querySelector('#questionTemplate');
		let clone = template.content.cloneNode(true);
		clone.querySelector("div[data-voxpop-question-uuid]").setAttribute("data-voxpop-question-uuid", question.uuid);
		clone.querySelector("blockquote").innerText = question.text;
		clone.querySelector(".displayName").innerText = question.display_name;
		// clone.querySelector(".votes span").innerText = '0';
		clone.querySelector(".createdAt").innerText = question.created_at;
		return clone.firstElementChild;
	}


	document.querySelectorAll('button.copyToClipboard').forEach(function (copyButtonElm) {
		copyButtonElm.addEventListener('click', function (evt) {
			navigator.clipboard.writeText(evt.target.nextElementSibling.innerText);
		});
	});

	window.addEventListener('beforeunload', function() {
		allSse.forEach(function (sse) {
			sse.close();
		});
	});
}());
