
import * as THREE from '../../three.js-master/build/three.module.js';
// import { pong_websocket } from './pong-game.js';

let container;
let camera, scene, renderer;
let field_material;
let group;

let clock = new THREE.Clock();
let delta = 0;
// 30 fps
let interval = 1 / 30;


const FIELD_LENGTH = 500;
const FIELD_WIDTH = 200;
const FIELD_HEIGTH = 10;

initGamePong();

function initGamePong() {
	container = document.getElementById('game-canvas');
	renderer = new THREE.WebGLRenderer({ antialias: true });

	let canvas_width = container.getAttribute("width");
	let canvas_height = container.getAttribute("height");

	console.log("canvas size x: " + canvas_width + ", y:" + canvas_height);

	renderer.setSize(canvas_width, canvas_height);
	container.appendChild(renderer.domElement);

	camera = new THREE.PerspectiveCamera(65, canvas_width / canvas_height, 100, 700);
	camera.position.x = 400;
	camera.position.y = 200;

	camera.lookAt(0, 0, 0);

	// Scene creation
	scene = new THREE.Scene();
	scene.background = new THREE.Color(0xaaaaaa);

	// Lights creation
	scene.add(new THREE.DirectionalLight(0xffffff, 4));
	scene.add(new THREE.AmbientLight(0xffffff));

	// Field mesh creation
	field_material = new THREE.MeshLambertMaterial(0xFF8054);
	let field_geometry = new THREE.BoxGeometry(FIELD_LENGTH, FIELD_HEIGTH, FIELD_WIDTH);
	let field_mesh = new THREE.Mesh(field_geometry, field_material);
	scene.add(field_mesh);

	// Cubes meshes creation
	group = new THREE.Group();
	scene.add(group);

	const geometry = new THREE.BoxGeometry(10, 10, 10);
	for (let i = 0; i < 100; i++) {

		const material = new THREE.MeshLambertMaterial({
			color: Math.random() * 0xffffff
		});

		const mesh = new THREE.Mesh(geometry, material);
		mesh.position.x = Math.random() * 400 - 200;
		mesh.position.y = Math.random() * 400 - 200;
		mesh.position.z = Math.random() * 400 - 200;
		mesh.rotation.x = Math.random();
		mesh.rotation.y = Math.random();
		mesh.rotation.z = Math.random();

		mesh.scale.setScalar(Math.random() * 0.8 + 0.1);
		group.add(mesh);

	}

	// window.addEventListener('resize', onWindowResize);

	animateGamePong();
}

// function onWindowResize() {

// 	const width = window.innerWidth;
// 	const height = window.innerHeight;

// 	camera.aspect = width / height;
// 	camera.updateProjectionMatrix();

// 	renderer.setSize(width, height);

// }

function animateGamePong() {

	requestAnimationFrame(animateGamePong);

	renderGamePong();

}

function renderGamePong() {

	const timer = performance.now();
	group.rotation.x = timer * 0.0002;
	group.rotation.y = timer * 0.0001;
	group.rotation.z = timer * 0.0003;


	delta += clock.getDelta();

	if (delta > interval) {
		// The draw or time dependent code are here
		renderer.render(scene, camera);
		if(pong_websocket.readyState == 1)
		{
			const msg = {
				type: "update",
				// text: document.getElementById("text").value,
				// id: clientID,
				date: Date.now(),
			  };
			  pong_websocket.send(JSON.stringify(msg));
		}

		delta = delta % interval;
	}



}