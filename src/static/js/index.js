

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
import { getUser } from '/static/js/users/search.js';
import { settingsPopup, handleSettingsFormSubmit, setupSettingsForm, getAllInfo } from '/static/js/users/settings.js';

import { body, header, nav, main, pages, globals, base_url } from '/static/js/globals.js';


const newspaper_title = document.getElementById('newspaperTitle');
newspaper_title.addEventListener('click', () => {
    if (newspaper_title.innerHTML == 'Boston Bugle')
        notification('Congrats for finding the easter egg :)', 'check', 'success'); 
});

window.addEventListener('scroll', () => {
	const currentScroll = window.scrollY;
    if (currentScroll <= 0) {
		header.classList.remove('scrolled');
        return ;
    }
	
	if (globals.want_header === true)
		return ;
    
    if (currentScroll > globals.lastScroll && !header.classList.contains('scrolled'))
        header.classList.add('scrolled');
    else if (currentScroll < globals.lastScroll && header.classList.contains('scrolled'))
        header.classList.remove('scrolled');
		globals.lastScroll = currentScroll;
});

function blur_background() {
	main.classList.add("blurry");
	header.classList.add("blurry");
}

function unblur_background() {
	main.classList.remove("blurry");
	header.classList.remove("blurry");
}

async function onPageReload() {
	const isAuthenticated = await checkAuthentication();
	if (isAuthenticated) {
		getProfile();
		getPodium();
		setOnline();
		actualiseFriendsSection();
		setupSettingsForm();
	} else {
		header.classList.add('d-none');
		navigateToSection('register');
	}
}

onPageReload();

document.querySelectorAll('.sentence').forEach(sentence => {
    sentence.addEventListener('mouseover', () => {
        sentence.classList.add('active');
    });
    sentence.addEventListener('mouseout', () => {
        sentence.classList.remove('active');
    });
});

document.addEventListener("DOMContentLoaded", function() {
    const sentences = document.querySelectorAll('.appear-on-load');
    sentences.forEach((span, index) => {
        // Delay each sentence's animation start time
        span.style.animationDelay = `${index * 0.03}s`;
    });
});

export { blur_background, unblur_background, onPageReload };
