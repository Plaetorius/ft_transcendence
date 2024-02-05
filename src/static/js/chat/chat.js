document.getElementsByClassName("chatRoomButton").array.forEach(element => {
    element.addEventListener('click', (e) => {
        const username = element.getAttribute('data-username');
        console.log(`Clicked ${username}`);
    });
});