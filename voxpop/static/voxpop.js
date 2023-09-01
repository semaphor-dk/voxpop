/*jslint browser: true, plusplus: true, sloppy: true */
/* jshint -W100 */
(function() {
	'use strict';
	let allSse = [];
	let translations = {};
	let voxpopElements = document.querySelectorAll('*[data-voxpop-uuid*="-"]');
	insertStylesheet(voxpopElements[0]);
	voxpopElements.forEach(function (voxpopElm) {
		let hostPort = (voxpopElm.dataset.voxpopHost) ? `//${ voxpopElm.dataset.voxpopHost }` : '';
		let questionsUrl = `${ hostPort }/api/voxpops/${ voxpopElm.dataset.voxpopUuid }/questions`;
		renderVoxpop(voxpopElm, questionsUrl);
		var sse = new EventSource(`${ hostPort }/voxpops/${ voxpopElm.dataset.voxpopUuid }/questions/stream`, {withCredentials: true});
		allSse.push(sse);
		sse.onopen = function (evt) {
			updateConnectionStatus(voxpopElm, evt.target.readyState);
		};
		sse.onerror = function (evt) {
			updateConnectionStatus(voxpopElm, evt.target.readyState);
		};
		sse.addEventListener("new_question", function (evt) {
			let data = JSON.parse(evt.data);
			let form = voxpopElm.querySelector("form");
			form.insertAdjacentHTML("beforebegin", createHTMLforQuestion(data, translations));
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

	function insertStylesheet(voxpopElm) {
		const head = document.querySelector("head");
		head.insertAdjacentHTML("beforeend", `<link rel="stylesheet" href="${ (voxpopElm.dataset.voxpopHost) ? '//' + voxpopElm.dataset.voxpopHost : '' }/static/voxpop.css">`);
	}

	function updateConnectionStatus(voxpopElm, state) {
		voxpopElm.className = ["connecting", "live", "disconnected"][state];
	}

	function getLanguage(voxpopElm) {
			let langElm = voxpopElm.closest('[lang]');
			return (langElm) ? langElm.getAttribute('lang') : 'en';
	}

	function getJSON(url) {
		return new Promise(function (resolve, reject) {
			var xhr = new XMLHttpRequest();
			xhr.withCredentials = true;
			xhr.open('get', url, true);
			xhr.onload = function () {
				if (this.status >= 200 && this.status < 300) {
					try {
						resolve(JSON.parse(xhr.response));
					}
					catch(error) {
						reject(error);
					}
				} else {
					reject({
						status: this.status,
						message: xhr.statusText
					});
				}
			};
			xhr.onerror = function () {
				reject({
					status: this.status,
					message: xhr.statusText
				});
			};
			xhr.send();
		});
	}

	function createHTMLforQuestion(question, translations) {
		let voteCountLabel = (question.vote_count || 0)  === 1 ? 'VoteCounterLabelOne' : 'VoteCounterLabel';
		return `<div data-voxpop-question-uuid="${ question.uuid }">
	<blockquote>${ question.text }</blockquote>
	<div class="displayName">${ question.display_name }</div>
	<div class="votes"><span>${ question.vote_count || 0 }</span> ${ translations[voteCountLabel] }</div>
	<button type="button" class="vote">${ translations['VoteButton'] }</button>
</div>\n`;
	}

	function createNewQuestionForm(hostname, voxpopUuid, translations) {
		return `<form action="${ hostname }/api/voxpops/${ voxpopUuid }/questions/new" method="POST">
	<h3>${ translations['QuestionFormHeadline'] }</h3>
    <input type="hidden" name="csrfmiddlewaretoken" value="CF7wx3OUxgmnjF4KWO0FJsQcrjJIk0luPQDtv0XBA6UFi42MwbT4yoav3cBmxcPW">
    <textarea name="text" rows="3" maxlength="150" required></textarea>
    - <input name="display_name" type="text" maxlength="50" placeholder="${ translations['NamePlaceholder'] }">
    <button type="submit" class="primary">${ translations['SubmitQuestionButton'] }</button>
</form>`;
	}

	function renderVoxpop(voxpopElm, questionsUrl) {
		let lang = getLanguage(voxpopElm);
		let promises = [
			getJSON(questionsUrl),
			getJSON(((voxpopElm.dataset.voxpopHost) ? '//' + voxpopElm.dataset.voxpopHost : '') + '/static/translations.json')
		];
		Promise.all(promises).then(function (values) {
			let questions = values[0];
			translations = values[1][lang];
			if (typeof translations === 'undefined') translations = values[1]['en'];
			let fragment = "\n";
			questions.approved.forEach(function (question) {
				fragment += createHTMLforQuestion(question, translations);
			});
			fragment += createNewQuestionForm((voxpopElm.dataset.voxpopHost) ? '//' + voxpopElm.dataset.voxpopHost : '', voxpopElm.dataset.voxpopUuid, translations);
			voxpopElm.innerHTML = fragment;
			voxpopElm.addEventListener('click', function (evt) {
				if (evt.target.classList.contains('vote')) {
					let questionUuid = evt.target.closest('div[data-voxpop-question-uuid]').dataset.voxpopQuestionUuid;
					let voxpopData = evt.target.closest('*[data-voxpop-uuid').dataset;
					let hostPort = (voxpopData.voxpopHost) ? `//${ voxpopData.voxpopHost }` : '';
					vote(`${ hostPort }/api/voxpops/${ voxpopData.voxpopUuid }/questions/${ questionUuid }/vote`);
				}
			});
			voxpopElm.querySelector('form').addEventListener('submit', function (evt) {
				evt.preventDefault();
				let formData = new FormData(evt.target);
				let object = {};
				formData.forEach(function(value, key){
					object[key] = value;
				});
				const xhr = new XMLHttpRequest();
				xhr.withCredentials = true;
				xhr.addEventListener('load', function () {
					evt.target.querySelector('textarea[name="text"]').value = '';
				});
				xhr.open(evt.target.method, evt.target.action);
				xhr.send(JSON.stringify(object));
			});
		});
	}

	function vote(endpoint) {
		let xhr = new XMLHttpRequest();
		xhr.withCredentials = true;
		xhr.open('post', endpoint, true);
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
