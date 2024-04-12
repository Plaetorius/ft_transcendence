import * as THREE from '../../three.js-master/build/three.module.js';
// import { pong_websocket } from './pong-game.js';

let container;
let camera, scene, renderer;
let field_material;
let group;

let clock = new THREE.Clock();
let delta = 0;

// The frame per second
let interval = 1 / 20;


const FIELD_LENGTH = 500;
const FIELD_WIDTH = 200;
const FIELD_HEIGTH = 10;

let loaded_party = null;

const sleep = (delay) => new Promise((resolve) => setTimeout(resolve, delay))

function wait_for_base_party() {
	if (loaded_party === null) { //we want it to match
		setTimeout(wait_for_base_party, 50); //wait 50 millisecnds then recheck
		return;
	}
	//real action
}

initGamePong();
wait_for_base_party();
animateGamePong();

function initGamePong() {

	container = document.getElementById('game-canvas');
	container.style.display = "flex";
	container.style.flexDirection = "row";

	let player_list = document.createElement('ul');
	player_list.id = "ingame_player_list";
	container.appendChild(player_list);

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
}


function animateGamePong() {
	
	renderGamePong();
	requestAnimationFrame(animateGamePong);
}

// WEBSOCKET RECEIVE
pong_websocket.onmessage = function(data) {
	const json_data = JSON.parse(data.data);

	if (json_data["type"] === "update") {
		// console.log("pong_websocket.update at " + Date.now());
		loaded_party = json_data["party"];
	}
	// console.log("pong_websocket.on_recv: " + json_data);
};

function getSceneById(id) {
	let ret_obj = null;
	scene.traverse(function(object) {
		if (object.userId != undefined) {
			if (object.userId === id) {
				ret_obj = object;
				return ;
			}
		}
	});
	return ret_obj;
}

function updateOrCreateObject(id, position, rotation, color) {
    let object = getSceneById(id);

    if (object == null) {
        // Create new object
		const color = '#' + Math.floor(Math.random()*16777215).toString(16);
		const geometry = new THREE.BoxGeometry(32, Math.random() * 10 + 10, 16);
        const material = new THREE.MeshLambertMaterial({ color: color})
			
        let cube = new THREE.Mesh(geometry, material);
        cube.position.set(position.x, position.y, position.z);
        cube.rotation.set(0, rotation, 0);
		cube.userId = id;
        scene.add(cube);
    } else {
        // Update existing object
		// console.log("THERE IS OBJECTS: " + position.x + ", " + position.y + ", " + position.z);
        object.position.set(position.x, position.y, position.z);
        object.rotation.set(0, rotation, 0);
        object.material.color.set(color);
    }
}

function removeObject(id) {
    let object = getSceneById(id);
    if (object) {
        scene.remove(object);
    }
}

function setPlayerList() {
	let player_list = document.getElementById('ingame_player_list');
	if (player_list == null) {
		return;
	}
	player_list.innerHTML = "";
	if (loaded_party != null) {
		let players = loaded_party['players'];
		for (let player of players) {
			let player_li = document.createElement('li');
			player_li.innerText = player['name'];
			player_list.appendChild(player_li);
		}
	}

}


function renderGamePong() {

	const timer = performance.now();
	group.rotation.x = timer * 0.0002;
	group.rotation.y = timer * 0.0001;


	delta += clock.getDelta();

	if (delta > interval) {
		// The draw or time dependent code are here
		if (pong_websocket.readyState == 1) {
			let msg = {
				type: "update",
				date: Date.now()
			};
			pong_websocket.send(JSON.stringify(msg));
		}

		if (loaded_party != null) {
			const obj_array = loaded_party['objects'];
			for (let obj of obj_array) {
				const uuid = obj['uuid'];
				const pos = new THREE.Vector3(obj['pos'][0], FIELD_HEIGTH, obj['pos'][1]);
				const rot = obj['rot']

				updateOrCreateObject(uuid, pos, rot);
			}
			setPlayerList();
		}

		renderer.render(scene, camera);

		delta = delta % interval;
	}
}