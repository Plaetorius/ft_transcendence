document.getElementById('header-friends').addEventListener('click', () => {
	getFriends().then(data => {
        // Assuming 'data' is the array of friendships as shown in your log
        console.log(`Number of friends: ${data.length}`); // Correctly logs the number of friends
        data.forEach(friendship => {
            console.log(`Friend's username: ${friendship.friend_details.username}`);
            // Here, you can update the UI with each friend's details
        });
        // If you need to handle the case when there are no friendships, you can do it here
        if (data.length === 0) {
            console.log('No friendships found.');
        }
    }).catch(error => {
        // Log the backend error message if it exists, otherwise log a default error message
        console.log(`Failed to getFriends: ${error.error ? error.error : 'An error occurred'}`);
        // Handle failure, perhaps show a message to the user
    });
});

// function getFriends() {
// 	fetch('/users/friends/', {
// 		method: 'GET',
// 		headers: {
// 			'Content-Type': 'application/json',
// 			'Authorization': `Bearer ${localStorage.getItem('accessToken')}`
// 		}
// 	})
// 	.then(response => {
// 		if (!response.ok) {
// 			return response.json();
// 		}
// 		return response.json();
// 	})
// 	.then(friendsData => {
// 		showFriends(friendsData);
// 	})
// 	.catch(error => {
// 		console.log(error.message);
// 		// document.getElementById('friendsError').innerHTML = error.message;
// 	});
// }

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
