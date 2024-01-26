document.getElementById('registrationForm').addEventListener('submit', (e) => {
    e.preventDefault();
    const userData = {
        username: document.getElementById('registerUsername').value,
        email: document.getElementById('registerEmail').value,
        password1: document.getElementById('registerPassword1').value,
        password2: document.getElementById('registerPassword2').value,
    };
    
    const csrftoken = getCookie('csrftoken');
    fetch('/users/register/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
        },
        body: JSON.stringify(userData),
    })
    .then(async response => {
        if (!response.ok) {
            const err = await response.json();
            throw err;
        }
        return response.json();
    })
    .then(data => {
        if (data.id) {
            userRegistered();
            console.log('Registered');
            // Handle successful registration
        } else {
            // Handle validation errors or other issues
        }
    })
    .catch(error => {
        // console.log(`${JSON.stringify(error)}`);
        let errorMessageHTML = '';
        for (const key in error) {
            if (error.hasOwnProperty(key)) {
                errorMessageHTML += `<p>${key}: ${error[key].join(', ')}</p>`;
            }
        }
        document.getElementById('registrationErrors').innerHTML = errorMessageHTML;
    });    
});

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === name + '=') {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function userRegistered() {

}