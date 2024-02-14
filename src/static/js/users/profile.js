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
    // TODO check if the user is changing his username AND/OR email to an already existing one
    // TODO password change
    let profileElem = document.getElementById('editProfile');
    profileElem.innerHTML = `
        <form id="editProfileForm">
            <input type="text" id="formProfileUsername" placeholder="Username" required value="${fullUser.username}">
            <input type="text" id="formProfileEmail" placeholder="Email" required value="${fullUser.email}">
            <input type="text" id="formProfileFirstName" placeholder="First name" value="${fullUser.first_name}">
            <input type="text" id="formProfileLastName" placeholder="Last name" value="${fullUser.last_name}">
            <textarea id="formProfileBio" placeholder="Bio">${fullUser.bio}</textarea>
            <input type="file" id="formProfilePicture" value="${fullUser.profile_picture}">
        </form>
        <button id="formProfileButton" type="submit">Save...</button>
    `;
    submitListener();
}

const validateEmail = (email) => {
    return email.match(
      /^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/
    );
  };

function sanitizeSettingsForm(form) {
    // Sanitize username
    let username = form.get('username');
    let email = form.get('email');
    let errors = [];
    // Length checks may be useless as already done in the HTML
    if (username.length < 4) {
        errors.append("Username too short (must be more than 4 characters)!");
    }
    if (username.length > 20) {
        errors.append("Username too long (must be less than 20 characters)!");
    }
    // Sanitize email
    if (!email.match(/^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/)) {
        errors.append("Uncorrect email.");
    }
    return errors;
}

function submitListener() {
    document.getElementById('formProfileButton').addEventListener('click', async (e) => {
        e.preventDefault();

        let formData = new FormData();

        formData.append('username', document.getElementById('formProfileUsername').value.trim());
        formData.append('email', document.getElementById('formProfileEmail').value.trim());
        formData.append('first_name', document.getElementById('formProfileFirstName').value.trim());
        formData.append('last_name', document.getElementById('formProfileLastName').value.trim());
        formData.append('bio', document.getElementById('formProfileBio').value.trim());

        let profilePictureInput = document.getElementById('formProfilePicture');
        if (profilePictureInput.files[0]) {
            formData.append('profile_picture', profilePictureInput.files[0]);
        }

        try {
            const response = await fetch("/users/edit-user/", {
                method: 'PUT',
                headers: {
                    // NO CONTENT-TYPE FOR FORMDATA
                    'Authorization': `Bearer ${localStorage.getItem('accessToken')}`,
                },
                body: formData,
            });

            if (!response.ok) {
                throw new Error("Couldn't submit form");
            }

            const result = await response.json();
            showProfile();
        } catch (error) {
            console.log(`${error}`);
        }
    });
}

function setOnline() {
    // TODO change to wss
    console.log("Set Online called");
    const token = localStorage.getItem('accessToken');
    const statusSocket = new WebSocket(`ws://${window.location.host}/ws/user-status/?token=${token}`);

    statusSocket.onopen = (e) => {
        console.log(`You are online`);
    };

    statusSocket.onclose = (e) => {
        console.log(`You turned offline`);
    };
}

setOnline();
showProfile();