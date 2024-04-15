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
		console.log(data);
        if (data.access) {
            localStorage.setItem('accessToken', data.access);
            localStorage.setItem('refreshToken', data.refresh);
			authenticated();
        } else {
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
    })
    .then(response => response.json())
    .then(data => {
		console.log(data);
        if (data.access) {
            localStorage.setItem('accessToken', data.access);
            localStorage.setItem('refreshToken', data.refresh);
			authenticated();
		} else {
			handleErrors(data);
        }
    });
});

// Hide pages if user not authenticated
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