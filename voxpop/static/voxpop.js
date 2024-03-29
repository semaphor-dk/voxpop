/*jslint browser: true, plusplus: true, sloppy: true */
/* jshint -W100 */
(function() {
	'use strict';
	let allSse = [];
	let translations = {};
	let voxpopElements = document.querySelectorAll('*[data-voxpop-uuid*="-"]');
	insertStylesheet(voxpopElements[0]);
	voxpopElements.forEach(function (voxpopElm) {
		renderVoxpop(voxpopElm);
		let hostPort = (voxpopElm.dataset.voxpopHost) ? `//${ voxpopElm.dataset.voxpopHost }` : '';
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
			let list = voxpopElm.querySelector(".list");
			list.insertAdjacentHTML("beforebegin", createHTMLforQuestion(data, translations));
		});
		sse.addEventListener("question_state_update", function (evt) {
			let data = JSON.parse(evt.data);
			let questionElm = document.querySelector(`div[data-voxpop-question-uuid="${ data.question_id }"]`);
			if (questionElm) {
				if (data.state == "answered") {
					questionElm.classList.add("answered");
				} else {
					questionElm.remove();
				}
			}
		});
		sse.addEventListener("new_vote", function (evt) {
			let data = JSON.parse(evt.data);
			let questionElm = document.querySelector(`div[data-voxpop-question-uuid="${ data.question_id }"]`);
			let voteDisplayElm = questionElm.querySelector('.votes span');
			if (voteDisplayElm) {
				voteDisplayElm.innerText = data.vote_count;
				let voxpopElm = questionElm.closest('*[data-voxpop-uuid*="-"]');
				sortQuestionsByVotes(voxpopElm);
			}
		});
		updateConnectionStatus(voxpopElm, sse.readyState);
	});

	function sortQuestionsByVotes(voxpopElm) {
		let listElm = voxpopElm.querySelector('.list');
		let questions = Array.from(listElm.children);
		questions.forEach(function (questionElm) {
			questionElm.votes = parseInt(questionElm.querySelector('.votes span').innerText, 10);
		});
		let sorted = questions.sort((a, b) => b.votes - a.votes);
		listElm.replaceChildren(...sorted);
	}

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
	<blockquote><span class="displayName">${ question.display_name }</span>${ question.text }</blockquote>
	<div class="displayName">${ question.display_name }</div>
	<div class="votes"><span title="${ translations[voteCountLabel] }">${ question.vote_count || 0 }</span></div>
	<button type="button" class="vote" title="${ translations['VoteButton'] }"></button>
