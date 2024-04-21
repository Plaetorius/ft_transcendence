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

    const response = await fetch('/users/edit-user/', {
        method: 'PATCH',
        credentials: 'include',
        body: formData,
    });

    if (!response.ok) {
        response.json().then(err => handleErrors(err.error));
        setupSettingsForm();
        return ;
    }
    const data = await response.json();
    setupSettingsForm();
    getProfile();
    notification('Profile updated!', 'check', 'success');
}

settingsForm.addEventListener('submit', handleSettingsFormSubmit);

async function setupSettingsForm() {
    try {
        const userData = await getAllInfo();
        if (!userData) {
			notification("Error fetching user data", 'cross', 'error');
			return;
        }

        // Set form field values
        document.getElementById('settings-username').value = userData.username || '';
        document.getElementById('settings-email').value = userData.email || '';
        document.getElementById('settings-first-name').value = userData.first_name || '';
        document.getElementById('settings-last-name').value = userData.last_name || '';
        document.getElementById('settings-bio').value = userData.bio || '';

        // Set profile picture preview
        const profilePicturePreview = document.getElementById('profile-picture-preview');
        if (userData.profile_picture_url) {
            profilePicturePreview.src = userData.profile_picture_url;
        } else {
            // Set to a default image if no profile picture URL is provided
            profilePicturePreview.src = '../media/profile_pictures/default.jpg';
        }

    } catch (error) {
		notification("Error in settings form", 'cross', 'error');
	}
}

async function getAllInfo() {
    try {
        const response = await fetch(`/users/edit-user/`, {
			method: 'GET',
            credentials: 'include',
        });
        if (!response.ok) {
            throw new Error("Error fetching the data");
        }
        const userData = await response.json();
        return userData.data;
    } catch (error) {
		notification(error, 'cross', 'error');
    }
}
