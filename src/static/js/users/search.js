document.getElementById('userSearchForm').addEventListener('submit', (e) => {
	e.preventDefault();
	const username = document.getElementById('searchUsername').value;
	getUser(username)
	.catch(error => {
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
	const searchedProfileDiv = document.getElementById('searchedProfile');
	searchedProfileDiv.innerHTML = `
		<h4>${userData.username}</h4>
		<p>Bio: ${userData.bio}</p>
		<img src="${userData.profile_picture}">
		<p>Elo: ${userData.elo}</p>
	`;
}