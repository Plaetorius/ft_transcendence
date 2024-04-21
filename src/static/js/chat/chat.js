// TODO Add PONG invites system

function getChatRoom(username) {
	const cookie = getCookie('csrftoken');
	fetch(`chat/room-id/${username}`, {
		method: 'GET',
		headers: {
			'Content-Type': 'application/json',
		},
		credentials: 'include',
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
		notification(error, 'cross', 'error');
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
			},
			credentials: 'include',
        });
        if (!response.ok) {
            throw new Error('Message fetching failed');
        }
        const data = await response.json();
        // Return fetched messages
        return data.messages;
    } catch (error) {
        notification(error, 'cross', 'error');
        return undefined;
    }
}

async function fetchBlockedUsers() {
    try {
        const response = await fetch(`/users/list-blocked/`, {
            method: 'GET',
            headers: {
				'Content-Type': 'application/json',
			},
			credentials: 'include',
        });
        if (!response.ok) {
            throw new Error("Blocked list fetching failed");
        }
        const data = await response.json();
        return data.list;
    } catch (error) {
		notification(error, 'cross', 'error');
        return undefined;
    }
}

document.getElementById('clash-button').addEventListener('click', createClash);

async function createClash() {
    const clash_uid = await fetchPongCreation(); 
    if (chatSocket.readyState === WebSocket.OPEN) {
        chatSocket.send(JSON.stringify({
            message: `/clash ${clash_uid}`,
        }));
    }
}


function createDomInvitation(sender, uid) {
    let invitationDiv = document.createElement('div');
    let profileDiv = document.createElement('div');
    let imgElem = document.createElement('img');
    let invitationContentDiv = document.createElement('div');
    let pElem = document.createElement('p');
    let acceptBtn = document.createElement('button');

    invitationDiv.classList.add('invitation', 'd-flex');
    imgElem.src = `${sender.profile_picture}`;
    imgElem.className = 'open-profile';
    imgElem.setAttribute('data-username', sender.username);
    imgElem.draggable = false;

    pElem.innerHTML = `${sender.username} created a game!`;

    acceptBtn.innerHTML = 'Clash!';
    acceptBtn.classList.add('accept-invitation');
    acceptBtn.setAttribute('data-username', sender.username);
    acceptBtn.setAttribute('data-uid', uid);



    profileDiv.appendChild(imgElem);

    invitationContentDiv.className = 'invitation-content';
    invitationContentDiv.appendChild(pElem);
    invitationContentDiv.appendChild(acceptBtn);

    invitationDiv.appendChild(profileDiv);
    invitationDiv.appendChild(invitationContentDiv);

    document.getElementById('messages').appendChild(invitationDiv);

    // After appending the message, scroll to the last message
    scrollToLastMessages();
}

function createDomMessage(message, sender) {
    let messageDiv = document.createElement('div');
    let profileDiv = document.createElement('div');
    let imgElem = document.createElement('img');
    let messageContentDiv = document.createElement('div');
    let pElem = document.createElement('p');

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

    profileDiv.appendChild(imgElem);

    messageContentDiv.className = 'message-content';
    messageContentDiv.appendChild(pElem);

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
	const chatUser = await getUser(username);
	let titleElem = chatPopup.querySelector("h5");
    
    // Clear existing online-status span if any
    let existingStatus = titleElem.querySelector('.online-status');
    if (existingStatus) {
        existingStatus.remove();
    }
    
    // Create and add new online status span
    let onlineElem = document.createElement("span");
    onlineElem.classList.add("online-status", chatUser.is_online ? "online" : "offline");
    titleElem.innerText = chatUser.username;
    titleElem.insertBefore(onlineElem, titleElem.firstChild);
}

async function enterRoom(room_id, username) {
    blocked_list = await fetchBlockedUsers(room_id);
    const previous_messages = await fetchRoomMessages(room_id);
    if (previous_messages) {
        previous_messages.forEach(message => {
            createDomMessage(message.content, {'username': message.sender_username, 'profile_picture': message.sender_pp_url});
        });
    }
    const address = `wss://${window.location.host}/ws/dm/${room_id}/`;
    chatSocket = new WebSocket(address);
    
    chatSocket.onopen = (e) => {
		updateChatPopup(username);
    };

    chatSocket.onerror = (e) => {
		notification("You are not allowed in this room!", 'cross', 'error');
		removeChatDisplayAndListeners();
        chatSocket.close();
    }

    chatSocket.onmessage = (e) => {
        const data = JSON.parse(e.data);
        const message = data.message;
        const sender = data.sender;
        if (message.startsWith('/clash')) {
            const uid = message.split(' ')[1];
            createDomInvitation(sender, uid);
            return ;
        }
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
		notification("Message can't be empty", 'cross', 'error');
	} 
	else if (message.length > 1024)
		notification('Message too long', 'cross', 'error');
	else {
		messageElem.value = '';
		if (chatSocket.readyState === WebSocket.OPEN) {
			chatSocket.send(JSON.stringify({
				message: message,
			}));
		} else {
			notification("Problem connecting to the server. Please retry", 'cross', 'error');
		}
	}
}

const chatPopup = document.getElementById("chat-popup");

// Close for Chats
function closeChatPopup(event) {
	if (!chatPopup.contains(event.target) && !event.target.matches('.open-chat')) {
		event.stopPropagation();
		removeChatDisplayAndListeners();
		chatSocket.close();
	}
}

function removeChatDisplayAndListeners() {
	chatPopup.classList.add("d-none");
	chatPopup.classList.remove("d-block");
	unblur_background();
	document.removeEventListener('click', closeChatPopup);
	document.getElementById("send-message-btn").removeEventListener('click', handleSendMessage);
	document.getElementById("message-input").removeEventListener('keydown', handleSendMessage);
	document.getElementById('messages').innerHTML = '';
	clearChatHeader();
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
