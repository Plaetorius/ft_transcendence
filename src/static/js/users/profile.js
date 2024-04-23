



import {chatPopup, getChatRoom, fetchRoomMessages, fetchBlockedUsers, createDomInvitation, createDomMessage, updateChatPopup, enterRoom, handleSendMessage, closeChatPopup, removeChatDisplayAndListeners, scrollToLastMessages, clearChatHeader } from '/static/js/chat/chat.js';
import {appendAndRemoveNotification, notification } from '/static/js/chat/notification.js';

import { navigateToSection, setActiveSection, hide_popups, initializeListeners, removeListeners, loadUserProfile } from '/static/js/general/navigation.js';

import { loadGames, fetchPongCreation, pongJoinGame  } from '/static/js/pong/pong-game.js';
import { g_game_canister } from '/static/js/pong/pong-canister.js';

import { getCookie, handleErrors, authenticated, oauth_register, checkAuthentication } from '/static/js/users/auth.js';
import { block, unblock } from '/static/js/users/block.js';
import { createActionButton, loadAndDisplayFriends, getFriends, addFriend, removeFriend, actualiseFriendsSection } from '/static/js/users/friends.js';
import { getPodium, createPodium, createRankingList } from '/static/js/users/podium.js';
import { getUser } from '/static/js/users/search.js';
import { settingsPopup, handleSettingsFormSubmit, setupSettingsForm, getAllInfo } from '/static/js/users/settings.js';

import {globals, body, header, nav, main, pages, base_url } from '/static/js/globals.js';
import { blur_background, unblur_background, onPageReload } from '/static/js/index.js';


function getProfile() {
	fetch('/users/profile/', {
			method: 'GET',
			headers: {
				'Content-Type': 'application/json',
			},
			credentials: 'include',
		})
		.then(response => {
			if (!response.ok) {
				throw new Error('User not found');
			}
			return response.json();
		})
		.then(userData => {
			globals.user = userData;
			document.getElementById("profile-picture").src = userData.profile_picture_url;
			loadMyProfile();
			actualiseFriendsSection();
			getPlayerMatchHistory(globals.user.username, 'profile-history');
      		getPlayerRank(globals.user.username, 'profile');
		})
		.catch(error => {
			notification(error, 'cross', 'error');
			console.log(error);
		});
}

function loadMyProfile() {
	document.getElementById("profile-picture").src = globals.user.profile_picture_url;
	document.getElementById("header-profile-picture").src = globals.user.profile_picture_url;
	document.getElementById("profile-username").innerHTML = `<span class="online-status online"></span>${globals.user.username}`;
	document.getElementById("profile-elo").innerHTML = `<span>Elo: </span>${globals.user.elo}`;
	const dateJoined = new Date(globals.user.date_joined);
	const formattedDate = [
		dateJoined.getDate().toString().padStart(2, '0'),
		(dateJoined.getMonth() + 1).toString().padStart(2, '0'),
		dateJoined.getFullYear()
	].join('/');

	document.getElementById("profile-joined").innerHTML = `<span>Joined: </span>${formattedDate}`;
}

// Socket serves both at checking if user is online
// AND send notifications to the user
let notificationSocket = undefined;

function setOnline() {
	notificationSocket = new WebSocket(`wss://${window.location.host}/ws/user-status/`);

	notificationSocket.onopen = (e) => {
		notification("You are online!", "check", "success");
	};

	notificationSocket.onmessage = (e) => {
		const data = JSON.parse(e.data);
		console.log("DATA FOR GLOBAL MESSAGE :");
		console.log(data);
		notification(data.message, data.path_to_icon, data.context);
	};

	notificationSocket.onclose = (e) => {

	};
}

const profilePopup = document.getElementById("profile-popup");

// Open Profile Popup, handle buttons click
async function openProfileHandler(event) {
	let targetElement = event.target;

	// Traverse up to find the element with .open-profile
	while (targetElement != null && !targetElement.matches('.open-profile')) {
		targetElement = targetElement.parentElement;
	}

	// If a .open-profile element was clicked
	if (targetElement) {
		event.stopPropagation();
		hide_popups();

		try {
			// Await the getUser promise and then log the data
			const userProfile = await getUser(targetElement.dataset.username);
			updateProfilePopup(userProfile);
			profilePopup.classList.remove("d-none");
			profilePopup.classList.add("d-block");
			blur_background();
		} catch (error) {
			notification("Error fetching user data", "cross", "error");
		}
	}
}

