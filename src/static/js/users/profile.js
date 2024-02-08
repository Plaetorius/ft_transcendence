let user = undefined;

function showProfile() {

    document.getElementById('profileErrors').innerHTML = '';
	let profileElement = document.getElementById('displayProfile');
    fetch('/users/profile/', {
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
        // TODO hide error in the console
        return response.json();
    })
    .then(userData => {
		user = userData;
		profileElement.innerHTML = `
            <h4>${userData.username}</h4>
            <p>Bio: ${userData.bio}</p>
            <img src="${userData.profile_picture}">
            <p>Elo: ${userData.elo}</p>
       `;

	   //TODO remove
	   document.getElementById('connected-username').innerHTML = user.username;
    })
    .catch(error => {
        document.getElementById('profileErrors').innerHTML = error.message;
    });
}

showProfile();