

function loadGames() {
	if (!user)
		return;

	const socket = new WebSocket(`wss://${window.location.host}/ws/pong/`);
	socket.onopen = function (event) {
		console.log("Pong WebSocket connection established.");
	};
	socket.onmessage = function (event) {
		console.log("Pong Received message from server:", event.data);
		// Update UI to display the received message
	};
	socket.onerror = function (event) {
		console.error("Pong WebSocket error:", event);
		console.log("error code is: ", event.code);
		console.log("error message is: ", event.message);
	};
	socket.onclose = function (event) {
		console.log("Pong WebSocket connection closed.");
		console.log("close code is: ", event.code);
		console.log("close reason is: ", event.reason);
	};


	console.log(`Load and Display game called`);

	const gamesContainer = document.getElementById('pong-game');
	if (gamesContainer) {
		gamesContainer.innerHTML = ``;

		const base_div = document.createTextNode('le text du fond et rarement du bon');
		gamesContainer.appendChild(base_div);

		const my_canvas = document.createElement('div');
		my_canvas.setAttribute('id', 'canvas');
		my_canvas.setAttribute('width', '800');
		my_canvas.setAttribute('height', '400');
		gamesContainer.appendChild(my_canvas);

		const my_script = document.createElement('script');
		my_script.setAttribute('type', 'module');
		my_script.setAttribute('src', '../static/js/pong/pong-canvas.js');
		gamesContainer.appendChild(my_script);
	}
}