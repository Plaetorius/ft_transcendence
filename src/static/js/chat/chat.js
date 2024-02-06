// TODO Use WSS
document.querySelectorAll(".chatRoomButton").forEach(element => {
    element.addEventListener('click', (e) => {
        const username = element.getAttribute('data-username');
        const cookie = getCookie('csrftoken');
        changeSection("chat");
        fetch(`chat/get-id/${username}`, {
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

function enter_room(room_id) {
    socket = new WebSocket(`ws://${window.location.host}/ws/dm/${room_id}/`);
    window.location.pathname = `/chat/dm/${room_id}/`;
    
    socket.onopen = (e) => {
        console.log(`Web socket opened`);
    };

    socket.onmessage = (e) => {
        const data = JSON.parse(e.data);
        console.log(`Message rereceived: ${data.message}`);
    };

    document.getElementById("send-message-btn").addEventListener('click', (e) => {
        e.preventDefault();
        let messageElem = document.getElementById('message-input');
        const message = messageElem.value;
        messageElem.value = '';
        console.log(`Message: ${message}`);

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


