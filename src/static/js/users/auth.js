// Utils
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function handleErrors(errorData, errorElementId) {
    let errorMessageHTML = '';
    Object.keys(errorData).forEach(key => {
        errorMessageHTML += `<p>${key}: ${errorData[key].join(', ')}</p>`;
    });
    document.getElementById(errorElementId).innerHTML = errorMessageHTML;
}

// Registration
document.getElementById('registrationForm').addEventListener('submit', (e) => {
    e.preventDefault();
    const userData = {
        username: document.getElementById('registerUsername').value,
        email: document.getElementById('registerEmail').value,
        password1: document.getElementById('registerPassword1').value,
        password2: document.getElementById('registerPassword2').value,
    };

    fetch('/users/register/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        },
        body: JSON.stringify(userData),
    })
    .then(response => response.json())
    .then(data => {
        if (data.access) {
            localStorage.setItem('accessToken', data.access);
            localStorage.setItem('refreshToken', data.refresh);
            console.log('Registered and logged');
            userRegistered();
        } else {
            console.log("No data access");
            throw Error('No data access');
        }
    })
    .catch(error => handleErrors(error, 'registrationErrors'));
});

// Login
document.getElementById('loginForm').addEventListener('submit', (e) => {
    e.preventDefault();
    const loginData = {
        username: document.getElementById('loginUsername').value,
        password: document.getElementById('loginPassword').value,
    };

    fetch('/users/login/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        },
        body: JSON.stringify(loginData),
    })
    .then(response => response.json())
    .then(data => {
        if (data.access) {
            localStorage.setItem('accessToken', data.access);
            localStorage.setItem('refreshToken', data.refresh);
            console.log('Logged in successfully');
            userLoggedIn();
        } else {
            throw Error('No data access');
        }
    })
    .catch(error => handleErrors(error, 'loginErrors'));
});
