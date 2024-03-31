const settingsPopup = document.getElementById("settings-popup");

// Open Settings Popup
document.querySelectorAll(".open-settings").forEach(element => {
    element.addEventListener('click', (event) => {
        event.stopPropagation();
        hide_popups();
        settingsPopup.classList.remove("d-none");
        settingsPopup.classList.add("d-block");
        blur_background();
    });
});

// Close Settings Popup 
document.addEventListener('click', (event) => {
    if (!settingsPopup.contains(event.target) && !event.target.matches('.open-settings') && !event.target.closest('.settings-picture')) {
        event.stopPropagation();
        settingsPopup.classList.add("d-none");
        settingsPopup.classList.remove("d-block");
        unblur_background();
    }
});

const settingsForm = document.getElementById('settings-form');
const profilePictureInput = document.getElementById('profile-picture-input');
const profilePicturePreview = document.getElementById('profile-picture-preview');

// Trigger the file input when the profile picture is clicked
document.querySelector('.settings-picture').addEventListener('click', function() {
    profilePictureInput.click();
});

// Update the profile picture preview when a new picture is selected
profilePictureInput.addEventListener('change', function() {
    if (this.files && this.files[0]) {
        var reader = new FileReader();
        reader.onload = function(e) {
            profilePicturePreview.src = e.target.result;
        };
        reader.readAsDataURL(this.files[0]);
    }
});

// Handle form submission
settingsForm.addEventListener('submit', function(e) {
    e.preventDefault();
    const formData = new FormData(settingsForm);

	const profilePictureInput = document.getElementById('profile-picture-input');
	if (profilePictureInput.files.length > 0) {
		formData.append('profile_picture', profilePictureInput.files[0]);
	}

	// const errors = validateSettingsForm(formData);
	// if (!errors.length === 0) {
	// 	errors.forEach(error => console.log(error));
	// 	return ;
	// }

	console.log('Fetching on PUT');
    fetch('/users/edit-user/', {
        method: 'PATCH',
        headers: {
            'Authorization': `Bearer ${localStorage.getItem('accessToken')}`,
        },
        body: formData,
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok.');
        }
        return response.json();
    })
    .then(data => {
		notification('Profile updated!', 'check', 'success');
        console.log('Success:', data);
        // showProfile();
		setupSettingsForm();
    })
    .catch(error => {
		notification('Error updating your profile!', 'cross', 'error');
        console.error('Error:', error);
        // TODO Handle error
    });
});

async function setupSettingsForm() {
    try {
        const userData = await getAllInfo();
        if (!userData) {
            console.log('No user data received');
            return;
        }

        // Set form field values
        document.getElementById('settings-username').value = userData.username || '';
        document.getElementById('settings-email').value = userData.email || '';
        document.getElementById('settings-first-name').value = userData.first_name || '';
        document.getElementById('settings-last-name').value = userData.last_name || '';
        document.getElementById('settings-bio').value = userData.bio || '';
        document.getElementById('settings-2fa').checked = userData.two_fa_enabled || false;

        // Set profile picture preview
        const profilePicturePreview = document.getElementById('profile-picture-preview');
        if (userData.profile_picture_url) {
            profilePicturePreview.src = userData.profile_picture_url;
        } else {
            // Set to a default image if no profile picture URL is provided
            profilePicturePreview.src = '../media/profile_pictures/default.jpg';
        }

    } catch (error) {
        console.error('Error setting up settings form:', error);
    }
}

async function getAllInfo() {
    try {
        const response = await fetch(`/users/edit-user/`, {
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


// const validateEmail = (email) => {
//     return email.match(
//       /^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/
//     );
// };

// function validateSettingsForm(form) {
//     let errors = [];
    
//     // Retrieve the username and email directly from the form fields
// 	let username = form.get('username');
//     let email = form.get('email');
    
//     // Validate username length
//     if (username.length < 4) {
//         errors.push("Username too short (must be more than 4 characters)!");
//     }
//     if (username.length > 20) {
//         errors.push("Username too long (must be less than 20 characters)!");
//     }

//     // Validate email using the regex function
//     if (!validateEmail(email)) {
//         errors.push("Incorrect email format.");
//     }
//     return errors;
// }