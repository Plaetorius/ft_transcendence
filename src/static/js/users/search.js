// TODO create functions for better error handling for friend add, friend remove,
// block user, unblock user

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
		// TODO Just do it better
		console.log(userData);
	});	
}


// TODO not comptaible anymore
document.getElementById('searchedProfile').addEventListener('click', (e) => {
	if (e.target && e.target.id === 'searchAddFriendButton') {
		const username = e.target.getAttribute('data-username');
		addFriend(username);
	}
	if (e.target && e.target.id === 'searchRemoveFriendButton') {
		const username = e.target.getAttribute('data-username');
		removeFriend(username);
	}
	if (e.target && e.target.id === 'searchBlockUserButton') {
		const username = e.target.getAttribute('data-username');
		blockUser(username);
	}
	if (e.target && e.target.id === 'searchUnblockUserButton') {
		const username = e.target.getAttribute('data-username');
		unblockUser(username);
	}
});

function addFriend(username) {
	fetch(`/users/friend/${username}`, {
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
	fetch(`/users/friend/${username}`, {
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

function blockUser(username) {
	fetch(`/users/block/${username}`, {
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

function unblockUser(username) {
	fetch(`/users/block/${username}`, {
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