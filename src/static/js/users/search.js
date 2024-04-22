document.getElementById('userSearchForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const usernameInput = document.getElementById('searchUsername');
    const username = usernameInput.value.trim();
	usernameInput.value = '';

	if (username.length === 0) {
		notification("Username can't be empty!", "cross", "error");
		return ;
	}

	addFriend(username).then(data => {
		notification(`Friend added: ${data.success}`, "check", "success");
		actualiseFriendsSection();
    }).catch(error => {
        notification(`Failed to add friend: ${error.error ? error.error : 'An error occurred'}`, "cross", "error");
    });
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



