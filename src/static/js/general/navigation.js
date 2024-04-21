// Default section to activate on page load, if none is specified in the URL
const defaultSection = 'home';
const currentHash = window.location.hash.replace('#', '');
let initialSection = defaultSection;
let initialState = {};

if (currentHash) {
    const parts = currentHash.split('/');
    initialSection = parts[0];
    if (parts[0] === 'user') {
        if (parts.length > 1 && parts[1]) {
            initialState.username = decodeURIComponent(parts[1]);
            loadUserProfile(initialState.username).catch(e => {
                notification("User not found!", "cross", "error");
                window.location.hash = '#home';
				initialSection = 'home';
				navigateToSection("home");
            });
        } else {
			window.location.hash = '#home';
			initialSection = 'home';
			navigateToSection("home");
        }
    }
}

// Set the initial active section based on the current URL hash, if any
setActiveSection(initialSection, initialState);

// Navigation links event handlers
document.getElementById("header-home").onclick = () => navigateToSection("home");
document.getElementById("header-games").onclick = () => navigateToSection("games");
document.getElementById("header-friends").onclick = () => navigateToSection("friends");
document.getElementById("header-podium").onclick = () => navigateToSection("podium");
document.getElementById("header-news").onclick = () => navigateToSection("news");
document.getElementById("header-profile").onclick = () => navigateToSection("profile");

// Listen for popstate event
window.addEventListener('popstate', (event) => {
    const section = event.state ? event.state.section : defaultSection;
    const stateObj = event.state || {};
    setActiveSection(section, stateObj);
});

function navigateToSection(sectionId, stateObj = {}) {
    removeListeners();

    if (sectionId === 'user' && !stateObj.username) {
        window.location.hash = '#home';
        sectionId = 'home';
        stateObj = {};
    }

    stateObj.section = sectionId;
    let url = `#${sectionId}`;
    if (sectionId === 'user' && stateObj.username) {
        url += `/${encodeURIComponent(stateObj.username)}`;
    }

    history.pushState(stateObj, '', url);
    setActiveSection(sectionId, stateObj);
    initializeListeners();
}

function setActiveSection(sectionId, stateObj = {}) {
    document.querySelectorAll("main > section").forEach(section => {
        section.classList.remove("active");
    });
    const activeSection = document.getElementById(sectionId);
    if (activeSection) {
        activeSection.classList.add("active");
        switch (sectionId) {
            case 'friends':
                loadAndDisplayFriends();
                break;
            case 'podium':
                getPodium();
                break;
            case 'games':
                loadGames();
                break;
            case 'profile':
                console.log('profile');
				getProfile();
				setupSettingsForm();
                break;
            case 'user':
                if (stateObj.username) {
                    loadUserProfile(stateObj.username); 
                    getPlayerMatchHistory(stateObj.username);
                } else {
                    navigateToSection('home');
                }
                break;
            default:
                break;
        }
    } else {
        document.getElementById(defaultSection).classList.add("active");
    }
}

function hide_popups() {
	chatPopup.classList.add("d-none");
	chatPopup.classList.remove("d-block");
	profilePopup.classList.add("d-none");
	profilePopup.classList.remove("d-block");
	settingsPopup.classList.add("d-none");
	settingsPopup.classList.remove("d-block");
}

function initializeListeners() {
	document.addEventListener('click', openProfileHandler);
	document.addEventListener('click', closeProfileHandle);
}

function removeListeners() {
    document.removeEventListener('click', openProfileHandler);
	document.removeEventListener('click', closeProfileHandle);
}

async function loadUserProfile(username) {
    try {
        let visited_user = await getUser(username);
        if (!visited_user) {
            throw new Error("User not found");
        }
        document.getElementById("user-picture").src = visited_user.profile_picture_url;
        document.getElementById("user-username").innerHTML = `<span class="online-status online"></span>${visited_user.username}`;
        document.getElementById("user-elo").innerHTML = `<span>Elo: </span>${visited_user.elo}`;
        const dateJoined = new Date(visited_user.date_joined);
        const formattedDate = [
            dateJoined.getDate().toString().padStart(2, '0'),
            (dateJoined.getMonth() + 1).toString().padStart(2, '0'),
            dateJoined.getFullYear()
        ].join('/');
        document.getElementById("user-joined").innerHTML = `<span>Joined: </span>${formattedDate}`;
    } catch (error) {
        notification(error.message, "cross", "error");
        navigateToSection("home");
    }
}

