document.getElementById('userSearchForm').addEventListener('submit', (e) => {
	console.log('caught');
	e.preventDefault();
	const username = document.getElementById('searchUsername').value;
	fetch(`/users/search/${encodeURIComponent(username)}/`)
	.then(response => {
		if (!response.ok) {
			throw new Error('User not found');
		}
		return response.json();
	})
	.then(userData => {
		displayUserProfile(userData);
	})
	.catch(error => {
		document.getElementById('searchedProfile').innerHTML = error.message;
	});
});

function displayUserProfile(userData) {
	const searchedProfileDiv = document.getElementById('searchedProfile');
	searchedProfileDiv.innerHTML = `
		<h4>${userData.username}</h4>
	`;
}