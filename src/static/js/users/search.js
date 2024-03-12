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

async function getUser(username) {
	const response = await fetch(`/users/search/${encodeURIComponent(username)}/`, {
		method: 'GET',
		headers: {
			'Content-Type': 'application/json',
			'Authorization': `Bearer ${localStorage.getItem('accessToken')}`
		}
	});
	if (!response.ok) {
		// TODO better handling
		throw new Error('User not found');
	}
	const userData = await response.json();
	return userData;	
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
