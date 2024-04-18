function showProfile() {
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
        user = userData;
		console.log(user);
		document.getElementById("profile-picture").src = user.profile_picture_url;
		loadMyProfile();
		loadAndDisplayFriends();
    })
    .catch(error => {
		notification(error, 'cross', 'error');
	});
}

function loadMyProfile() {
	// TODO call when clicking and the header button
    document.getElementById("profile-picture").src = user.profile_picture_url;
	document.getElementById("header-profile-picture").src = user.profile_picture_url;
    document.getElementById("profile-username").innerHTML = `<span class="online-status online"></span>${user.username}`;
    document.getElementById("profile-elo").innerHTML = `<span>Elo: </span>${user.elo}`;
    const dateJoined = new Date(user.date_joined);
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
        notification(data);
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

//TODO Only show relevant buttons: block if not blocked, unblock if blocked...
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
	getChatRoom(username);
	chatPopup.classList.remove("d-none");
	chatPopup.classList.add("d-block");
	blur_background();
	document.addEventListener('click', closeChatPopup);
	scrollToLastMessages();
}

function handleAddFriendClick(username) {
	addFriend(username).then(data => {
        // Handle success, update the UI accordingly
		notification(`Friend added: ${data.success}`, "check", "success");
		actualiseFriendsSection();
    }).catch(error => {
        // Log the backend error message if it exists, otherwise log a default error message
        // Handle failure, perhaps show a message to the user
        notification(`Failed to add friend: ${error.error ? error.error : 'An error occurred'}`, "cross", "error");
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
        notification(`Failed to removed friend: ${error.error ? error.error : 'An error occurred'}`, "cross", "error");
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
        notificationSocket(`Failed to unblock: ${error.error ? error.error : 'An error occurred'}`, "cross", "error");
    });
}

async function handleGotoProfileClick(username) {
	// TODO maybe use URL query params to use the history
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
	navigateToSection("user");
}