function showProfile() {
	console.log("Call Show Profile");
    fetch('/users/profile/', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('accessToken')}`
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('User not found');
        }
        // TODO hide error in the console
        return response.json();
    })
    .then(userData => {
        user = userData;
		document.getElementById("my-profile-picture").src = user.profile_picture_url;
		loadMyProfile();
		loadAndDisplayFriends();
    })
    .catch(error => {
		console.log(error);
	});
}

function loadMyProfile() {
    document.getElementById("my-profile-picture").src = user.profile_picture_url;
    document.getElementById("my-profile-username").innerHTML = `<span class="online-status online"></span>${user.username}`;
    document.getElementById("my-profile-elo").innerHTML = `<span>Elo: </span>${user.elo}`;
    const dateJoined = new Date(user.date_joined);
    const formattedDate = [
        dateJoined.getDate().toString().padStart(2, '0'),
        (dateJoined.getMonth() + 1).toString().padStart(2, '0'),
        dateJoined.getFullYear()
    ].join('/');

    document.getElementById("my-profile-joined").innerHTML = `<span>Joined: </span>${formattedDate}`;
}

// Socket serves both at checking if user is online
// AND send notifications to the user
let notificationSocket = undefined;

function setOnline() {
	console.log("Set online called");
    const token = localStorage.getItem('accessToken');
    notificationSocket = new WebSocket(`wss://${window.location.host}/ws/user-status/?token=${token}`);

    notificationSocket.onopen = (e) => {
        console.log(`You are online`);
    };

    notificationSocket.onmessage = (e) => {
        const data = JSON.parse(e.data);
        notification(data);
    };

    notificationSocket.onclose = (e) => {
        console.log(`You turned offline`);
    };
}

// showProfile();

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
			console.log(`openProfileHandler`, userProfile);
			updateProfilePopup(userProfile);
			profilePopup.classList.remove("d-none");
			profilePopup.classList.add("d-block");
			blur_background();
		} catch (error) {
			console.error('Error fetching user data:', error);
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
    // profilePopup.querySelector('#profile-popup-rank span.attribute + span').textContent = `#${user.rank}`; TODO implement
    profilePopup.querySelector('#profile-popup-elo').innerHTML = `<span class="attribute">Elo: </span>${user.elo}`;
    // profilePopup.querySelector('#profile-popup-winrate span.attribute + span').textContent = user.winrate; // TODO implement
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
				console.log("Comparing");
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
	console.log(`handleChatlick called to chat: ${username}`);
	hide_popups();
	getChatRoom(username);
	chatPopup.classList.remove("d-none");
	chatPopup.classList.add("d-block");
	blur_background();
	document.addEventListener('click', closeChatPopup);
	scrollToLastMessages();


}

function handleAddFriendClick(username) {
	console.log("Add friend clicked for user:", username);
	
	addFriend(username).then(data => {
        console.log(`Friend added: ${data.success}`);
		actualiseFriendsSection();
        // Handle success, update the UI accordingly
    }).catch(error => {
        // Log the backend error message if it exists, otherwise log a default error message
        console.log(`Failed to add friend: ${error.error ? error.error : 'An error occurred'}`);
        // Handle failure, perhaps show a message to the user
    });
}

function handleRemoveFriendClick(username) {
    console.log("Remove friend clicked for user:", username);
    removeFriend(username).then(data => {
        console.log(`Friend removed: ${data.success}`);
		actualiseFriendsSection();
        // Handle success, update the UI accordingly
    }).catch(error => {
        // Log the backend error message if it exists, otherwise log a default error message
        console.log(`Failed to remove friend: ${error.error ? error.error : 'An error occurred'}`);
        // Handle failure, perhaps show a message to the user
    });
}

function handleBlockClick(username) {
	console.log("Block clicked for user:", username);
	
	block(username).then(data => {
        console.log(`Block: ${data.success}`);
        // Handle success, update the UI accordingly
    }).catch(error => {
        // Log the backend error message if it exists, otherwise log a default error message
        console.log(`Failed to block: ${error.error ? error.error : 'An error occurred'}`);
        // Handle failure, perhaps show a message to the user
    });
}

function handleUnblockClick(username) {
    console.log("Unblock clicked for user:", username);
    unblock(username).then(data => {
        console.log(`Unblock: ${data.success}`);
        // Handle success, update the UI accordingly
    }).catch(error => {
        // Log the backend error message if it exists, otherwise log a default error message
        console.log(`Failed to unblock: ${error.error ? error.error : 'An error occurred'}`);
        // Handle failure, perhaps show a message to the user
    });
}

function handleGotoProfileClick(username) {
	console.log("GotoProfile clicked for user:", username);
}

