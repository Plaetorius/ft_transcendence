async function getPodium() {
    try {
        const response = await fetch(`/users/podium/`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('accessToken')}`,
            }
        });

        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.message);
        }

        const users = await response.json();
        createPodium(users);
        createRankingList(users);
    } catch (error) {
        notificationr(error, 'cross', 'error');
    }
}

function createPodium(users) {
    // Assuming the first three users are the top players for the podium
    const podiumPlaces = ['first-place', 'second-place', 'third-place'];

    podiumPlaces.forEach((place, index) => {
        if (users[index]) { // Check if the user exists
            const container = document.getElementById(place);
            container.innerHTML = ''; // Clear existing content
            const img = document.createElement('img');
            img.src = users[index].profile_picture_url ? users[index].profile_picture_url : '../media/profile_pictures/default.jpg';
            img.draggable = false;
            img.className = 'podium-profile open-profile';
            img.setAttribute('data-username', users[index].username);
            container.appendChild(img);
        }
    });
}

function createRankingList(users) {
    const listContainer = document.getElementById('podium-list');
    listContainer.innerHTML = ''; // Clear existing content

    // Start from the 4th user since the first three are on the podium
    users.slice(3).forEach((user, index) => {
        const row = document.createElement('div');
        row.className = 'row';

        const col = document.createElement('div');
        col.className = 'col d-flex align-items-center';

        const position = document.createElement('span');
        position.textContent = `${index + 4}.`;
        
        const img = document.createElement('img');
        img.src = user.profile_picture_url;
        img.draggable = false;
        img.className = 'podium-profile open-profile';
        img.setAttribute('data-username', user.username);
        
        const usernameSpan = document.createElement('span');
        usernameSpan.className = 'podium-profile open-profile d-flex align-items-center';
        usernameSpan.setAttribute('data-username', user.username);
        usernameSpan.textContent = user.username;

        col.appendChild(position);
        col.appendChild(img);
        col.appendChild(usernameSpan);
        row.appendChild(col);

        listContainer.appendChild(row);
    });
}
