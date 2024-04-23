

import {chatPopup, getChatRoom, fetchRoomMessages, fetchBlockedUsers, createDomInvitation, createDomMessage, updateChatPopup, enterRoom, handleSendMessage, closeChatPopup, removeChatDisplayAndListeners, scrollToLastMessages, clearChatHeader } from '/static/js/chat/chat.js';
import {appendAndRemoveNotification, notification } from '/static/js/chat/notification.js';

import { navigateToSection, setActiveSection, hide_popups, initializeListeners, removeListeners, loadUserProfile } from '/static/js/general/navigation.js';

import { loadGames, fetchPongCreation, pongJoinGame  } from '/static/js/pong/pong-game.js';
import { g_game_canister } from '/static/js/pong/pong-canister.js';

import { getCookie, handleErrors, authenticated, oauth_register, checkAuthentication } from '/static/js/users/auth.js';
import { block, unblock } from '/static/js/users/block.js';
import { createActionButton, loadAndDisplayFriends, getFriends, addFriend, removeFriend, actualiseFriendsSection } from '/static/js/users/friends.js';
import { getPodium, createPodium, createRankingList } from '/static/js/users/podium.js';
import {profilePopup, getProfile, loadMyProfile, setOnline, openProfileHandler, updateProfilePopup, closeProfileHandle, handleChatClick, handleAddFriendClick, handleRemoveFriendClick, handleBlockClick, handleUnblockClick, handleGotoProfileClick, getPlayerMatchHistory, loadMatchHistory, calculateTimeSince, getPlayerRank, loadPlayerRank} from '/static/js/users/profile.js';
import { getUser } from '/static/js/users/search.js';

import { body, header, nav, main, pages, globals, base_url } from '/static/js/globals.js';
import { blur_background, unblur_background, onPageReload } from '/static/js/index.js';


const settingsPopup = document.getElementById("settings-popup");

// Open Settings Popup
document.querySelectorAll(".open-settings").forEach(element => {
    element.addEventListener('click', (event) => {
        event.stopPropagation();
        hide_popups();
        settingsPopup.classList.remove("d-none");
        settingsPopup.classList.add("d-block");
        blur_background();
    });
});

// Close Settings Popup 
document.addEventListener('click', (event) => {
    if (!settingsPopup.contains(event.target) && !event.target.matches('.open-settings') && !event.target.closest('.settings-picture')) {
        event.stopPropagation();
        settingsPopup.classList.add("d-none");
        settingsPopup.classList.remove("d-block");
        unblur_background();
    }
});

const settingsForm = document.getElementById('settings-form');
const profilePictureInput = document.getElementById('profile-picture-input');
const profilePicturePreview = document.getElementById('profile-picture-preview');

// Trigger the file input when the profile picture is clicked
document.querySelector('.settings-picture').addEventListener('click', function() {
    profilePictureInput.click();
});

// Update the profile picture preview when a new picture is selected
profilePictureInput.addEventListener('change', function() {
    if (this.files && this.files[0]) {
        var reader = new FileReader();
        reader.onload = function(e) {
            profilePicturePreview.src = e.target.result;
        };
        reader.readAsDataURL(this.files[0]);
    }
});

// Handle form submission
async function handleSettingsFormSubmit(e) {
    e.preventDefault();
    const formData = new FormData(settingsForm);
    const profilePictureInput = document.getElementById('profile-picture-input');

    // Check if file is larger than 4MB
    if (profilePictureInput.files.length > 0) {
        const file = profilePictureInput.files[0];
        const maxSize = 4 * 1024 * 1024; // 4MB in bytes

        if (file.size > maxSize) {
            notification('File is too large. Maximum size is 4MB.', 'cross', 'error');
            return; // Stop the function if the file is too large
        }
        formData.append('profile_picture', file);
    }

    try {
        const response = await fetch('/users/edit-user/', {
            method: 'PATCH',
            credentials: 'include',
            body: formData,
        });

        if (!response.ok) {
            if (response.headers.get('Content-Type').includes('application/json')) {
                // Process JSON error response
                const errorData = await response.json();
                handleErrors(errorData.error || 'Failed to update profile');
            } else {
                // Handle non-JSON responses
                const errorText = await response.text();
                handleErrors(`Try a smaller file`);
            }
        } else {
            const data = await response.json();
            setupSettingsForm();
            getProfile();
            notification('Profile updated!', 'check', 'success');
        }
    } catch (error) {
        notification('An error occurred while updating your profile.', 'cross', 'error');
    }
}

settingsForm.addEventListener('submit', handleSettingsFormSubmit);

async function setupSettingsForm() {
    try {
        const userData = await getAllInfo();
        if (!userData) {
			notification("Error fetching user data", 'cross', 'error');
			return;
        }

        // Set form field values
        document.getElementById('settings-username').value = userData.username || '';
        document.getElementById('settings-email').value = userData.email || '';
        document.getElementById('settings-first-name').value = userData.first_name || '';
        document.getElementById('settings-last-name').value = userData.last_name || '';
        document.getElementById('settings-bio').value = userData.bio || '';

        // Set profile picture preview
        const profilePicturePreview = document.getElementById('profile-picture-preview');
        if (userData.profile_picture_url) {
            profilePicturePreview.src = userData.profile_picture_url;
        } else {
            // Set to a default image if no profile picture URL is provided
            profilePicturePreview.src = '../media/profile_pictures/default.jpg';
        }

    } catch (error) {
		notification("Error in settings form", 'cross', 'error');
	}
}

async function getAllInfo() {
    try {
        const response = await fetch(`/users/edit-user/`, {
			method: 'GET',
            credentials: 'include',
        });
        if (!response.ok) {
            throw new Error("Error fetching the data");
        }
        const userData = await response.json();
        return userData.data;
    } catch (error) {
		notification(error, 'cross', 'error');
    }
}

export { settingsPopup, handleSettingsFormSubmit, setupSettingsForm, getAllInfo };
