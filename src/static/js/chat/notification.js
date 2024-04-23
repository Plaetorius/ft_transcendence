

import {chatPopup, getChatRoom, fetchRoomMessages, fetchBlockedUsers, createDomMessage, updateChatPopup, enterRoom, handleSendMessage, closeChatPopup, removeChatDisplayAndListeners, scrollToLastMessages, clearChatHeader } from '/static/js/chat/chat.js';


import { navigateToSection, setActiveSection, hide_popups, initializeListeners, removeListeners, loadUserProfile } from '/static/js/general/navigation.js';

import { loadGames } from '/static/js/pong/pong-game.js';
import { g_game_canister } from '/static/js/pong/pong-canister.js';

import { getCookie, handleErrors, authenticated, oauth_register, checkAuthentication } from '/static/js/users/auth.js';
import { block, unblock } from '/static/js/users/block.js';
import { createActionButton, loadAndDisplayFriends, getFriends, addFriend, removeFriend, actualiseFriendsSection } from '/static/js/users/friends.js';
import { getPodium, createPodium, createRankingList } from '/static/js/users/podium.js';
import {profilePopup, getProfile, loadMyProfile, setOnline, openProfileHandler, updateProfilePopup, closeProfileHandle, handleChatClick, handleAddFriendClick, handleRemoveFriendClick, handleBlockClick, handleUnblockClick, handleGotoProfileClick } from '/static/js/users/profile.js';
import { getUser } from '/static/js/users/search.js';
import { settingsPopup, handleSettingsFormSubmit, setupSettingsForm, getAllInfo } from '/static/js/users/settings.js';

import { body, header, nav, main, pages, globals, base_url } from '/static/js/globals.js';
import { blur_background, unblur_background, onPageReload } from '/static/js/index.js';


// Create a function to append the notification and remove it after a time
function appendAndRemoveNotification(element_list, message, type, delay = 3000) {
	// Create a new list item
	const listItem = document.createElement('li');

	listItem.innerHTML = message;
	listItem.style.z_index = 999;

	listItem.classList.add('notif-item');

	if (type)
		listItem.classList.add(type);


	// Append the new list item to the list
	element_list.appendChild(listItem);

	// First show the notification, then remove it
	setTimeout(() => {
		listItem.classList.add('show');
		setTimeout(() => {
			listItem.classList.remove('show');
			setTimeout(() => {
				element_list.removeChild(listItem);
			}, 600);
		}, delay);
	}, 100);

}

function notification(message, pathToIcon, type, delay = 3) {
	// Set a default icon
	// if (!pathToIcon)
	// 	pathToIcon = '../static/icons/bell.png';
	// else
	// 	pathToIcon = '../static/icons/' + pathToIcon + '.png';


	// Select the notification container and its components
	// const notificationContainer = document.getElementById('notification');
	// const notificationIcon = notificationContainer.querySelector('.col-3 img');
	// const notificationMessage = notificationContainer.querySelector('.col-9');

	// Add type if any (types are: success, error)
	
	// console.log('Notification:', message, type, delay);

	// ALAN's take at notifications
	const element_list = document.getElementById('list-notifications');
	// Call the function
	appendAndRemoveNotification(element_list, message, type, delay * 1000);


	// Update the icon's src attribute and message content
	// notificationIcon.src = pathToIcon;
	// notificationMessage.innerHTML = message;

	// // Make the notification visible
	// notificationContainer.classList.remove('d-none');

	// // Hide the notification after 3 seconds (3000 milliseconds)
	// setTimeout(() => {
	// 	notificationContainer.classList.add('d-none');
	// 	// Remove type if any
	// 	if (type)
	// 		notificationContainer.classList.remove(type);
	// }, 3000);
}

export { appendAndRemoveNotification, notification };
