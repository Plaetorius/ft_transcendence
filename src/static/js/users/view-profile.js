document.addEventListener('DOMContentLoaded', function() {
    const userId = 1;
    fetch(`users/profile/${userId}/`)
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok ' + response.statusText);
        }
        return response.json();
    })
    .then(userData => {
        displayUserProfile(userData);
    })
    .catch(error => {
        console.error('There has been a problem with your fetch operation:', error);
    });
});

function displayUserProfile(userData) {
    const userProfileDiv = document.getElementById('userProfile');
    userProfileDiv.innerHTML = `
        <h4>${userData.username}</h4>
        <img src="${userData.profile_picture_url}" alt="${userData}" draggable="false">
        <p>${userData.bio}</p>    
        `;
}