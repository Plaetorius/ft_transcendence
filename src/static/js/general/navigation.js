// Default section to activate on page load, if none is specified in the URL
// TODO change to home
const defaultSection = 'home';
const currentHash = window.location.hash.replace('#', '');
const initialSection = currentHash || defaultSection;

// Set the initial active section based on the current URL hash, if any
setActiveSection(initialSection);

// Navigation links event handlers
document.getElementById("header-home").onclick = () => navigateToSection("home");
document.getElementById("header-games").onclick = () => navigateToSection("games");
document.getElementById("header-friends").onclick = () => navigateToSection("friends");
document.getElementById("header-podium").onclick = () => navigateToSection("podium");
document.getElementById("header-chats").onclick = () => navigateToSection("chats");
document.getElementById("header-profile").onclick = () => navigateToSection("my-profile");

// Listen for popstate event
window.addEventListener('popstate', (event) => {
	const section = event.state ? event.state.section : defaultSection;
	setActiveSection(section);
});

function navigateToSection(sectionId) {
	removeListeners();
    setActiveSection(sectionId);
    history.pushState({ section: sectionId }, '', '#' + sectionId);
	initializeListeners();
}

function setActiveSection(sectionId) {
    document.querySelectorAll("main > section").forEach(section => {
        section.classList.remove("active");
    });
    const activeSection = document.getElementById(sectionId);
    if (activeSection) {
        activeSection.classList.add("active");
		// Calls to functions to load the section
		if (sectionId === 'friends') {
			loadAndDisplayFriends();
		}
    } else {
		// Fallback to default section if the specified ID is not found
        document.getElementById(defaultSection).classList.add("active");
    }
	// Actualise listeners no matter the page
}

function hide_popups() {
	chatPopup.classList.add("d-none");
	chatPopup.classList.remove("d-block");
	profilePopup.classList.add("d-none");
	profilePopup.classList.remove("d-block");
	cardPopup.classList.add("d-none");
	cardPopup.classList.remove("d-block");
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