async function block(username) {
	const response = await fetch(`/users/block/${username}`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
		},
		credentials: 'include',
	});
	if (!response.ok) {
		return response.json().then(err => Promise.reject(err));
	}
	return await response.json();
}

async function unblock(username) {
	const response = await fetch(`/users/block/${username}`, {
		method: 'DELETE',
		headers: {
			'Content-Type': 'application/json',
		},
		credentials: 'include',
	});
	if (!response.ok) {
		return response.json().then(err => Promise.reject(err));
	}
	return await response.json();
}
