// TODO Add PONG invites system
function getChatRoom(username) {
	console.log("Clicked");
	const cookie = getCookie('csrftoken');
	fetch(`chat/room-id/${username}`, {
		method: 'GET',
		headers: {
			'Content-Type': 'application/json',
			'Authorization': `Bearer ${localStorage.getItem('accessToken')}`
		}
	})
	.then(response => {
		if (!response.ok) {
			throw new Error('Username not found');
		}
		return response.json();
	})
	.then(data => {
		enterRoom(data.room_id, username);

	})
	.catch(error => {
		// TODO proper error handling
		console.log(error);
	});
}

let chatSocket = null;
let blocked_list;

async function fetchRoomMessages(room_id) {
    // Fetch URL with room_id to retrieve messages
    try {
        const response = await fetch(`/chat/room-messages/${room_id}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('accessToken')}`,
            }
        });
        if (!response.ok) {
            throw new Error('Message fetching failed');
        }
        const data = await response.json();
        // Return fetched messages
        return data.messages;
    } catch (error) {
        console.log(error);
        return undefined;
    }
}

async function fetchBlockedUsers(room_id) {
    try {
        const response = await fetch(`/users/list-blocked/`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('accessToken')}`,
            }
        });
        if (!response.ok) {
            throw new Error("Blocked list fetching failed");
        }
        const data = await response.json();
        return data.list;
    } catch (error) {
        return undefined;
    }
}

function createDomMessage(message, sender) {
    let messageDiv = document.createElement('div');
    let profileDiv = document.createElement('div');
    let imgElem = document.createElement('img');
    let messageContentDiv = document.createElement('div');
    let pElem = document.createElement('p');
    // let timeSpan = document.createElement('span');

    // Applying classes based on whether the message is sent or received
    messageDiv.classList.add('message', 'd-flex');
    if (user.username === sender.username) {
        // Message sent by the current user
        messageDiv.classList.add('flex-row-reverse');
    }

    imgElem.src = `${sender.profile_picture}`;
    imgElem.className = 'open-profile';
    imgElem.setAttribute('data-username', sender.username);
    imgElem.draggable = false;
    
    pElem.innerHTML = message;
    // TODO use real message time
    // timeSpan.textContent = '16:20';

    profileDiv.appendChild(imgElem);

    messageContentDiv.className = 'message-content';
    messageContentDiv.appendChild(pElem);
    // messageContentDiv.appendChild(timeSpan);

    messageDiv.appendChild(profileDiv);
    messageDiv.appendChild(messageContentDiv);

    if (blocked_list && blocked_list.includes(sender.username)) {
		messageDiv.classList.remove("d-flex");
        messageDiv.classList.add("d-none");
    }

    document.getElementById('messages').appendChild(messageDiv);

    // After appending the message, scroll to the last message
    scrollToLastMessages();
}

async function updateChatPopup(username) {
	const user = await getUser(username);
	let titleElem = chatPopup.querySelector("h5");
    
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
}

async function enterRoom(room_id, username) {
	console.log("Enter room entered");
    blocked_list = await fetchBlockedUsers(room_id);
    const previous_messages = await fetchRoomMessages(room_id);
    if (previous_messages) {
        previous_messages.forEach(message => {
            createDomMessage(message.content, {'username': message.sender_username, 'profile_picture': message.sender_pp_url});
        });
    }
    const token = localStorage.getItem('accessToken');
    const address = `wss://${window.location.host}/ws/dm/${room_id}/?token=${token}`;
    chatSocket = new WebSocket(address);
    
    chatSocket.onopen = (e) => {
		updateChatPopup(username);
        console.log(`Web socket opened`);
    };

    chatSocket.onerror = (e) => {
        // TODO display propperly
        console.log("Not allowed to enter that room");
        chatSocket.close();
    }

    chatSocket.onmessage = (e) => {
        const data = JSON.parse(e.data);
        const message = data.message;
        const sender = data.sender;
        createDomMessage(message, sender);
    };

    document.getElementById("send-message-btn").addEventListener('click', handleSendMessage);
	document.getElementById("message-input").addEventListener('keydown', handleSendMessage);
    document.getElementById('message-input').focus();
}

function handleSendMessage(event) {
	if (event.type === 'keydown' && event.key !== 'Enter') {
		return ;
	}

	event.preventDefault();
	let messageElem = document.getElementById('message-input');
	const message = messageElem.value.trim();
	if (message.length == 0) {
		console.log("Message can't be empty");
	} 
	else if (message.length > 1024)
		console.log('Message too long');
	else {
		messageElem.value = '';
		if (chatSocket.readyState === WebSocket.OPEN) {
			chatSocket.send(JSON.stringify({
				message: message,
			}));
		} else {
			console.error(`WebSocket is not open. State: ${chatSocket.readyState}`);
		}
	}
}

const chatPopup = document.getElementById("chat-popup");

// // Open for Chats
// document.querySelectorAll(".open-chat").forEach(element => {
// 	element.addEventListener('click', (event) => {
// 		event.stopPropagation();
// 		hide_popups();
// 		chatPopup.classList.remove("d-none");
// 		chatPopup.classList.add("d-block");
// 		blur_background();
// 		scrollToLastMessages();
// 	});
// });

// // Close for Chats
function closeChatPopup(event) {
	if (!chatPopup.contains(event.target) && !event.target.matches('.open-chat')) {
		event.stopPropagation();
		chatPopup.classList.add("d-none");
		chatPopup.classList.remove("d-block");
		unblur_background();
		document.removeEventListener('click', closeChatPopup);
		document.getElementById("send-message-btn").removeEventListener('click', handleSendMessage);
		document.getElementById("message-input").removeEventListener('keydown', handleSendMessage);
		document.getElementById('messages').innerHTML = '';
		clearChatHeader();
		chatSocket.close();
	}
}

function scrollToLastMessages() {
    const chatMessages = document.querySelector('.chat-messages');
    if (chatMessages) {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
}

function clearChatHeader() {
    const h5Tag = document.querySelector("#chat-popup h5");
    const statusSpan = h5Tag.querySelector(".online-status");

    // Remove the username
    h5Tag.childNodes.forEach(node => {
        if (node.nodeType === Node.TEXT_NODE) {
            node.nodeValue = '';
        }
    });

    // Remove "online" or "offline" classes
    if (statusSpan.classList.contains("online")) {
        statusSpan.classList.remove("online");
    } else if (statusSpan.classList.contains("offline")) {
        statusSpan.classList.remove("offline");
    }
}
