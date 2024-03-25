
import * as THREE from '../../three.js-master/build/three.module.js';

let container;
let camera, scene, renderer;
let field_material;
let group;

const FIELD_LENGTH = 500;
const FIELD_WIDTH = 200;
const FIELD_HEIGTH = 10;

console.log("Before Init pong game called");

init();
animate();

function init() {
	console.log("Init pong game called");

	container = document.getElementById('canvas');
	renderer = new THREE.WebGLRenderer();
	renderer.setSize(window.innerWidth, window.innerHeight);
	container.appendChild(renderer.domElement);

	camera = new THREE.PerspectiveCamera(65, window.innerWidth / window.innerHeight, 100, 700);
	camera.position.z = 400;
	camera.position.y = -200;

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

		mesh.scale.setScalar(Math.random() * 2 + 2);
		group.add(mesh);

	}

	window.addEventListener('resize', onWindowResize);

}

function onWindowResize() {

	const width = window.innerWidth;
	const height = window.innerHeight;

	camera.aspect = width / height;
	camera.updateProjectionMatrix();

	renderer.setSize(width, height);

}

function animate() {

	requestAnimationFrame(animate);

	console.log("Animate pong game called");

	render();

}

function render() {

	const timer = performance.now();
	group.rotation.x = timer * 0.0002;
	group.rotation.y = timer * 0.0001;

	renderer.render(scene, camera);

}