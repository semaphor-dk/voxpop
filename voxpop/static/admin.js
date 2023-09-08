/*jslint browser: true, plusplus: true, sloppy: true */
/* jshint -W100 */
(function() {
	'use strict';
	let allSse = [];
	let voxpopElm = document.querySelector('*[data-voxpop-uuid*="-"]');
	var adminQuestionLists = {
		'new': document.getElementById('newQuestions'),
		'approved': document.getElementById('approvedQuestions'),
		'discarded': document.getElementById('discardedQuestions'),
		'answered': document.getElementById('answeredQuestions')
	};
	let parent = adminQuestionLists['approved'];
	sortQuestionsByVotes(parent);
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
			sortQuestionsByVotes(parent);
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

	function sortQuestionsByVotes(parentElm) {
		let questions = Array.from(parentElm.children);
		questions.forEach(function (questionElm) {
			if(questionElm.hasAttribute("data-voxpop-question-uuid")) {
				questionElm.votes = parseInt(questionElm.querySelector('.votes span').innerText, 10);
			} else {
				questionElm.votes = -10; // For the form element.
			}
		});
		let sorted = questions.sort((a, b) => b.votes - a.votes);
		parentElm.replaceChildren(...sorted);
	}

	function updateConnectionStatus(voxpopElm, state) {
		voxpopElm.className = ["connecting", "live", "disconnected"][state];
	}

	let questionLists = document.getElementById('adminQuestionLists');
	questionLists.addEventListener('click', function (evt) {
		if (evt.target.tagName !== 'BUTTON') return;
		let csrfmiddlewaretoken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;
		let button = evt.target;
		let state = button.dataset.state;
		let question = button.closest('[data-voxpop-question-uuid]');
		let questionId = question.dataset.voxpopQuestionUuid;
		let xhr = new XMLHttpRequest();
		xhr.withCredentials = true;
		xhr.open("PATCH", `${questionId}?state=${state}`, true);
		xhr.setRequestHeader('X-CSRFToken', csrfmiddlewaretoken);
		xhr.onload = function () {
			if (state == "approved") {
				sortQuestionsByVotes(question.parentElement);
			}
		};
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
