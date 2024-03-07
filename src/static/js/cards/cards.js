const cardPopup = document.getElementById("card-popup");

// Open Card Popup
document.querySelectorAll(".open-card").forEach(element => {
	element.addEventListener('click', (event) => {
		event.stopPropagation();
		hide_popups();
		cardPopup.classList.remove("d-none");
		cardPopup.classList.add("d-block");
		blur_background();
	});
});

// Close Card Popup
document.addEventListener('click', (event) => {
	if (!cardPopup.contains(event.target) && !event.target.matches('.open-card')) {
		event.stopPropagation();
		cardPopup.classList.add("d-none");
		cardPopup.classList.remove("d-block");
		unblur_background();
	}
});
