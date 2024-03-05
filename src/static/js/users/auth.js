// Registration Part

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
            const errorData = await response.json();
            handleRegistrationErrors(errorData);
            return ;
            // throw new Error('Registration failed');
        }
        return response.json();
    })
    .then(data => {
        if (data.access) {
            localStorage.setItem('accessToken', data.access);
            localStorage.setItem('refreshToken', data.refresh);
            console.log('Registered and logged');
            userRegistered();
            showProfile();
            changeSection("welcome");
        } else {
            console.log("No data access");
            throw Error ('No data access');
        }
    })
    .catch(error => {
        // let errorMessageHTML = '';
        // for (const key in error) {
            // if (error.hasOwnProperty(key)) {
                // errorMessageHTML += `<p>${key}: ${error[key].join(', ')}</p>`;
            // }
        // }
        // handleRegistrationErrors(error);

        // console.log(`Catch block ${errorMessageHTML} end`);
        // console.log(`Registration Errors InnerHTML ${document.getElementById('registrationErrors').innerHTML}`);
        // document.getElementById('registrationErrors').innerHTML = errorMessageHTML;
    });    
});

function handleRegistrationErrors(errorData) {
	let errorMessageHTML = '';
	Object.keys(errorData).forEach(key => {
		errorMessageHTML += `<p>${key}: ${errorData[key].join(', ')}</p>`;
	});
	document.getElementById('registrationErrors').innerHTML = errorMessageHTML;
}

function userRegistered() {
    changeSection("welcome");
    setOnline();
}

// Login Part

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
	.then(async response => {
		if (!response.ok) {
			const errorData = await response.json();
			handleLoginErrors(errorData);
			throw new Error('Login Failed');
		}
		return response.json();
	})
	.then(data => {
		if (data.access) {
			localStorage.setItem('accessToken', data.access);
			localStorage.setItem('refreshToken', data.refresh);
			console.log('Logged in successfully');
			console.log(`Data: ${data.user}`);
			alert(`Hello ${data.user.username}!`);
			userLoggedIn();
            // TODO change the edit profile view
            changeSection("home");
		} else {
			throw Error ('No data access');
		}
	})
	.catch(error => {
		console.log(error);
		document.getElementById('loginErrors').textContent = 'Login failed!';
	});
});

function handleLoginErrors(errorData) {
	let errorMessageHTML = '';
	Object.keys(errorData).forEach(key => {
		errorMessageHTML += `<p>${key}: ${errorData[key].join(', ')}</p>`;
	});
	document.getElementById('loginErrors').innerHTML = errorMessageHTML;
}

function userLoggedIn() {
    setOnline();
    showProfile();
}


// Utils Part

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
