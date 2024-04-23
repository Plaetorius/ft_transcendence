


import {chatPopup, getChatRoom, fetchRoomMessages, fetchBlockedUsers, createDomInvitation, createDomMessage, updateChatPopup, enterRoom, handleSendMessage, closeChatPopup, removeChatDisplayAndListeners, scrollToLastMessages, clearChatHeader } from '/static/js/chat/chat.js';
import {appendAndRemoveNotification, notification } from '/static/js/chat/notification.js';

import { navigateToSection, setActiveSection, hide_popups, initializeListeners, removeListeners, loadUserProfile } from '/static/js/general/navigation.js';

import { loadGames, fetchPongCreation, pongJoinGame  } from '/static/js/pong/pong-game.js';
import { g_game_canister } from '/static/js/pong/pong-canister.js';

import { block, unblock } from '/static/js/users/block.js';
import { createActionButton, loadAndDisplayFriends, getFriends, addFriend, removeFriend, actualiseFriendsSection } from '/static/js/users/friends.js';
import { getPodium, createPodium, createRankingList } from '/static/js/users/podium.js';
import {profilePopup, getProfile, loadMyProfile, setOnline, openProfileHandler, updateProfilePopup, closeProfileHandle, handleChatClick, handleAddFriendClick, handleRemoveFriendClick, handleBlockClick, handleUnblockClick, handleGotoProfileClick, getPlayerMatchHistory, loadMatchHistory, calculateTimeSince, getPlayerRank, loadPlayerRank} from '/static/js/users/profile.js';
import { getUser } from '/static/js/users/search.js';
import { settingsPopup, handleSettingsFormSubmit, setupSettingsForm, getAllInfo } from '/static/js/users/settings.js';

import { body, header, nav, main, pages, globals, base_url } from '/static/js/globals.js';
import { blur_background, unblur_background, onPageReload } from '/static/js/index.js';


// Utils
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function handleErrors(data) {
	notification(data['detail'], 'cross', 'error');
}

// Registration
document.getElementById('registerForm').addEventListener('submit', (e) => {
    e.preventDefault();
    const registerData = {
        username: document.getElementById('registerUsername').value,
        email: document.getElementById('registerEmail').value,
        password1: document.getElementById('registerPassword1').value,
        password2: document.getElementById('registerPassword2').value,
    };

    fetch('/users/register/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        },
        body: JSON.stringify(registerData),
		credentials: 'include',
    })
	.then(response => {
        if (response.ok) {
			authenticated();
        } else {
            return response.json();
        }
    })
	.then(data => {
		if (data) {
			handleErrors(data);
		}
	});
});

// Login
document.getElementById('loginForm').addEventListener('submit', (e) => {
    e.preventDefault();
    const loginData = {
        username: document.getElementById('loginUsername').value,
        password: document.getElementById('loginPassword').value,
    };

    fetch('/users/login/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        },
        body: JSON.stringify(loginData),
		credentials: 'include',
    })
	.then(response => {
        if (response.ok) {
			authenticated();
        } else {
            return response.json();
        }
    })
	.then(data => {
		if (data) {
			handleErrors(data);
		}
	});
});

document.getElementById('already-account').addEventListener('click', () => {
	navigateToSection('login');
});

document.getElementById('no-account').addEventListener('click', () => {
	navigateToSection('register');
});

function authenticated() {
	header.classList.remove("d-none");
	onPageReload();
	navigateToSection('home');
	notification('Successfully authenticated!', 'check', 'success');
}

document.getElementById("oauth-button").addEventListener("click", oauth_register);

function oauth_register() {
    const encodedCallBackUrl = encodeURI(base_url + '/users/oauth2/callback');
    const client_id = "u-s4t2ud-74b16c2e5ea3a21411f68f94d3baa9360412380b7ee6088672f7028ffcac8652";
    const authUrl = `https://api.intra.42.fr/oauth/authorize?client_id=${client_id}&redirect_uri=${encodedCallBackUrl}&response_type=code`;
    window.location.href = authUrl;
}

document.addEventListener('DOMContentLoaded', function() {
    const currentUrl = window.location.href;
    if (currentUrl.includes('/users/oauth2/callback')) {
        window.location.href = base_url + '/#home';
    }
});

async function checkAuthentication() {
    try {
        const response = await fetch('/users/check-session/', {
            method: 'GET',
            credentials: 'include',  
        });

        if (!response.ok) {
            throw new Error('Not authenticated');
        }

        const data = await response.json();
        return true;
    } catch (error) {
        header.classList.add('d-none');
        navigateToSection('register');
        return false;
    }
}

export { getCookie, handleErrors, authenticated, oauth_register, checkAuthentication };