// Default section to activate on page load, if none is specified in the URL
// TODO change to home
const defaultSection = 'register';
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
    setActiveSection(sectionId);
    history.pushState({ section: sectionId }, '', '#' + sectionId);
}

function setActiveSection(sectionId) {
    document.querySelectorAll("main > section").forEach(section => {
        section.classList.remove("active");
    });
    const activeSection = document.getElementById(sectionId);
    if (activeSection) {
        activeSection.classList.add("active");
    } else {
        // Fallback to default section if the specified ID is not found
        document.getElementById(defaultSection).classList.add("active");
    }
}
