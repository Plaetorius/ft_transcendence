

import {chatPopup, getChatRoom, fetchRoomMessages, fetchBlockedUsers, createDomMessage, updateChatPopup, enterRoom, handleSendMessage, closeChatPopup, removeChatDisplayAndListeners, scrollToLastMessages, clearChatHeader } from '/static/js/chat/chat.js';
import {appendAndRemoveNotification, notification } from '/static/js/chat/notification.js';

import { navigateToSection, setActiveSection, hide_popups, initializeListeners, removeListeners, loadUserProfile } from '/static/js/general/navigation.js';

import { loadGames } from '/static/js/pong/pong-game.js';
import { g_game_canister } from '/static/js/pong/pong-canister.js';

import { getCookie, handleErrors, authenticated, oauth_register, checkAuthentication } from '/static/js/users/auth.js';
import { block, unblock } from '/static/js/users/block.js';
import { createActionButton, loadAndDisplayFriends, getFriends, addFriend, removeFriend, actualiseFriendsSection } from '/static/js/users/friends.js';
import { getPodium, createPodium, createRankingList } from '/static/js/users/podium.js';
import {profilePopup, getProfile, loadMyProfile, setOnline, openProfileHandler, updateProfilePopup, closeProfileHandle, handleChatClick, handleAddFriendClick, handleRemoveFriendClick, handleBlockClick, handleUnblockClick, handleGotoProfileClick } from '/static/js/users/profile.js';
import { settingsPopup, handleSettingsFormSubmit, setupSettingsForm, getAllInfo } from '/static/js/users/settings.js';

import { body, header, nav, main, pages, globals, base_url } from '/static/js/globals.js';
import { blur_background, unblur_background, onPageReload } from '/static/js/index.js';

document.getElementById('userSearchForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const usernameInput = document.getElementById('searchUsername');
    const username = usernameInput.value;
	usernameInput.value = '';

	addFriend(username).then(data => {
        // Handle success, update the UI accordingly
		notification(`Friend added: ${data.success}`, "check", "success");
		actualiseFriendsSection();
    }).catch(error => {
        // Log the backend error message if it exists, otherwise log a default error message
        // Handle failure, perhaps show a message to the user
        notification(`Failed to add friend: ${error.error ? error.error : 'An error occurred'}`, "cross", "error");
    });
	actualiseFriendsSection();
});

async function getUser(username) {
	const response = await fetch(`/users/search/${encodeURIComponent(username)}/`, {
		method: 'GET',
		headers: {
			'Content-Type': 'application/json',
		},
		credentials: 'include',
	});
	if (!response.ok) {
		notification("User not found", "cross", "error");
		throw new Error("User not found!");
	}
	const userData = await response.json();
	return userData;	
}

export { getUser };
