

import {chatPopup, getChatRoom, fetchRoomMessages, fetchBlockedUsers, createDomInvitation, createDomMessage, updateChatPopup, enterRoom, handleSendMessage, closeChatPopup, removeChatDisplayAndListeners, scrollToLastMessages, clearChatHeader } from '/static/js/chat/chat.js';
import {appendAndRemoveNotification, notification } from '/static/js/chat/notification.js';

import { navigateToSection, setActiveSection, hide_popups, initializeListeners, removeListeners, loadUserProfile } from '/static/js/general/navigation.js';

import { loadGames, fetchPongCreation, pongJoinGame  } from '/static/js/pong/pong-game.js';
import { g_game_canister } from '/static/js/pong/pong-canister.js';

import { getCookie, handleErrors, authenticated, oauth_register, checkAuthentication } from '/static/js/users/auth.js';
import { block, unblock } from '/static/js/users/block.js';
import { getPodium, createPodium, createRankingList } from '/static/js/users/podium.js';
import {profilePopup, getProfile, loadMyProfile, setOnline, openProfileHandler, updateProfilePopup, closeProfileHandle, handleChatClick, handleAddFriendClick, handleRemoveFriendClick, handleBlockClick, handleUnblockClick, handleGotoProfileClick, getPlayerMatchHistory, loadMatchHistory, calculateTimeSince, getPlayerRank, loadPlayerRank} from '/static/js/users/profile.js';
import { getUser } from '/static/js/users/search.js';
import { settingsPopup, handleSettingsFormSubmit, setupSettingsForm, getAllInfo } from '/static/js/users/settings.js';

import {globals, body, header, nav, main, pages, base_url } from '/static/js/globals.js';
import { blur_background, unblur_background, onPageReload } from '/static/js/index.js';


function createActionButton(iconSrc, title, username) {
    const button = document.createElement('button');
    button.classList.add('profile-action-button');
    button.setAttribute('data-username', username);
    button.title = title;

    const img = document.createElement('img');
    img.src = iconSrc;
    img.draggable = false;

    button.appendChild(img);

    return button;
}

function loadAndDisplayFriends() {

    getFriends().then(data => {        
        const friendshipsContainer = document.getElementById('friendships');
        
        // Clear existing friends to avoid duplication
        friendshipsContainer.innerHTML = '';
        
        // Check if there are friends
        if (data.length === 0) {
            const noFriendsMessage = document.createElement('div');
            noFriendsMessage.textContent = 'No friends found.';
            friendshipsContainer.appendChild(noFriendsMessage);
            return;
        }
        
        // Iterate through each friend and create elements
        data.forEach(friendship => {
            const friend = friendship.friend_details;

            // Create a row for each friend
            const rowDiv = document.createElement('div');
            rowDiv.classList.add('row', 'd-flex', 'justify-content-center', 'align-items-center', 'w-75', 'mt-2');
            
            // Column for the friend's profile picture and name
            const colProfileDiv = document.createElement('div');
            colProfileDiv.classList.add('col-6', 'd-flex', 'justify-content-start', 'align-items-center');

            const img = document.createElement('img');
            img.src = friend.profile_picture_url;
            img.draggable = false;
            img.classList.add('friendships-profile', 'open-profile');
			img.dataset.username=friend.username;

            const span = document.createElement('span');
            span.textContent = friend.username;
            span.classList.add('friendships-profile', 'open-profile');
            span.dataset.username = friend.username;
			
            colProfileDiv.appendChild(img);
            colProfileDiv.appendChild(span);

            // Column for action buttons
            const colActionDiv = document.createElement('div');
            colActionDiv.classList.add('col-6', 'd-flex', 'flex-row', 'justify-content-end');

            // Append columns to the row
            rowDiv.appendChild(colProfileDiv);
            rowDiv.appendChild(colActionDiv);

            // Append the row to the friendships container
            friendshipsContainer.appendChild(rowDiv);
        });
    }).catch(error => {
		// console.error(error);
        // notification(`Failed to get friends`, 'cross', 'error');
    });
}

async function getFriends() {
	const response = await fetch(`/users/friends/${globals.user.username}`, {
		method: 'GET',
		headers: {
			'Content-Type': 'application/json',
		},
		credentials: 'include',
	});
	if (!response.ok) {
		return response.json().then(err => Promise.reject(err));
	}
	return await response.json();
}

function addFriend(username) {
	username = username.trim();
	if (!username)
		return "Not a valid username";
	return fetch(`/users/friend/${username}`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
		},
		credentials: 'include',
	})
	.then(response => {
		if (!response.ok) {
            return response.json().then(err => Promise.reject(err));
		}
		return response.json();
	});
}

function removeFriend(username) {
	username = username.trim();
	if (!username)
		return "Not a valid username";
	return fetch(`/users/friend/${username}`, {
		method: 'DELETE',
		headers: {
			'Content-Type': 'application/json',
		},
		credentials: 'include',
	})
	.then(response => {
		if (!response.ok) {
            return response.json().then(err => Promise.reject(err));
		}
		return response.json();
	});
}

function actualiseFriendsSection() {
	removeListeners();
	loadAndDisplayFriends();
	initializeListeners();
}

export { createActionButton, loadAndDisplayFriends, getFriends, addFriend, removeFriend, actualiseFriendsSection };
