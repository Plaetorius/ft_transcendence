

import { chatPopup, getChatRoom, fetchRoomMessages, fetchBlockedUsers, createDomMessage, updateChatPopup, enterRoom, handleSendMessage, closeChatPopup, removeChatDisplayAndListeners, scrollToLastMessages, clearChatHeader } from '/static/js/chat/chat.js';
import { appendAndRemoveNotification, notification } from '/static/js/chat/notification.js';

import { navigateToSection, setActiveSection, hide_popups, initializeListeners, removeListeners, loadUserProfile } from '/static/js/general/navigation.js';

import { loadGames } from '/static/js/pong/pong-game.js';

import { getCookie, handleErrors, authenticated, oauth_register, checkAuthentication } from '/static/js/users/auth.js';
import { block, unblock } from '/static/js/users/block.js';
import { createActionButton, loadAndDisplayFriends, getFriends, addFriend, removeFriend, actualiseFriendsSection } from '/static/js/users/friends.js';
import { getPodium, createPodium, createRankingList } from '/static/js/users/podium.js';
import { profilePopup, getProfile, loadMyProfile, setOnline, openProfileHandler, updateProfilePopup, closeProfileHandle, handleChatClick, handleAddFriendClick, handleRemoveFriendClick, handleBlockClick, handleUnblockClick, handleGotoProfileClick } from '/static/js/users/profile.js';
import { getUser } from '/static/js/users/search.js';
import { settingsPopup, handleSettingsFormSubmit, setupSettingsForm, getAllInfo } from '/static/js/users/settings.js';

import { body, header, nav, main, pages, globals, base_url } from '/static/js/globals.js';
import { blur_background, unblur_background, onPageReload } from '/static/js/index.js';

import * as THREE from 'three';
import { EffectComposer, RenderPass, ShaderPass, SobelOperatorShader, FontLoader, TextGeometry, DotScreenShader, DotScreenPass, HalftonePass } from 'addons/Addons.js';

// import { pong_websocket } from './pong-game.js';



// sleep = (delay) => new Promise((resolve) => setTimeout(resolve, delay));

// TO CALL
// animateGamePong();

class GameCanister {
	constructor(canvas_id) {
		this.game_overlay = document.getElementById('pong_game_overlay');
		console.log(this.game_overlay);
		this.canvas = document.getElementById(canvas_id);

		this.renderer = new THREE.WebGLRenderer({ antialias: true, canvas: this.canvas });

		this.canvas = this.renderer.domElement;

		this.camera = new THREE.PerspectiveCamera(65, this.canvas.width / this.canvas.height, 0.1, 5000);
		this.camera.position.x = 0;
		this.camera.position.y = 500;
		this.camera.position.z = -0.001;
		this.camera.lookAt(0, 0, 0);

		this.composer = new EffectComposer(this.renderer);

		this.scene = new THREE.Scene();
		this.scene.background = new THREE.Color(0x222831);


		this.sky_geometry = new THREE.SphereGeometry(2, 16, 16);
		this.sky_geometry.scale(-1, 1, 1); // Inversion des normales pour l'intérieur de la sphère

		this.textureLoader = new THREE.TextureLoader();
		this.texture_sky = this.textureLoader.load('static/pong_images/sky.jpg'); // Face avant

		this.skybox = new THREE.Mesh(this.sky_geometry, new THREE.MeshBasicMaterial({ map: this.texture_sky }));
		this.skybox.renderOrder = 0;
		this.skybox.material.depthTest = false;
		this.skybox.material.depthWrite = false;

		this.group = new THREE.Group();

		this.clock = new THREE.Clock();
		this.delta = 0.0;
		this.server_delta = 0.0;

		this.interval = 1 / 60;
		this.server_interval = 1 / 30;

		this.websocket = null;
		this.party_joined = "";

		this.loaded_party = null;
		this.removed_obj_list = [];

		this.pressed = {};

		// Ajoute un RenderPass à l'EffectComposer
		const renderPass = new RenderPass(this.scene, this.camera);
		this.composer.addPass(renderPass);

		// Ajoute un FilmPass à l'EffectComposer
		// const filmPass = new FilmPass(0.5, 0.5, 1000, false);
		// const filmPass = new GlitchPass();
		// // const stensilPass = new MaskPass(scene, camera);
		// const shaderMaterial = new THREE.ShaderMaterial(DotScreenShader)
		// const shaderPass = new DotScreenPass(new THREE.Vector2(0.2, 0.2), /* angle */ 1.4, 1.5);
		const half_pass = new HalftonePass();
		half_pass.uniforms.blending.value = 0.5;
		half_pass.uniforms.blendingMode.value = 0.0;
		half_pass.uniforms.scatter.value = 0.5;
		half_pass.uniforms.greyscale.value = false;

		this.composer.addPass(half_pass);

		this.is_rendering = false;

	}

