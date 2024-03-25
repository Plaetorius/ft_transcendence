

function loadGames() {
	if (!user)
		return;
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
