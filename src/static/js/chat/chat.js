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
            let room_id = data.room_id;
            console.log(`Room ID: ${room_id}`);
        })
        .catch(error => {
            // TODO proper error handling
            console.log(error);
        });
    });
});

// let socket = null;

// window.onload = () => {
//     const username = 'example';
//     socket = new WebSocket(`ws://${window.location.host}/ws/chat/${username}/`);

//     socket.onopen = (e) => {
//         console.log(`Web socket opened`);
//     };

//     socket.onmessage = (e) => {
//         const data = JSON.parse(e.data);
//         console.log(`Message rereceived: ${data.message}`)
//     }
//     document.getElementById("send-message-btn").addEventListener('click', (e) => {
//         e.preventDefault();
//         let messageElem = document.getElementById('message-input');
//         const message = messageElem.value;
//         const username = 'example';
//         messageElem.value = '';
//         console.log(`Message: ${message}`);

//         if (socket.readyState === WebSocket.OPEN) {
//             socket.send(JSON.stringify({
//                 message: message,
//             }));
//             console.log(`Message sent: ${message}`);
//         } else {
//             console.error(`WebSocket is not open. State: ${socket.readyState}`);
//         }
//     })
// }


