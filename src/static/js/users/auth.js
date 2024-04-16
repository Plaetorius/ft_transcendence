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

function handleErrors(data) {
    let errorMessage = 'Error:\n';

	for (const [key, value] of Object.entries(data)) {
		errorMessage += value[0] + " ";
	}
	notification(errorMessage, 'cross', 'error');
}

// Registration
document.getElementById('registerForm').addEventListener('submit', (e) => {
    e.preventDefault();
    const registerData = {
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
        body: JSON.stringify(registerData),
		credentials: 'include',
    })
	.then(response => {
        if (response.ok) {
			authenticated();
        } else {
            return response.json();
        }
    })
	.then(data => {
		if (data) {
			handleErrors(data);
		}
	});
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
		credentials: 'include',
    })
	.then(response => {
        if (response.ok) {
			authenticated();
        } else {
            return response.json();
        }
    })
	.then(data => {
		if (data) {
			handleErrors(data);
		}
	});
});

// Hide pages if user not authenticated
//TODO uncomment me
if (!accessToken) {
	header.classList.add('d-none');
	navigateToSection('register');
}

document.getElementById('already-account').addEventListener('click', () => {
	navigateToSection('login');
});

document.getElementById('no-account').addEventListener('click', () => {
	navigateToSection('register');
});

function authenticated() {
	header.classList.remove("d-none");
	setOnline();
	showProfile();
	navigateToSection('home');
	notification('Successfully authenticated!', 'check', 'success');
}

document.getElementById("oauth-button").addEventListener("click", oauth_register);

function oauth_register() {
	const authUrl = "https://api.intra.42.fr/oauth/authorize?client_id=u-s4t2ud-4cf77c385e4067e3dc3de603d034c7e441b48ba5f16b3d4e77063066fb464532&redirect_uri=https%3A%2F%2Flocalhost%2Fusers%2Foauth2%2Fcallback&response_type=code"
    window.location.href = authUrl;
}

document.addEventListener('DOMContentLoaded', function() {
    const currentUrl = window.location.href;
    if (currentUrl.includes('/users/oauth2/callback')) {
        // Check if there are any essential parameters or cookies you expect to be set
        if (document.cookie.includes('access_token')) {
            window.location.href = 'https://localhost/#home';
        } else {
            console.error('Token was not set properly.');
            // Redirect to an error page or show an error message
        }
    }
});

function checkAuthentication() {
    fetch('users/check-session/', {
        method: 'GET',
        credentials: 'include', // Ensure cookies are included with the request
    })
    .then(response => {
        if (response.ok) {
            return response.json();
        }
        throw new Error('Not authenticated');
    })
    .then(data => {
        console.log('User is authenticated:', data.user);
        // Handle authenticated user
    })
    .catch(error => {
        console.error('User is not authenticated:', error);
        // Handle unauthenticated user, e.g., redirect to login
		header.classList.add('d-none');
		navigateToSection('register');
    });
}