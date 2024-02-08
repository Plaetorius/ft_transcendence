// TODO Use WSS
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
            console.log(`Room ID: ${data.room_id}`);
            enter_room(data.room_id)
        })
        .catch(error => {
            // TODO proper error handling
            console.log(error);
        });
    });
});

let socket = null;

function fetch_room_messages(room_id) {
    // Fetch URL with room_id to retrieve messages
    fetch(`/chat/room-messages/${room_id}`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('accessToken')}`
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Message fetching failed');
        }
        return response.json();
    })
    .then(data => {
        // Return fetched messages
        return data.messages;
    })
    .catch(error => {
        console.log(error);
    });
}

function create_dom_message(message, sender) {
    return ;
}

function enter_room(room_id) {
	console.log(user);
    // TODO retrieve every message
    fetch_room_messages(room_id);
    const token = localStorage.getItem('accessToken');
    const address = `ws://${window.location.host}/ws/dm/${room_id}/?token=${token}`
    socket = new WebSocket(address);
    
    socket.onopen = (e) => {
        history.pushState({ room: room_id}, "", `/chat/dm/${room_id}`);
        console.log(`Web socket opened`);
        document.getElementById('chats-section').classList.remove("d-block");
        document.getElementById('chats-section').classList.add("d-none");
        document.getElementById('chat-section').classList.remove("d-none");
        document.getElementById('chat-section').classList.add("d-block");
    };

    socket.onerror = (e) => {
        console.log("Not allowed to enter that room");
        socket.close();
    }

    socket.onmessage = (e) => {
        const data = JSON.parse(e.data);
        console.log(`Message rereceived: ${data.message}`);
    };

    document.getElementById("send-message-btn").addEventListener('click', (e) => {
        e.preventDefault();
        let messageElem = document.getElementById('message-input');
        const message = messageElem.value;
        messageElem.value = '';
        // console.log(`Message: ${message}`);

        if (socket.readyState === WebSocket.OPEN) {
            socket.send(JSON.stringify({
                message: message,
            }));
            console.log(`Message sent: ${message}`);
        } else {
            console.error(`WebSocket is not open. State: ${socket.readyState}`);
        }
    })
}


