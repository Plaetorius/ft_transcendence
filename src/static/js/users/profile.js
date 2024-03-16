let user = undefined;

function showProfile() {
    // document.getElementById('profileErrors').innerHTML = '';
    // let profileElement = document.getElementById('displayProfile');
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
		let imgElem = document.getElementById('header-profile-picture');
		imgElem.src = `..${user.profile_picture_url}`;
    })
    .catch(error => {
		console.log(error);
	});
}

// document.getElementById('editProfileButton').addEventListener('click', (e) => {
//     document.getElementById('editProfile').classList.remove('d-none');
//     changeProfile();
// });

// async function getAllInfo() {
//     try {
//         const response = await fetch(`/users/edit-user`, {
//             method: 'GET',
//             headers: {
//                 'Content-Type': 'application/json',
//                 'Authorization': `Bearer ${localStorage.getItem('accessToken')}`,
//             }
//         });
//         if (!response.ok) {
//             throw new Error("Couldn't fetch all data");
//         }
//         const userData = await response.json();
//         return userData.data;
//     } catch (error) {
//         console.log(`Error: ${error}`);
//     }
// }

// async function changeProfile() {
//     let fullUser = await getAllInfo();
//     // TODO password change
//     let profileElem = document.getElementById('editProfile');
//     profileElem.innerHTML = `
//         <form id="editProfileForm">
//             <input type="text" id="formProfileUsername" placeholder="Username" required value="${fullUser.username}">
//             <input type="text" id="formProfileEmail" placeholder="Email" required value="${fullUser.email}">
//             <input type="text" id="formProfileFirstName" placeholder="First name" value="${fullUser.first_name}">
//             <input type="text" id="formProfileLastName" placeholder="Last name" value="${fullUser.last_name}">
//             <textarea id="formProfileBio" placeholder="Bio">${fullUser.bio}</textarea>
//             <input type="file" id="formProfilePicture" value="${fullUser.profile_picture}">
//         </form>
//         <button id="formProfileButton" type="submit">Save...</button>
//     `;
//     submitListener();
// }

// const validateEmail = (email) => {
//     return email.match(
//       /^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/
//     );
//   };

// function sanitizeSettingsForm(form) {
//     // Sanitize username
//     let username = form.get('username');
//     let email = form.get('email');
//     let errors = [];
//     // Length checks may be useless as already done in the HTML
//     if (username.length < 4) {
//         errors.append("Username too short (must be more than 4 characters)!");
//     }
//     if (username.length > 20) {
//         errors.append("Username too long (must be less than 20 characters)!");
//     }
//     // Sanitize email
//     if (!email.match(/^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/)) {
//         errors.append("Incorrect email.");
//     }
//     return errors;
// }

// function submitListener() {
//     document.getElementById('formProfileButton').addEventListener('click', async (e) => {
//         e.preventDefault();

//         let formData = new FormData();

//         formData.append('username', document.getElementById('formProfileUsername').value.trim());
//         formData.append('email', document.getElementById('formProfileEmail').value.trim());
//         formData.append('first_name', document.getElementById('formProfileFirstName').value.trim());
//         formData.append('last_name', document.getElementById('formProfileLastName').value.trim());
//         formData.append('bio', document.getElementById('formProfileBio').value.trim());

//         let profilePictureInput = document.getElementById('formProfilePicture');
//         if (profilePictureInput.files[0]) {
//             formData.append('profile_picture', profilePictureInput.files[0]);
//         }

//         try {
//             const response = await fetch("/users/edit-user/", {
//                 method: 'PUT',
//                 headers: {
//                     // NO CONTENT-TYPE FOR FORMDATA
//                     'Authorization': `Bearer ${localStorage.getItem('accessToken')}`,
//                 },
//                 body: formData,
//             });

//             if (!response.ok) {
//                 let error_message = '';
//                 const parsed = await response.json();
//                 // Horrendous but necessary (Django has a weird way of sending error messages)
//                 // Django sends a map :
//                 //      [keys: str; field name where error happened, 
//                 //      values: array; contain strings of error messages, 1 per error]
//                 if (parsed.error && typeof parsed.error === 'object') {
//                     // Iterate through the map
//                     Object.entries(parsed.error).forEach(([key, value]) => {
//                         // Iterate through the array of errors related to the field
//                         if (Array.isArray(value)) {
//                             value.forEach(error => {
//                                 error_message += `${key}: ${error}\n`;
//                             });
//                         }
//                         // Shouldn't happen (not an array)
//                         else {
//                             error_message += `${key}: ${value}\n`;
//                         }
//                     });
//                 }
//                 // Shouldn't happen (not a map)
//                 else {
//                     error_message += `Error: ${parsed.error} || 'An error occurred'`;
//                 }
            
//                 throw new Error(error_message);
//             }

//             const result = await response.json();
//             showProfile();
//         } catch (error) {
//             console.log(`${error}`);
//         }
//     });
// }

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

setOnline();
showProfile();

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
			const user = await getUser(targetElement.dataset.username);
			console.log(`openProfileHandler`, user);
			updateProfilePopup(user);
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
	if (!settingsPopup.contains(event.target) && !event.target.matches('.open-settings')) {
		event.stopPropagation();
		settingsPopup.classList.add("d-none");
		settingsPopup.classList.remove("d-block");
		unblur_background();
	}
});


document.querySelector('.settings-picture').addEventListener('click', function() {
	document.getElementById('profile-picture-input').click();
});


// Handle settings form
const form = document.querySelector('#settings-popup form');
    
form.addEventListener('submit', function(event) {
	event.preventDefault();
	blur_background();


	const formData = new FormData(form);
	const formJSON = {};
	for (const [key, value] of formData.entries()) {
		formJSON[key] = value;
	}
	// Debug code
	const fileInput = document.getElementById('profile-picture-input');
	if (fileInput.files[0]) {
		const reader = new FileReader();
		reader.onloadend = function() {
			const base64String = reader.result;
			console.log('Base64 String:', base64String);
			console.log('Form JSON:', formJSON);
		};
		reader.readAsDataURL(fileInput.files[0]);
	} else {
		console.log('Form JSON:', formJSON);
	}
});
