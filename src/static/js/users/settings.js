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

async function handleSettingsFormSubmit(e) {
	e.preventDefault();
	const formData = new FormData(settingsForm);
	const profilePictureInput = document.getElementById('profile-picture-input');
	if (profilePictureInput.files.length > 0) {
		formData.append('profile_picture', profilePictureInput.files[0]);
	}

	for (let [key, value] of formData.entries()) {
		if (value instanceof File) {
			console.log(key, value.name, value.size, value.type);
		} else {
			console.log(key, value);
		}
	}

	console.log('Fetching on PUT');
	try {
		const response = await fetch('/users/edit-user/', {
			method: 'PATCH',
			headers: {
				'Authorization': `Bearer ${localStorage.getItem('accessToken')}`,
			},
			body: formData,
		});

		if (!response.ok) {
			throw new Error('Network response was not ok.');
		}
		const data = await response.json();
		notification('Profile updated!', 'check', 'success');
		console.log('Success:', data);
		await setupSettingsForm(); // Ensure this runs after the update
	} catch (error) {
		notification('Error updating your profile!', 'cross', 'error');
		console.error('Error:', error);
	}
}

settingsForm.addEventListener('submit', handleSettingsFormSubmit);

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
