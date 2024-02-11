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

document.getElementById('editProfileButton').addEventListener('click', (e) => {
    document.getElementById('editProfile').classList.remove('d-none');
    changeProfile();
});

async function getAllInfo() {
    try {
        const response = await fetch(`/users/edit-user`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('accessToken')}`,
            }
        });
        if (!response.ok) {
            throw new Error("Couldn't fetch all data");
        }
        const userData = await response.json();
        return userData.data;
    } catch (error) {
        console.log(`Error: ${error}`);
    }
}

async function changeProfile() {
    let fullUser = await getAllInfo();
    console.log(`FullUser: ${fullUser.profile_picture} ${fullUser.profile_picture_url}`);
    // TODO check if the user is changing his username AND/OR email to an already existing one
    // TODO password change
    let profileElem = document.getElementById('editProfile');
    profileElem.innerHTML = `
        <form id="editProfileForm">
            <input type="text" id="editProfileUsername" placeholder="Username" required value="${fullUser.username}">
            <input type="text" id="editProfileEmail" placeholder="Email" required value="${fullUser.email}">
            <input type="text" id="editProfileFirstName" placeholder="First name" value="${fullUser.first_name}">
            <input type="text" id="editProfileLastName" placeholder="Last name" value="${fullUser.last_name}">
            <textarea id="editProfileBio" placeholder="Bio">${fullUser.bio}</textarea>
            <input type="file" id="editProfilePicture" value="${fullUser.profile_picture}">
            <label for=editProfilePicture" 
            <button type="submit">Save...</button>
        </form>
    `;
}

showProfile();