function getFriends() {
	fetch('/users/friends/', {
		method: 'GET',
		headers: {
			'Content-Type': 'application/json',
			'Authorization': `Bearer ${localStorage.getItem('accessToken')}`
		}
	})
	.then(response => {
		if (!response.ok) {
			throw new Error("User not found!");
		}
		return response.json();
	})
	.then(friendsData => {
		showFriends(friendsData);
	})
	.catch(error => {
		document.getElementById('friendsError').innerHTML = error.message;
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
