// Import the notification function
let pong_websocket = null;
let party_uuid = "Party uuid";
let party_joined = "";


///////////////////////////////////////
///////////////////////////////////////
///////////////////////////////////////


// Load the HTML file content into the specified element
async function loadHtmlElement(file_path) {
	let text = '';
	const response = await fetch(file_path);

	if (!response.ok) {
		throw new Error('Failed to load HTML element: ' + response.status);
	}

	text = await response.text();

	const parser = new DOMParser();
	dom = parser.parseFromString(text, "text/html");

	return (dom.body.firstChild);
}


///////////////////////////////////////
///////////////////////////////////////
///////////////////////////////////////


async function fetchPongCreation() {
	try {
		const response = await fetch(`pong/create_party/`, {
			method: 'GET',
			headers: {
				'Content-Type': 'application/json',
			},
			credentials: 'include',
		});

		if (!response.ok) {
			throw new Error('Party creation failed: ' + response.status);
		}

		const data = await response.json();
		return data.party_uuid;
	} catch (error) {
		console.error('Error fetching party creation:', error); // Log any errors for debugging
		return undefined;
	}
}

async function getPartyList() {
	try {
		const response = await fetch(`pong/get_parties/`, {
			method: 'GET',
			headers: {
				'Content-Type': 'application/json',
			},
			credentials: 'include',
		});

		if (!response.ok) {
			throw new Error('Party list getter failed: ' + response.status);
		}

		const data = await response.json();
		return data['parties'];
	} catch (error) {
		console.error('Error fetching party list:', error); // Log any errors for debugging
		return [];
	}
}

async function getPartyById(_party_uuid) {
	try {
		const response = await fetch(`pong/get_party_by_id/${_party_uuid}`, {
			method: 'GET',
			headers: {
				'Content-Type': 'application/json',
			},
			credentials: 'include',
		});

		if (!response.ok) {
			throw new Error('Party list getter failed: ' + response.status);
		}

		const data = await response.json();
		console.log('Response data:', data); // Log the response data for debugging
		return data['party'];
	} catch (error) {
		console.error('Error fetching party list:', error); // Log any errors for debugging
		return null;
	}
}


function pongJoinGame(party_uuid) {
	pong_websocket = new WebSocket(`wss://${window.location.host}/ws/pong/${party_uuid}/`);
	pong_websocket.onopen = function (event) {
		notification(`Joined game:${party_uuid.substring(0, 5)}`, null, '');
		console.log("Pong WebSocket connection established.");

		party_joined = party_uuid;
		loadGames();
	};
	pong_websocket.onmessage = async function (event) {
		// Update UI to display the received message
	};
	pong_websocket.onerror = function (event) {
		notification(`Failed to join game:${party_uuid}`, null, 'error');
		console.error("Pong WebSocket error:", event);
		console.log("error code is: ", event.code);
		console.log("error message is: ", event.message);
	};
	pong_websocket.onclose = function (event) {
		console.log("Pong WebSocket connection closed.");
		console.log("close code is: ", event.code);
		console.log("close reason is: ", event.reason);

		party_joined = "";
		pong_websocket = null;
		loadGames();
	
	};
}


async function updateCard(party_card, _party_uuid) {
	const _party = await getPartyById(_party_uuid);
	if (!_party)
		return;
	console.log("Party:", _party);
	party_card.setAttribute('id', `party_card_${_party['uuid']}`);
	party_card.getElementsByClassName('party_card_name')[0].innerHTML = _party['name'];
	party_card.getElementsByClassName('party_card_uuid')[0].innerHTML = _party['uuid'].slice(0, 6);
	party_card.getElementsByClassName('party_card_players')[0].innerHTML = `${_party['players'].length}/${_party['max_players']}`;
	// if (_party_uuid === party_joined) {
	// 	party_card.style.backgroundColor = '#86b985';
	// } else {
	// 	party_card.style.backgroundColor = '#f5e0ab';
	// }
}

// random number generator
function cyrb128(str) {
	let h1 = 1779033703, h2 = 3144134277,
		h3 = 1013904242, h4 = 2773480762;
	for (let i = 0, k; i < str.length; i++) {
		k = str.charCodeAt(i);
		h1 = h2 ^ Math.imul(h1 ^ k, 597399067);
		h2 = h3 ^ Math.imul(h2 ^ k, 2869860233);
		h3 = h4 ^ Math.imul(h3 ^ k, 951274213);
		h4 = h1 ^ Math.imul(h4 ^ k, 2716044179);
	}
	h1 = Math.imul(h3 ^ (h1 >>> 18), 597399067);
	h2 = Math.imul(h4 ^ (h2 >>> 22), 2869860233);
	h3 = Math.imul(h1 ^ (h3 >>> 17), 951274213);
	h4 = Math.imul(h2 ^ (h4 >>> 19), 2716044179);
	h1 ^= (h2 ^ h3 ^ h4), h2 ^= h1, h3 ^= h1, h4 ^= h1;
	return [h1 >>> 0, h2 >>> 0, h3 >>> 0, h4 >>> 0];
}

