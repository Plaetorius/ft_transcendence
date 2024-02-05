document.querySelectorAll(".chatRoomButton").forEach(element => {
    element.addEventListener('click', (e) => {
        const username = element.getAttribute('data-username');
        const cookie = getCookie('csrftoken');
        fetch('/chat/chatrooms/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': cookie,
            },
            body: JSON.stringify({
                members: [username],
                is_direct_message: true,
            })
        })
        .then(response => response.json())
        .then(data => {
            console.log(data);
            const newLocation = `${window.location.origin}/chat/${username}`;
            window.location.href = newLocation;
        })
        .catch((error) => {
            console.log(`Error: ${error}`);
        })
    });
});