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