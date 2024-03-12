function createActionButton(iconSrc, title, username) {
    const button = document.createElement('button');
    button.classList.add('profile-action-button');
    button.setAttribute('data-username', username);
    button.title = title;

    const img = document.createElement('img');
    img.src = iconSrc;
    img.draggable = false;

    button.appendChild(img);

    return button;
}

function loadAndDisplayFriends() {
	if (!user)
		return ;
    getFriends().then(data => {        
        const friendshipsContainer = document.getElementById('friendships');
        
        // Clear existing friends to avoid duplication
        friendshipsContainer.innerHTML = '';
        
        // Check if there are friends
        if (data.length === 0) {
            console.log('No friendships found.');
            const noFriendsMessage = document.createElement('div');
            noFriendsMessage.textContent = 'No friends found.';
            friendshipsContainer.appendChild(noFriendsMessage);
            return;
        }
        
        // Iterate through each friend and create elements
        data.forEach(friendship => {
            const friend = friendship.friend_details;

            // Create a row for each friend
            const rowDiv = document.createElement('div');
            rowDiv.classList.add('row', 'd-flex', 'justify-content-center', 'align-items-center', 'w-75', 'mt-2');
            
            // Column for the friend's profile picture and name
            const colProfileDiv = document.createElement('div');
            colProfileDiv.classList.add('col-6', 'd-flex', 'justify-content-start', 'align-items-center');

            const img = document.createElement('img');
            img.src = friend.profile_picture_url; // Assuming 'profile_picture_url' is correct
            img.draggable = false;
            img.classList.add('friendships-profile', 'open-profile');
			img.dataset.username=friend.username;

            const span = document.createElement('span');
            span.textContent = friend.username;
            span.classList.add('friendships-profile', 'open-profile');
            span.dataset.username = friend.username;
			
            colProfileDiv.appendChild(img);
            colProfileDiv.appendChild(span);

            // Column for action buttons
            const colActionDiv = document.createElement('div');
            colActionDiv.classList.add('col-6', 'd-flex', 'flex-row', 'justify-content-end');

			// TODO hanndle better by using global vars in HTML template
            const chatButton = createActionButton('../static/icons/chat.png', 'Chat', friend.username);
            const removeFriendButton = createActionButton('../static/icons/remove-friend.png', 'Remove friend', friend.username);
            const blockButton = createActionButton('../static/icons/block.png', 'Block user', friend.username);

            colActionDiv.appendChild(chatButton);
            colActionDiv.appendChild(removeFriendButton);
            colActionDiv.appendChild(blockButton);

            // Append columns to the row
            rowDiv.appendChild(colProfileDiv);
            rowDiv.appendChild(colActionDiv);

            // Append the row to the friendships container
            friendshipsContainer.appendChild(rowDiv);
        });
    }).catch(error => {
        console.log(`Failed to getFriends: ${error.error ? error.error : 'An error occurred'}`);
    });
}

function getFriends() {
	return fetch(`/users/friends/${user.username}`, {
		method: 'GET',
		headers: {
			'Content-Type': 'application/json',
			'Authorization': `Bearer ${localStorage.getItem('accessToken')}`,
		}
	})
	.then(response => {
		if (!response.ok) {
            return response.json().then(err => Promise.reject(err));
		}
		return response.json();
	});
}


function showFriends(friendsData) {
	const friendshipsElem = document.getElementById('friendships');
	friendsData.array.forEach(element => {
		console.log(element);
	});


}

function addFriend(username) {
	return fetch(`/users/friend/${username}`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
			'Authorization': `Bearer ${localStorage.getItem('accessToken')}`,
		}
	})
	.then(response => {
		if (!response.ok) {
            return response.json().then(err => Promise.reject(err));
		}
		return response.json();
	});
}

function removeFriend(username) {
	return fetch(`/users/friend/${username}`, {
		method: 'DELETE',
		headers: {
			'Content-Type': 'application/json',
			'Authorization': `Bearer ${localStorage.getItem('accessToken')}`,
		}
	})
	.then(response => {
		if (!response.ok) {
            return response.json().then(err => Promise.reject(err));
		}
		return response.json();
	});
}
