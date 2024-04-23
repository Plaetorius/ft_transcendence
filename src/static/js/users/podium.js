

import {chatPopup, getChatRoom, fetchRoomMessages, fetchBlockedUsers, createDomMessage, updateChatPopup, enterRoom, handleSendMessage, closeChatPopup, removeChatDisplayAndListeners, scrollToLastMessages, clearChatHeader } from '/static/js/chat/chat.js';
import {appendAndRemoveNotification, notification } from '/static/js/chat/notification.js';

import { navigateToSection, setActiveSection, hide_popups, initializeListeners, removeListeners, loadUserProfile } from '/static/js/general/navigation.js';

import { loadGames } from '/static/js/pong/pong-game.js';
import { g_game_canister } from '/static/js/pong/pong-canister.js';

import { getCookie, handleErrors, authenticated, oauth_register, checkAuthentication } from '/static/js/users/auth.js';
import { block, unblock } from '/static/js/users/block.js';
import { createActionButton, loadAndDisplayFriends, getFriends, addFriend, removeFriend, actualiseFriendsSection } from '/static/js/users/friends.js';
import {profilePopup, getProfile, loadMyProfile, setOnline, openProfileHandler, updateProfilePopup, closeProfileHandle, handleChatClick, handleAddFriendClick, handleRemoveFriendClick, handleBlockClick, handleUnblockClick, handleGotoProfileClick } from '/static/js/users/profile.js';
import { getUser } from '/static/js/users/search.js';
import { settingsPopup, handleSettingsFormSubmit, setupSettingsForm, getAllInfo } from '/static/js/users/settings.js';

import { body, header, nav, main, pages, globals, base_url } from '/static/js/globals.js';
import { blur_background, unblur_background, onPageReload } from '/static/js/index.js';


async function getPodium() {
    try {
        const response = await fetch(`/users/podium/`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
			},
			credentials: 'include',
        });

        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.message);
        }

        const users = await response.json();
        createPodium(users);
        createRankingList(users);
    } catch (error) {
        notificationr(error, 'cross', 'error');
    }
}

function createPodium(users) {
    // Assuming the first three users are the top players for the podium
    const podiumPlaces = ['first-place', 'second-place', 'third-place'];

    podiumPlaces.forEach((place, index) => {
        if (users[index]) { // Check if the user exists
            const container = document.getElementById(place);
            container.innerHTML = ''; // Clear existing content
            const img = document.createElement('img');
            img.src = users[index].profile_picture_url ? users[index].profile_picture_url : '../media/profile_pictures/default.jpg';
            img.draggable = false;
            img.className = 'podium-profile open-profile';
            img.setAttribute('data-username', users[index].username);
            container.appendChild(img);
        }
    });
}

function createRankingList(users) {
    const listContainer = document.getElementById('podium-list');
    listContainer.innerHTML = ''; // Clear existing content

    // Start from the 4th user since the first three are on the podium
    users.slice(3).forEach((user, index) => {
        const row = document.createElement('div');
        row.className = 'row';

        const col = document.createElement('div');
        col.className = 'col d-flex align-items-center';

        const position = document.createElement('span');
        position.textContent = `${index + 4}.`;
        
        const img = document.createElement('img');
        img.src = globals.user.profile_picture_url;
        img.draggable = false;
        img.className = 'podium-profile open-profile';
        img.setAttribute('data-username', globals.user.username);
        
        const usernameSpan = document.createElement('span');
        usernameSpan.className = 'podium-profile open-profile d-flex align-items-center';
        usernameSpan.setAttribute('data-username', globals.user.username);
        usernameSpan.textContent = globals.user.username;

        col.appendChild(position);
        col.appendChild(img);
        col.appendChild(usernameSpan);
        row.appendChild(col);

        listContainer.appendChild(row);
    });
}

export { getPodium, createPodium, createRankingList };