function updateProfilePopup(user) {
	let titleElem = profilePopup.querySelector("h5");

	// Clear existing online-status span if any
	let existingStatus = titleElem.querySelector('.online-status');
	if (existingStatus) {
		existingStatus.remove();
	}

	// Create and add new online status span
	let onlineElem = document.createElement("span");
	onlineElem.classList.add("online-status", user.is_online ? "online" : "offline");
	titleElem.innerText = user.username;
	titleElem.insertBefore(onlineElem, titleElem.firstChild);

	let imgElem = profilePopup.querySelector('img.profile-picture');
	imgElem.src = user.profile_picture_url;
	imgElem.draggable = false;


	// Convert the string into a Date object
	const date = new Date(user.date_joined);

	// Use Intl.DateTimeFormat to format the date
	const options = { day: 'numeric', month: 'numeric', year: 'numeric' };

	const formattedDate = new Intl.DateTimeFormat('fr-FR', options).format(date);

	// Update other user information
	profilePopup.querySelector('#profile-popup-elo').innerHTML = `<span class="attribute">Elo: </span>${user.elo}`;
	profilePopup.querySelector('#profile-popup-joined').innerHTML = `<span class="attribute">Date Joined: </span>${formattedDate}`;
	profilePopup.querySelector('#profile-popup-bio').innerHTML = `<span class="attribute">Bio: </span>${user.bio}`;

	// Update buttons with the user's username
	const buttonsToUpdate = profilePopup.querySelectorAll('button[data-username]');
	buttonsToUpdate.forEach(button => {
		button.dataset.username = user.username;
	});
}

// Close Profile Popup, handle buttons click
function closeProfileHandle(event) {
	if (!profilePopup.contains(event.target) && !event.target.matches('.open-profile')) {
		event.stopPropagation();
		profilePopup.classList.add("d-none");
		profilePopup.classList.remove("d-block");
		unblur_background();
	}

	const button = event.target.closest('button');
	if (button) {
		const username = button.dataset.username;
		if (username) {
			if (button.matches('button.open-chat')) {
				handleChatClick(username);
			} else if (button.matches('button.add-friend')) {
				handleAddFriendClick(username);
			} else if (button.matches('button.remove-friend')) {
				handleRemoveFriendClick(username);
			} else if (button.matches('button.block')) {
				handleBlockClick(username);
			} else if (button.matches('button.unblock')) {
				handleUnblockClick(username);
			} else if (button.matches('button.goto-profile')) {
				handleGotoProfileClick(username);
			}
		}
	}
}

function handleChatClick(username) {
    hide_popups();
    getChatRoom(username).then(success => {
        if (success) {
            chatPopup.classList.remove("d-none");
            chatPopup.classList.add("d-block");
            blur_background();
            document.addEventListener('click', closeChatPopup);
            scrollToLastMessages();
        }
    });
}

function handleAddFriendClick(username) {
	addFriend(username).then(data => {
		// Handle success, update the UI accordingly
		notification(`Friend added: ${data.success}`, "check", "success");
		actualiseFriendsSection();
	}).catch(error => {
		// Log the backend error message if it exists, otherwise log a default error message
		// Handle failure, perhaps show a message to the user
		notification(`${error.error ? error.error : 'An error occurred'}`, "cross", "error");
	});
}

function handleRemoveFriendClick(username) {
	removeFriend(username).then(data => {
		// Handle success, update the UI accordingly
		notification(`Friend removed: ${data.success}`, "check", "success");
		actualiseFriendsSection();
	}).catch(error => {
		// Log the backend error message if it exists, otherwise log a default error message
		// Handle failure, perhaps show a message to the user
		notification(`${error.error ? error.error : 'An error occurred'}`, "cross", "error");
	});
}

function handleBlockClick(username) {
	block(username).then(data => {
		// Handle success, update the UI accordingly
		notification(`Blocked ${data.success}!`, "check", "cross");
	}).catch(error => {
		// Log the backend error message if it exists, otherwise log a default error message
		// Handle failure, perhaps show a message to the user
		notification(`Failed to block: ${error.error ? error.error : 'An error occurred'}`, "cross", "error");
	});
}

function handleUnblockClick(username) {
	unblock(username).then(data => {
		// Handle success, update the UI accordingly
		notification(`Unblock: ${data.success}`, "check", "error");
	}).catch(error => {
		// Log the backend error message if it exists, otherwise log a default error message
		// Handle failure, perhaps show a message to the user
		notification(`Failed to unblock: ${error.error ? error.error : 'An error occurred'}`, "cross", "error");
		notification(`Failed to unblock: ${error.error ? error.error : 'An error occurred'}`, "cross", "error");
	});
}

async function handleGotoProfileClick(username) {
	let visited_user = await getUser(username);
	if (!visited_user) {
		notification("User not found!", "cross", "error");
		return;
	}
	document.getElementById("user-picture").src = visited_user.profile_picture_url;
	document.getElementById("user-username").innerHTML = `<span class="online-status online"></span>${visited_user.username}`;
	document.getElementById("user-elo").innerHTML = `<span>Elo: </span>${visited_user.elo}`;
	const dateJoined = new Date(visited_user.date_joined);
	const formattedDate = [
		dateJoined.getDate().toString().padStart(2, '0'),
		(dateJoined.getMonth() + 1).toString().padStart(2, '0'),
		dateJoined.getFullYear()
	].join('/');
	document.getElementById("user-joined").innerHTML = `<span>Joined: </span>${formattedDate}`;

	navigateToSection('user', { username: username });
	profilePopup.classList.add("d-none");
	profilePopup.classList.remove("d-block");
}

