document.getElementById('userSearchForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const usernameInput = document.getElementById('searchUsername');
    const username = usernameInput.value;

	usernameInput.value = '';

    addFriend(username);
	actualiseFriendsSection();

});

async function getUser(username) {
	const response = await fetch(`/users/search/${encodeURIComponent(username)}/`, {
		method: 'GET',
		headers: {
			'Content-Type': 'application/json',
		},
		credentials: 'include',
	});
	if (!response.ok) {
		notification("User not found", "cross", "error");
		throw new Error("User not found!");
	}
	const userData = await response.json();
	return userData;	
}