	click_close() {
		g_game_canister.game_leave();
	}

	onPressKey(event) {
		if (event.key.toLowerCase() === "escape") {
			g_game_canister.game_leave();
			return;
		}
		g_game_canister.pressed[event.key.toLowerCase()] = true;
	}

	onReleaseKey(event) {
		delete g_game_canister.pressed[event.key.toLowerCase()];
	}

	onWindowResize() {

		const new_size_x = window.innerWidth * 0.80;
		const new_size_y = window.innerHeight * 0.80;

		g_game_canister.camera.aspect = new_size_x / new_size_y;
		g_game_canister.camera.updateProjectionMatrix();
		g_game_canister.renderer.setSize(new_size_x, new_size_y);
	}

	game_join(game_id) {

		if (this.websocket != null) {
			notification("Already in a game...", null, 'error');
			return;
		}

		this.websocket = new WebSocket(`wss://${window.location.host}/ws/pong/${game_id}/`);
		this.websocket.onopen = function (event) {
			notification(`Joined game:${game_id.substring(0, 5)}`, null, 'success');
			console.log(`Joined game:${game_id.substring(0, 5)}`);

			// g_game_canister.game_overlay.addEventListener("click", g_game_canister.click_close);
			addEventListener('keydown', g_game_canister.onPressKey);
			addEventListener('keyup', g_game_canister.onReleaseKey);
			addEventListener("resize", g_game_canister.onWindowResize);

			g_game_canister.party_joined = game_id;
			g_game_canister.game_overlay.classList.add("show");
			g_game_canister.game_init();
		};

		this.websocket.onmessage = async function (event) {
			// Update UI to display the received message
			const json_data = JSON.parse(event.data);

			if (json_data["type"] === "update") {
				g_game_canister.loaded_party = json_data["party"];
				g_game_canister.server_delta = 0.0;
				g_game_canister.server_interval = json_data["party"]["second_per_frames"];

				// send keys to server only when we receive information from server
				if (this.readyState == 1) {
					let msg = {
						type: "update",
						keys: g_game_canister.pressed,
						player_name: globals.user.username,
						removed_obj: g_game_canister.removed_obj_list,
						date: Date.now()
					};
					g_game_canister.websocket.send(JSON.stringify(msg));
				}


			}
			if (json_data["type"] === "title") {
				console.log("Title: " + json_data.text + " at " + json_data.time + " with img: " + json_data.img);
				notification(json_data["text"], json_data['time'], json_data['img']);
			}
		};

		this.websocket.onerror = function (event) {
			notification(`Failed to join game:${game_id.substring(0, 5)}`, null, 'error');
			console.error("Pong WebSocket error:", event);
			console.log("error code is: ", event.code);
			console.log("error message is: ", event.message);
		};

		this.websocket.onclose = function (event) {
			console.log("Pong WebSocket closed:", event);
			g_game_canister.party_joined = "";
			g_game_canister.game_stop_render()
			g_game_canister.loaded_party = null;

			g_game_canister.game_overlay.removeEventListener("click", g_game_canister.click_close);
			removeEventListener('keydown', g_game_canister.onPressKey);
			removeEventListener('keyup', g_game_canister.onReleaseKey);
			removeEventListener("resize", g_game_canister.onWindowResize);

			g_game_canister.game_overlay.classList.remove("show");
			g_game_canister.websocket = null;
		};
	}

	game_leave() {
		if (this.websocket != null) {
			try {
				console.log("Leaving game " + this.party_joined.substring(0, 5) + "...");
				this.websocket.close();
			}
			catch (error) {
				console.error("Error while closing websocket: ", error);
			}
		}
	}