</div>\n`;
	}

	function createNewQuestionForm(hostname, voxpopUuid, translations) {
		return `<form action="${ hostname }/api/voxpops/${ voxpopUuid }/questions/new" method="POST">
			<h3>${ translations['QuestionFormHeadline'] }</h3>
    		<input type="hidden" name="csrfmiddlewaretoken" value="CF7wx3OUxgmnjF4KWO0FJsQcrjJIk0luPQDtv0XBA6UFi42MwbT4yoav3cBmxcPW">
    		<input name="display_name" type="text" maxlength="50" placeholder="${translations['NamePlaceholder']}">
    		<input name="text" type="text" maxlength="1000" required placeholder="${ translations['QuestionPlaceholder'] }">
    		<button type="submit" class="primary cta">${ translations['SubmitQuestionButton'] }</button>
			</form>`;
	}

	function login(voxpopHost, token) {
		var xmlhttp = new XMLHttpRequest();
		xmlhttp.withCredentials = true;
		var url = voxpopHost + '/api/voxpops/login';
		xmlhttp.open('POST', url, true);
		xmlhttp.send(JSON.stringify({ "token": token.split("#")[1] }));
		if(xmlhttp.readyState == 4) {
			var resp = JSON.parse(xmlhttp.responseText);
			console.log(resp);
		}
	}

	function updateDisplayName(voxpopHost, me) {
        getJSON(voxpopHost + '/api/voxpops/whoami').then(function (new_me) {
            if (new_me.display_name) {
                const nameField = document.querySelector('input[name="display_name"]');
                nameField.disabled = true;
                nameField.placeholder = new_me.display_name;
            } else {
                setTimeout(updateDisplayName(voxpopHost, me), 1000);
            }
        });
    }

	function renderVoxpop(voxpopElm) {
		let lang = getLanguage(voxpopElm);
		let voxpopHost = ((voxpopElm.dataset.voxpopHost) ? '//' + voxpopElm.dataset.voxpopHost : '');
		let promises = [
			getJSON(voxpopHost + '/api/voxpops/' + voxpopElm.dataset.voxpopUuid + '/questions'),
			getJSON(voxpopHost + '/static/translations.json'),
			getJSON(voxpopHost + '/api/voxpops/' + voxpopElm.dataset.voxpopUuid),
			getJSON(voxpopHost + '/api/voxpops/whoami')
		];
		Promise.all(promises).then(function (values) {
			let questions = values[0];
			translations = values[1][lang];
			let config = values[2];
			let me = values[3];
			if (typeof translations === 'undefined') translations = values[1]['en'];
			if(config.allow_anonymous) {
				console.log("Anonymous allowed");
			} else {
				console.log("Anonymous not allowed");
				if(me.display_name) {
					console.log("You are logged in already!");
                    updateDisplayName(voxpopHost, me);
				} else {
					console.log("Not logged in");
					if (window.location.hash) {
						login(voxpopHost, window.location.hash);
						history.pushState("", document.title, window.location.pathname + window.location.search);
                        updateDisplayName(voxpopHost, me);
					} else {
						console.log("You are not logged in.");
						window.location.replace(voxpopElm.dataset.voxpopLogin + encodeURIComponent(document.location));
					}
				}
			}
			let fragment = "\n<div class=\"list\">";
			questions.approved.forEach(function (question) {
				fragment += createHTMLforQuestion(question, translations);
			});
			fragment += "</div>";
			fragment += createNewQuestionForm((voxpopElm.dataset.voxpopHost) ? '//' + voxpopElm.dataset.voxpopHost : '', voxpopElm.dataset.voxpopUuid, translations);
			voxpopElm.innerHTML = fragment;
			sortQuestionsByVotes(voxpopElm);
			voxpopElm.addEventListener('click', function (evt) {
				if (evt.target.classList.contains('vote')) {
					let questionUuid = evt.target.closest('div[data-voxpop-question-uuid]').dataset.voxpopQuestionUuid;
					let voxpopData = evt.target.closest('*[data-voxpop-uuid]').dataset;
					let hostPort = (voxpopData.voxpopHost) ? `//${ voxpopData.voxpopHost }` : '';
					vote(`${ hostPort }/api/voxpops/${ voxpopData.voxpopUuid }/questions/${ questionUuid }/vote`);
				}
			});
			voxpopElm.querySelector('form').addEventListener('submit', function (evt) {
				evt.preventDefault();
				let submitButton = voxpopElm.querySelector('button[type="submit"]');
				submitButton.disabled = true;
				let voxpopQuestionForm = evt.target;
				let formData = new FormData(voxpopQuestionForm);
				let object = {};
				formData.forEach(function(value, key) {
					object[key] = value;
				});
				const xhr = new XMLHttpRequest();
				xhr.withCredentials = true;
				xhr.addEventListener('load', function () {
					evt.target.querySelector('input[name="text"]').value = '';
				});
				xhr.open(evt.target.method, evt.target.action);
				xhr.send(JSON.stringify(object));
				voxpopQuestionForm.insertAdjacentHTML('beforeend', `<p class="info">${ translations['QuestionReceived'] }</p>`);
				setTimeout(function () {
					submitButton.disabled = false;
					voxpopQuestionForm.querySelector('.info').remove();
				}, 5000);
			});
		}).catch(function (error) {
			console.error(error.message || 'JSON source failed to load.');
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
