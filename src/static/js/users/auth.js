// TODO add message to confirm registration / login
// TODO remove ? in url after logging in
// TODO add return key listener for better UX

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
    let errorMessage = '';
    Object.keys(errorData).forEach(key => {
        errorMessage += `\n${key}: ${errorData[key].join(', ')}`;
    });
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
        if (data.access) {
            localStorage.setItem('accessToken', data.access);
            localStorage.setItem('refreshToken', data.refresh);
			authenticated();
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
			authenticated();
		} else {
            throw Error('No data access');
        }
    })
    .catch(error => handleErrors(error, 'loginErrors'));
});

// Hide pages if user not authenticated
if (!accessToken) {
	header.classList.add('d-none');
	navigateToSection('register');
}

document.getElementById('already-account').addEventListener('click', () => {
	navigateToSection('login');
});

function authenticated() {
	header.classList.remove("d-none");
	setOnline();
	// TODO actualise header image
	navigateToSection('home');
	notification('Successfully authenticated!', 'check', 'success');
}


/*
// server.js

const express = require('express');
const passport = require('passport');
const OAuth2Strategy = require('passport-oauth2');

const app = express();

passport.use(new OAuth2Strategy({
    authorizationURL: 'https://api.intra.42.fr/oauth/authorize',
    tokenURL: 'https://api.intra.42.fr/oauth/token',
    clientID: FORTYTWO_APP_ID,
    clientSecret: FORTYTWO_APP_SECRET,
    callbackURL: "http://www.example.com/auth/42/callback"
  },
  function(accessToken, refreshToken, profile, cb) {
    User.findOrCreate({ fortyTwoId: profile.id }, function (err, user) {
      return cb(err, user);
    });
  }
));

app.get('/auth/42',
  passport.authenticate('oauth2'));

app.get('/auth/42/callback', 
  passport.authenticate('oauth2', { failureRedirect: '/login' }),
  function(req, res) {
    // Successful authentication, redirect home.
    res.redirect('/');
  });

app.listen(3000);
*/