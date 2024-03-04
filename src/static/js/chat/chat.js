// TODO Use WSS
// TODO Add PONG invites system
document.querySelectorAll(".chatRoomButton").forEach(element => {
    element.addEventListener('click', (e) => {
        const username = element.getAttribute('data-username');
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
            enter_room(data.room_id)
        })
        .catch(error => {
            // TODO proper error handling
            console.log(error);
        });
    });
});

let chatSocket = null;
let blocked_list;

async function fetch_room_messages(room_id) {
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

async function fetch_blocked_users(room_id) {
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

function create_dom_message(message, sender) {
    // TODO optimize later to fetch user less times (not mandatory)
    let divElem = document.createElement('div');
    let imgElem = document.createElement('img');
    let pElem = document.createElement('p');
    divElem.classList.add('chat-message');
    divElem.appendChild(imgElem);
    divElem.appendChild(pElem);
    imgElem.src = `${sender.profile_picture}`;
    pElem.innerHTML = message;
    if (blocked_list.includes(sender.username)) {
        divElem.classList.add("d-none");        
    }
    document.getElementById('messages').appendChild(divElem);
}

async function enter_room(room_id) {
    blocked_list = await fetch_blocked_users(room_id);
    const previous_messages = await fetch_room_messages(room_id);
    if (previous_messages) {
        previous_messages.forEach(message => {
            create_dom_message(message.content, {'username': message.sender_username, 'profile_picture': message.sender_pp_url});
        });
    }
    const token = localStorage.getItem('accessToken');
    const address = `wss://${window.location.host}/ws/dm/${room_id}/?token=${token}`;
    chatSocket = new WebSocket(address);
    
    chatSocket.onopen = (e) => {
        history.pushState({ room: room_id}, "", `/chat/dm/${room_id}`);
        console.log(`Web socket opened`);
        document.getElementById('chats-section').classList.remove("d-block");
        document.getElementById('chats-section').classList.add("d-none");
        document.getElementById('chat-section').classList.remove("d-none");
        document.getElementById('chat-section').classList.add("d-block");
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
        create_dom_message(message, sender);
    };

    document.getElementById("send-message-btn").addEventListener('click', (e) => {
        e.preventDefault();
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
    });
}


