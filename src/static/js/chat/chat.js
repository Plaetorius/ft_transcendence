document.querySelectorAll(".chatRoomButton").forEach(element => {
    element.addEventListener('click', (e) => {
        const username = element.getAttribute('data-username');
        const cookie = getCookie('csrftoken');
        console.log(`Cookie: ${cookie}`);
        changeSection("chat");
        // TODO Use WSS
    });
});

let socket = null;

window.onload = () => {
    const username = 'example';
    socket = new WebSocket(`ws://${window.location.host}/ws/chat/${username}/`);

    socket.onopen = (e) => {
        console.log(`Web scoket opened`);
    };

    document.getElementById("send-message-btn").addEventListener('click', (e) => {
        e.preventDefault();
        let messageElem = document.getElementById('message-input');
        const message = messageElem.value;
        const username = 'example';
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