function getPlayerMatchHistory(username, containerId) {
	if (!username)
		return ;
	fetch(`/users/match-history/${username}`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        },
        credentials: 'include',
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('User not found');
        }
        return response.json();
    })
    .then(matchHistory => {
        loadMatchHistory(matchHistory, username, containerId);
    })
    .catch(error => {
        notification(error, 'cross', 'error');
    });
}

let isLoadingHistory = false;

async function loadMatchHistory(matchHistory, username, containerId) {
    if (isLoadingHistory) return; 
    isLoadingHistory = true; 

    const profileContainer = document.getElementById(containerId); 
    profileContainer.innerHTML = '';

    matchHistory.sort((a, b) => new Date(b.date_played) - new Date(a.date_played));

    for (const match of matchHistory) {
        const currentPlayer = match.players.find(player => player.username === username);
        const opponent = match.players.find(player => player.username !== username);

        const currentPlayerWin = currentPlayer.score > opponent.score;
        const resultClass = currentPlayerWin ? 'history-win' : 'history-loss';
        const resultText = currentPlayerWin ? 'WIN' : 'LOSS';

        // Get additional user data
        const currentPlayerData = await getUser(currentPlayer.username);
        const opponentData = await getUser(opponent.username);

        // Format the Elo change text
        const eloChangeText = (currentPlayer.elo_change > 0 ? `+${currentPlayer.elo_change}` : currentPlayer.elo_change) + ' elo';

        // Create match HTML block
        const matchDiv = document.createElement('div');
        matchDiv.className = `container-fluid w-100 d-flex justify-content-center flex-wrap`;
        matchDiv.innerHTML = `
            <div class="row d-inline-flex w-75 mx-0 my-1 py-2 px-0 justify-content-around history-row ${resultClass}">
                <div class="col-2 d-flex justify-content-center mx-0 my-2 p-0">
                    <img class="history-profile-picture open-profile" data-username="${currentPlayer.username}"
                         src="${currentPlayerData.profile_picture_url}" draggable="false">
                </div>
                <div class="col-2 m-0 p-0 d-flex flex-column align-items-center justify-content-center">
                    <div class="history-game-result">${resultText}</div>
                    <div class="history-game-time">${match.duration.split('.')[0]}</div>
                    <div class="history-game-type">${match.game_type}</div>
                    <div class="history-time-since">${calculateTimeSince(match.date_played)}</div>
                </div>
                <div class="col-2 m-0 p-0 d-flex flex-column align-items-center justify-content-center">
                    <div class="history-game-score">${currentPlayer.score} / ${opponent.score}</div>
                    <div class="history-game-elo">${eloChangeText}</div>
                </div>
                <div class="col-2 d-flex justify-content-center mx-0 my-2 p-0">
                    <img class="history-profile-picture open-profile" data-username="${opponent.username}"
                         src="${opponentData.profile_picture_url}" draggable="false">
                </div>
            </div>
        `;

        // Append to the main container
        profileContainer.appendChild(matchDiv);
    }
    isLoadingHistory = false;
}

function calculateTimeSince(datePlayed) {
    const date = new Date(datePlayed);
    const now = new Date();
    const diffMs = now - date;  // difference in milliseconds
    const diffMin = Math.floor(diffMs / (1000 * 60));
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

    if (diffDays >= 1) {
        // More than 24 hours ago, show the date
        return date.toLocaleDateString('en-US', {
            year: 'numeric', month: 'long', day: 'numeric'
        });
    } else if (diffHours >= 1) {
        // Less than 24 hours but more than an hour ago, show hours
        return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
    } else {
        // Less than an hour ago, show minutes
        return `${diffMin} minute${diffMin > 1 ? 's' : ''} ago`;
    }
}

function getPlayerRank(username, containerId) {
	if (!username)
		return ;
    fetch(`/users/rank/${username}/`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        },
        credentials: 'include',
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('User not found');
        }
        return response.json();
    })
    .then(stats => {
        loadPlayerRank(stats, containerId);
    })
    .catch(error => {
        notification(error, 'cross', 'error');
    });
}

let loadingRank = false;

function loadPlayerRank(stats, containerId) {
    if (loadingRank) return;
    loadingRank = true;

    document.getElementById(`${containerId}-rank`).innerHTML = `<span>Rank: </span>#${stats.rank}`;
    document.getElementById(`${containerId}-winrate`).innerHTML = `<span>Winrate: </span>${Math.round(stats.win_rate)}%`;
    loadingRank = false;

}

export { profilePopup, getProfile, loadMyProfile, setOnline, openProfileHandler, updateProfilePopup, closeProfileHandle, handleChatClick, handleAddFriendClick, handleRemoveFriendClick, handleBlockClick, handleUnblockClick, handleGotoProfileClick, getPlayerMatchHistory, loadMatchHistory, calculateTimeSince, getPlayerRank, loadPlayerRank };