async function createPartyList() {

	const party_list = document.getElementsByClassName('party_list')[0];
	if (party_list) {
		party_list.innerHTML = '';

		let raw_list = [];
		raw_list = await getPartyList();
		if (!raw_list) {
			console.log('No parties available');
			return;
		}
		if (raw_list.length === 0) {
			console.log('No parties available');
			return;
		}


		const default_party_card = await loadHtmlElement('../static/js/pong/party_list_card.html');

		for (let party of raw_list) {

			let party_card = default_party_card.cloneNode(true);

			party_card.setAttribute('id', `party_card_${party['uuid']}`);
			party_card.getElementsByClassName('party_card_name')[0].innerHTML = party['name'];
			party_card.getElementsByClassName('party_card_uuid')[0].innerHTML = party['uuid'].slice(0, 6);
			party_card.getElementsByClassName('party_card_players')[0].innerHTML = `${party['players'].length}/${party['max_players']}`;

			// updateCard(party_card, party['uuid']);

			// const color_table = ['#00286d', '#ffce00', '#dae5e5', '#ff1a00', '#0b0b0b'];
			const color_table = ['#398a74', '#394f8a', '#4b398a', '#8a394f', '#39788a'];

			const randomNumber = cyrb128(party['uuid'])[0];
			const randomColor = color_table[randomNumber % 5];
			party_card.getElementsByClassName('party_card_image')[0].style.backgroundColor = randomColor;

			// party_card.setAttribute('id', `party_card_${party['uuid']}`);
			// party_card.getElementsByClassName('party_card_name')[0].innerHTML = party['name'];
			// party_card.getElementsByClassName('party_card_uuid')[0].innerHTML = party['uuid'].slice(0, 6);
			// party_card.getElementsByClassName('party_card_players')[0].innerHTML = `${party['players'].length}/${party['max_players']}`;

			party_card.onclick = function () {
				// Implement the logic to connect to the chosen party
				pongJoinGame(party['uuid']);
			}

			party_list.appendChild(party_card);
		}
	}
}

// async function createPartyList() {

// 	const party_list = document.getElementById('party-list');
// 	if (party_list) {
// 		party_list.innerHTML = '';

// 		let raw_list = [];
// 		raw_list = await getPartyList();
// 		if (!raw_list) {
// 			console.log('No parties available');
// 			return;
// 		}
// 		if (raw_list.length === 0) {
// 			console.log('No parties available');
// 			return;
// 		}

// 		console.log('Raw list:', raw_list);

// 		raw_list['parties'].forEach(party => {
// 			const partyItem = document.createElement('li');
// 			const partyButJoin = document.createElement('button');

// 			partyButJoin.setAttribute('id', 'button_alan');
// 			partyButJoin.style.backgroundColor = '#86b985';
// 			partyButJoin.innerHTML = `${party['name']}`; // Display the party UUID
// 			partyButJoin.onclick = function () {
// 				// Implement the logic to connect to the chosen party
// 				pong_websocket = new WebSocket(`wss://${window.location.host}/ws/pong/${party['uuid']}/?token=${gtoken}`);
// 				pong_websocket.onopen = function (event) {
// 					notification(`Joined game:${party['uuid']}`, null, null);
// 					console.log("Pong WebSocket connection established.");
// 					createPartyList();
// 				};
// 				pong_websocket.onmessage = async function (event) {
// 					// Update UI to display the received message
// 					createPartyList();
// 					console.log("PONGGAME:", event.data);

// 				};
// 				pong_websocket.onerror = function (event) {
// 					notification(`Failed to join game:${party['uuid']}`, null, null);
// 					console.error("Pong WebSocket error:", event);
// 					console.log("error code is: ", event.code);
// 					console.log("error message is: ", event.reason);
// 				};
// 				pong_websocket.onclose = function (event) {
// 					if (event.error)
// 						notification(`Left game:${party['uuid']}`, null, null);
// 					createPartyList();
// 					console.log("Pong WebSocket connection closed.");
// 					console.log("close code is: ", event.code);
// 					console.log("close reason is: ", event.reason);
// 				};
// 			}
// 			const partyButCopy = document.createElement('button');
// 			partyButCopy.setAttribute('id', 'button_alan');
// 			partyButCopy.innerHTML = `Copy`;
// 			partyButCopy.style.backgroundColor = '#9FE2BF';

// 			partyButCopy.onclick = function () {

// 				navigator.clipboard.writeText(party['uuid']);
// 				notification(`Copied game:${party['uuid']}`, null, null);
// 				party_uuid = party['uuid'];
// 				document.getElementById('party-uuid').value = party_uuid;
// 			}

// 			partyItem.appendChild(partyButJoin);
// 			partyItem.appendChild(partyButCopy);
// 			partyItem.setAttribute('value', party['uuid']);

// 			party_list.appendChild(partyItem);
// 		});
// 	}
// }