	game_init() {
		this.onWindowResize();

		// Clearing the whole scene
		this.scene.clear();

		// Adding basic elements
		this.scene.add(new THREE.DirectionalLight(0xffffff, 4));
		this.scene.add(new THREE.AmbientLight(0xffffff));
		this.scene.add(this.skybox);
		this.scene.add(this.group);

		this.camera.position.x = 0;
		this.camera.position.y = 500;
		this.camera.position.z = -0.001;
		this.camera.lookAt(0, 0, 0);

		this.skybox.position.copy(this.camera.position);

		this.game_start_render();
	}

	game_start_render() {
		this.is_rendering = true;
		this.game_render();
	}

	game_stop_render() {
		this.is_rendering = false;
	}

	game_render() {
		if (this.is_rendering === true) {

			this.game_update();

			requestAnimationFrame(this.game_render.bind(this));
		}
	}

	getObject(id) {
		let ret_obj = null;
		this.scene.traverse(function (object) {
			if (object.userId != undefined) {
				if (object.userId === id) {
					ret_obj = object;
					return;
				}
			}
		});
		return ret_obj;
	}

	removeObject(id) {
		let object = this.getObject(id);
		if (object) {
			this.scene.remove(object);
		}
	}

	updateOrCreateObject(id, position, rotation, size, shape, color) {
		let object = this.getObject(id);

		if (object == null) {
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
			} else {
				geometry = new THREE.BoxGeometry(size.x, 10, size.z);
				material = new THREE.MeshLambertMaterial({ color: color });
			}

			let cube = new THREE.Mesh(geometry, material);
			cube.position.set(position.x, position.y, position.z);
			cube.rotation.set(0, rotation, 0);
			cube.userId = id;
			this.scene.add(cube);
		} else {
			object.position.set(position.x, object.position.y, position.z);
			object.rotation.set(0, rotation, 0);
			object.material.color.set(color);
		}

	}

	game_update() {
		// requestAnimationFrame(renderGamePong);
		const timer = performance.now();

		const cur_delta = this.clock.getDelta();

		this.delta += cur_delta;
		this.server_delta += cur_delta;

		if (this.loaded_party != null) {
			const current_server_offset = this.server_delta / this.server_interval;

			const uuid_to_remove = this.loaded_party['obj_to_remove'];
			for (let uuid of uuid_to_remove) {
				this.removeObject(uuid);
			}

			this.removed_obj_list = uuid_to_remove;

			this.camera.position.x = 0;
			this.camera.position.y = 500;
			this.camera.position.z = -0.001;

			this.camera.lookAt(0, 0, 0);

			const obj_array = this.loaded_party['objects'];
			for (let obj of obj_array) {
				const uuid = obj['uuid'];
				let pos = new THREE.Vector3(obj['pos']['x'], 10, obj['pos']['y']);
				const rot = obj['rot'];
				const size = new THREE.Vector3(obj['size']['x'], 10, obj['size']['y']);
				const shape = obj['shape'];
				const velocity = new THREE.Vector3(obj['vel']['x'], 10, obj['vel']['y']);
				const color = obj['color'];

				pos.x = pos.x + velocity.x * current_server_offset;
				pos.z = pos.z + velocity.z * current_server_offset;

				if (obj['camera'] && obj['camera']['username'] === globals.user.username) {
					if (obj['camera']['mode'] == 'first_person') {
						this.camera.position.x = pos.x;
						this.camera.position.y = 60;
						this.camera.position.z = pos.z;

						this.camera.setRotationFromEuler(new THREE.Euler(0, rot + Math.PI, 0.0));
						this.camera.rotateX(-Math.PI / 4);


					} else if (obj['camera']['mode'] == 'third_person') {
						this.camera.position.x = pos.x - Math.sin(rot) * 300;
						this.camera.position.z = pos.z - Math.cos(rot) * 300;
						this.camera.position.y = 200;
						this.camera.lookAt(pos.x, 100, pos.z);
					} else if (obj['camera']['mode'] == 'top_down') {
						this.camera.position.x = pos.x;
						this.camera.position.y = 400;
						this.camera.position.z = pos.z - 0.001;
						this.camera.lookAt(pos.x, 0, pos.z);
						this.camera.rotateZ(rot);
					}

				}
				this.updateOrCreateObject(uuid, pos, rot, size, shape, color);
			}
			this.skybox.position.copy(this.camera.position);
			this.composer.render();
			// renderer.render(scene, camera);

			this.delta = this.delta % this.interval;
		}
	}
}

const g_game_canister = new GameCanister("pong_game_canvas");

export { g_game_canister };