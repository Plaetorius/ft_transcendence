import * as THREE from 'three';
// import { EffectComposer, RenderPass, ShaderPass, SobelOperatorShader, FontLoader, TextGeometry } from 'addons/Addons.js';
// import { pong_websocket } from './pong-game.js';


let container;
let camera, scene, renderer, composer, skybox, font_loader;
let group;

let glob_font = null;

let clock = new THREE.Clock();
let delta = 0.0;
let server_delta = 0.0;

// The frame per second
let interval = 1 / 60;
let server_interval = 1 / 30;

let sky_geometry = new THREE.SphereGeometry(2, 16, 16);
sky_geometry.scale(-1, 1, 1); // Inversion des normales pour l'intérieur de la sphère

// Chargement des textures
const textureLoader = new THREE.TextureLoader();
let texture_sky = textureLoader.load('static/pong_images/sky.jpg'); // Face avant

const FIELD_HEIGTH = 10; //y

let loaded_party = null;
let removed_obj_list = [];

const sleep = (delay) => new Promise((resolve) => setTimeout(resolve, delay))

function wait_for_base_party() {
	if (loaded_party === null) { //we want it to match
		setTimeout(wait_for_base_party, 50); //wait 50 millisecnds then recheck
		return;
	}
	//real actionaaaaaa 
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
	player_list.classList.add("ingame_player_list");
	// player_list.style = "position:absolute; top:50%; left:00%; transform:translate(100%,-50%); background:yellow;"
	container.appendChild(player_list);


	renderer = new THREE.WebGLRenderer({ antialias: true });

	let canvas_width = container.getAttribute("width");
	let canvas_height = container.getAttribute("height");

	console.log("canvas size x: " + canvas_width + ", y:" + canvas_height);

	renderer.setSize(canvas_width, canvas_height);
	container.appendChild(renderer.domElement);


	// var canvas = renderer.domElement,
	// 	context = canvas.getContext('2d');


	// context.moveTo(100, 150);
	// context.lineTo(350, 50);
	// context.stroke();

	camera = new THREE.PerspectiveCamera(65, canvas_width / canvas_height, 0.1, 5000);
	camera.position.x = 0;
	camera.position.y = 500;
	camera.position.z = -0.001;
	// camera.position.z = 400;

	camera.lookAt(0, 0, 0);

	skybox = new THREE.Mesh(sky_geometry, new THREE.MeshBasicMaterial({ map: texture_sky }));
	skybox.renderOrder = 0;
	skybox.material.depthTest = false;
	skybox.material.depthWrite = false;

	// font_loader = new FontLoader();
	// font_loader.load('static/fonts/pong_font.json', function (font) {
	// 	glob_font = font;
	// });

	// Scene creation
	scene = new THREE.Scene();
	scene.background = new THREE.Color(0x222831);

	// Lights creation
	scene.add(new THREE.DirectionalLight(0xffffff, 4));
	scene.add(new THREE.AmbientLight(0xffffff));
	scene.add(skybox);

	// composer = new EffectComposer(renderer);

	// // Ajoute un RenderPass à l'EffectComposer
	// const renderPass = new RenderPass(scene, camera);
	// composer.addPass(renderPass);

	// Ajoute un FilmPass à l'EffectComposer
	// const filmPass = new FilmPass(0.5, 0.5, 1000, false);
	// const filmPass = new GlitchPass();
	// // const stensilPass = new MaskPass(scene, camera);
	// const shaderMaterial = new THREE.ShaderMaterial(SobelOperatorShader)
	// const shaderPass = new ShaderPass(shaderMaterial, "tDiffuse")
	// shaderMaterial.uniforms.resolution.value.x = window.innerWidth
	// shaderMaterial.uniforms.resolution.value.y = window.innerHeight

	// // composer.addPass(filmPass);
	// composer.addPass(shaderPass);

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

let pressed = {};

window.addEventListener('keydown', function (event) {
	pressed[event.key.toLowerCase()] = true;
});

window.addEventListener('keyup', function (event) {
	delete pressed[event.key.toLowerCase()];
});


function animateGamePong() {

	renderGamePong();
	requestAnimationFrame(animateGamePong);
}

// WEBSOCKET RECEIVE
pong_websocket.onmessage = function (data) {
	const json_data = JSON.parse(data.data);

	if (json_data["type"] === "update") {
		// console.log("pong_websocket.update at " + Date.now());
		loaded_party = json_data["party"];
		server_delta = 0.0;
		server_interval = loaded_party["second_per_frames"];

		// send keys to server only when we receive information from server
		if (pong_websocket.readyState == 1) {
			let msg = {
				type: "update",
				keys: pressed,
				player_name: user.username,
				removed_obj: removed_obj_list,
				date: Date.now()
			};
			pong_websocket.send(JSON.stringify(msg));
		}
		
	}
	if (json_data['type'] === "title") {
		console.log("Title: " + json_data.text + " at " + json_data.time + " with img: " + json_data.img);
		notification(json_data.text, null, json_data.img, json_data.time);
		
	}

};

function getSceneById(id) {
	let ret_obj = null;
	scene.traverse(function (object) {
		if (object.userId != undefined) {
			if (object.userId === id) {
				ret_obj = object;
				return;
			}
		}
	});
	return ret_obj;
}

function updateOrCreateObject(id, position, rotation, size, shape, color, text = "oeoe") {
	let object = getSceneById(id);

	if (object == null) {
		// Create new object
		//const color = '#' + Math.floor(Math.random()*16777215).toString(16);
		let geometry;
		let material;
		if (shape === "Shape.TERRAIN") {
			geometry = new THREE.BoxGeometry(size.x, 5, size.z);
			material = new THREE.MeshLambertMaterial({ color: color });
			position.y = -2.5;
		} else if (shape === "Shape.PADDLE") {
			geometry = new THREE.BoxGeometry(size.x, 10, size.z);
			material = new THREE.MeshLambertMaterial({ color: color });
			position.y = 5;
		} else if (shape === "Shape.BALL") {
			geometry = new THREE.SphereGeometry(size.x / 2, 16, 16);
			material = new THREE.MeshLambertMaterial({ color: color });
			position.y = 10;
		} /*else if (shape === "Shape.TEXT") {
			if (glob_font == null) {
				return;
			}
			console.log("TEXT: " + text);
			console.log(glob_font);
			geometry = new TextGeometry(text, {
				font: glob_font,
				size: size.x,
				height: 0.5,
				curveSegments: 12,
				bevelEnabled: true,
				bevelThickness: 0.03,
				bevelSize: 0.02,
				bevelOffset: 0,
				bevelSegments: 5
			});
			material = new THREE.MeshBasicMaterial({ color: 0xff0000 });
			position.y = size.y;
		} */else {
			geometry = new THREE.BoxGeometry(size.x, 10, size.z);
			material = new THREE.MeshLambertMaterial({ color: color });
		}

		let cube = new THREE.Mesh(geometry, material);
		cube.position.set(position.x, position.y, position.z);
		cube.rotation.set(0, rotation, 0);
		cube.userId = id;
		cube.userText = text;
		scene.add(cube);
	}else {
		// Update existing object
		// console.log("THERE IS OBJECTS: " + position.x + ", " + position.y + ", " + position.z);
		object.position.set(position.x, object.position.y, position.z);
		object.rotation.set(0, rotation, 0);
		object.material.color.set(color);
		// if (shape === "Shape.TEXT") {
		// 	if (text != object.userText) {
		// 		object.geometry = new TextGeometry(text, {
		// 			font: glob_font,
		// 			size: size.x,
		// 			height: 0.5,
		// 			curveSegments: 12,
		// 			bevelEnabled: true,
		// 			bevelThickness: 0.03,
		// 			bevelSize: 0.02,
		// 			bevelOffset: 0,
		// 			bevelSegments: 5
		// 		});
		// 		object.geometry.computeBoundingBox();
		// 		let boundingBox = object.geometry.boundingBox;
		// 		let textWidth = boundingBox.max.x - boundingBox.min.x;
		// 		let centerX = -textWidth / 2;
		// 		object.geometry.translate( centerX, 0, 0 );
		// 		object.position.x = pos.x
		// 		object.userText = text;
			// }
			// object.position.y = size.y;
			object.lookAt(camera.position);
		// }
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

	// requestAnimationFrame(renderGamePong);
	const timer = performance.now();
	group.rotation.x = timer * 0.0002;
	group.rotation.y = timer * 0.0001;

	const cur_delta = clock.getDelta();

	delta += cur_delta;
	server_delta += cur_delta;

	if (loaded_party != null) {
		const current_server_offset = server_delta / server_interval;

		const uuid_to_remove = loaded_party['obj_to_remove'];
		for (let uuid of uuid_to_remove) {
			removeObject(uuid);
		}
		removed_obj_list = uuid_to_remove;

		camera.position.x = 0;
		camera.position.y = 500;
		camera.position.z = -0.001;

		camera.lookAt(0, 0, 0);

		const obj_array = loaded_party['objects'];
		for (let obj of obj_array) {
			const uuid = obj['uuid'];
			let pos = new THREE.Vector3(obj['pos']['x'], FIELD_HEIGTH, obj['pos']['y']);
			const rot = obj['rot'];
			const size = new THREE.Vector3(obj['size']['x'], FIELD_HEIGTH, obj['size']['y']);
			const shape = obj['shape'];
			const velocity = new THREE.Vector3(obj['vel']['x'], FIELD_HEIGTH, obj['vel']['y']);
			const color = obj['color'];
			let text = "oeoe";
			if (obj['text'] != undefined) {
				text = obj['text'];
			}

			pos.x = pos.x + velocity.x * current_server_offset;
			pos.z = pos.z + velocity.z * current_server_offset;

			if (obj['controler'] === user.username) {
				camera.position.x = pos.x - Math.sin(rot) * 300;
				camera.position.z = pos.z - Math.cos(rot) * 300;
				camera.position.y = 200;
				camera.lookAt(pos.x, 100, pos.z);
			}

			updateOrCreateObject(uuid, pos, rot, size, shape, color, text);
		}
		setPlayerList();
	}
	skybox.position.copy(camera.position);
	//composer.render();
	renderer.render(scene, camera);

	delta = delta % interval;
}