async function loadGamesLobby() {
	const lobbyContainer = document.getElementById('pong-game');
	if (lobbyContainer) {
		lobbyContainer.innerHTML = '';

		const partyUuidInput = document.createElement('input');
		partyUuidInput.setAttribute('type', 'text');
		partyUuidInput.setAttribute('id', 'party-uuid');
		partyUuidInput.setAttribute('value', party_uuid);

		const createPartyButton = document.createElement('button');
		createPartyButton.setAttribute('type', 'button');
		createPartyButton.setAttribute('id', 'button_alan');
		createPartyButton.style.backgroundColor = '#355E3B';
		createPartyButton.style.color = '#FFFFFF';
		createPartyButton.innerHTML = 'Create Party';
		createPartyButton.onclick = async function () {
			partyUuidInput.setAttribute('value', await fetchPongCreation());
			await createPartyList();
		};

		const partyTitle = document.createElement('h2');
		partyTitle.innerHTML = 'Pong Parties';

		const partyList = document.createElement('ul');
		partyList.setAttribute('class', 'party_list');
		lobbyContainer.appendChild(partyList);

		// IN PROGRESS
		// loadHtmlElement('../static/js/pong/party_list.html', 'pong-game');

		await createPartyList();

		const connectButton = document.createElement('button');
		connectButton.setAttribute('type', 'button');
		connectButton.setAttribute('id', 'button_alan');
		connectButton.innerHTML = 'Connect';
		connectButton.onclick = function () {
			const chosenPartyUuid = partyUuidInput.value;

			// Implement the logic to connect to the chosen party
			pongJoinGame(chosenPartyUuid);
		};



		let small_div = document.createElement('div');
		small_div.setAttribute('id', 'uuid_form');
		small_div.appendChild(partyUuidInput);
		small_div.appendChild(connectButton);

		lobbyContainer.appendChild(createPartyButton);
		lobbyContainer.appendChild(small_div);

		lobbyContainer.appendChild(partyTitle);
		lobbyContainer.appendChild(partyList);
	}
}

function isWebSocketOpen(ws) {
	return ws !== null && ws.readyState === WebSocket.OPEN;
}

function unloadGames() {
	console.log('Unloading games');
	if (isWebSocketOpen(pong_websocket) === true) {
		pong_websocket.close();
		pong_websocket = null;
	}
	const lobbyContainer = document.getElementById('pong-game');
	if (lobbyContainer) {
		lobbyContainer.innerHTML = '';
	}
}

async function loadGames() {
	console.log('Loading games');
	if (party_joined === "") {
		loadGamesLobby();
	} else {
		const lobbyContainer = document.getElementById('pong-game');
		let gameScript = document.getElementById('game-script');
		lobbyContainer.innerHTML = '';
		// notification('Already in a game', null, null);

		const gameContainer = document.createElement('div');
		gameContainer.setAttribute('id', 'game-canvas');
		gameContainer.setAttribute('width', '1100');
		gameContainer.setAttribute('height', '700');
		lobbyContainer.appendChild(gameContainer);

		console.log('Game script:', gameScript);
		if (gameScript != null) {
			console.log('Removing existing game script');
			gameScript.remove();
		}
		gameScript = document.createElement('script');
		gameScript.setAttribute('id', 'game-script');
		gameScript.setAttribute('type', 'module');
		gameScript.setAttribute('src', '../static/js/pong/pong-canvas.js');
		lobbyContainer.appendChild(gameScript);
	}
}

// async function loadGames() {
// 	if (!user)
// 		return;

// 	const gamesContainer = document.getElementById('pong-game');
// 	if (gamesContainer) {
// 		gamesContainer.innerHTML = ``;

// 		const button_start = document.createElement('button');
// 		button_start.setAttribute('id', 'start');
// 		button_start.setAttribute('type', 'button');
// 		button_start.innerHTML = 'Start Game';
// 		button_start.onclick = function () {
// 			pong_websocket.send(JSON.stringify(
// 				{
// 					'command': 'start-game',
// 					'party_uuid': 'party_uuid'
// 				}
// 			));
// 		};
// 		gamesContainer.appendChild(button_start);

// 		const button_stop = document.createElement('button');
// 		button_stop.setAttribute('id', 'stop');
// 		button_stop.setAttribute('type', 'button');
// 		button_stop.innerHTML = 'Stop Game';
// 		button_stop.onclick = function () {
// 			pong_websocket.send(JSON.stringify(
// 				{
// 					'command': 'stop-game',
// 					'party_uuid': 'party_uuid'
// 				}
// 			));
// 		};
// 		gamesContainer.appendChild(button_stop);

// 		const party_uuid_field = document.createElement('input');
// 		party_uuid_field.setAttribute('id', 'party_uuid');
// 		party_uuid_field.setAttribute('type', 'text');
// 		party_uuid_field.setAttribute('value', party_uuid);
// 		gamesContainer.appendChild(button_stop);

// 		// const my_canvas = document.createElement('div');
// 		// my_canvas.setAttribute('id', 'canvas');
// 		// my_canvas.setAttribute('width', '800');
// 		// my_canvas.setAttribute('height', '400');
// 		// gamesContainer.appendChild(my_canvas);

// 		// const my_script = document.createElement('script');
// 		// my_script.setAttribute('type', 'module');
// 		// my_script.setAttribute('src', '../static/js/pong/pong-canvas.js');
// 		// gamesContainer.appendChild(my_script);
// 	}
// }