document.getElementById('userSearchForm').addEventListener('submit', (e) => {
	e.preventDefault();
	const username = document.getElementById('searchUsername').value;
	getUser(username)
	.catch(error => {
		document.getElementById('searchedProfile').innerHTML = '';
		document.getElementById('friendsError').innerHTML = error.message;
	});
});

function getUser(username) {
	return fetch(`/users/search/${encodeURIComponent(username)}/`, {
		method: 'GET',
		headers: {
			'Content-Type': 'application/json',
			'Authorization': `Bearer ${localStorage.getItem('accessToken')}`
		}
	})
	.then(response => {
		if (!response.ok) {
			throw new Error('User not found');
		}
		return response.json();
	})
	.then(userData => {
		showUserProfile(userData);
	});	
}

function showUserProfile(userData) {
	document.getElementById('friendsError').innerHTML = '';
	const searchedProfileDiv = document.getElementById('searchedProfile');
	searchedProfileDiv.innerHTML = `
		<h4>${userData.username}</h4>
		<p>Bio: ${userData.bio}</p>
		<img src="${userData.profile_picture}">
		<p>Elo: ${userData.elo}</p>
		<button id="searchAddFriendButton" data-username="${userData.username}"> Add Friend </button>
		<button id="searchRemoveFriendButton" data-username="${userData.username}"> Remove Friend </button>
		`;
}

document.getElementById('searchedProfile').addEventListener('click', (e) => {
	if (e.target && e.target.id === 'searchAddFriendButton') {
		const username = e.target.getAttribute('data-username');
		addFriend(username);
	}
	if (e.target && e.target.id === 'searchRemoveFriendButton') {
		const username = e.target.getAttribute('data-username');
		removeFriend(username);
	}
})

function addFriend(username) {
	fetch(`/users/add-friend/${username}`, {
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
	})
	.then(data => {
		// TODO handle success
		console.log(`Success: ${data.success}`);
	})
	.catch(error => {
		// TODO handle error
		console.log(`Error: ${error.error ? error.error : error}`);
	});
}

function removeFriend(username) {
	fetch(`/users/remove-friend/${username}`, {
		method: 'DELETE',
		headers: {
			'Content-Type': 'application/json',
			'Authorization': `Bearer ${localStorage.getItem('accessToken')}`,
		}
	})
	.then(response => {
		if (!response.ok) {
			// Parse the JSON error message and throw it as an error
            return response.json().then(err => Promise.reject(err));
		}
		return response.json();
	})
	.then(data => {
		// TODO handle success
		console.log(`Success: ${data.success}`);
	})
	.catch(error => {
		// TODO handle error
		console.log(`Error: ${error.error ? error.error : error}`);
	});
}
