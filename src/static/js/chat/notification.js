// Do NOT give a type for normal notifications
function notification(message, pathToIcon, type) {
	// Set a default icon
	if (!pathToIcon)
		pathToIcon = '../static/icons/bell.png';
	else
		pathToIcon = '../static/icons/' + pathToIcon + '.png';
	
	// Select the notification container and its components
    const notificationContainer = document.getElementById('notification');
    const notificationIcon = notificationContainer.querySelector('.col-3 img');
    const notificationMessage = notificationContainer.querySelector('.col-9');

	// Add type if any (types are: success, error)
	if (type)
		notificationContainer.classList.add(type);

    // Update the icon's src attribute and message content
    notificationIcon.src = pathToIcon;
    notificationMessage.innerHTML = message;

    // Make the notification visible
    notificationContainer.classList.remove('d-none');

    setTimeout(() => {
        notificationContainer.classList.add('d-none');
		// Remove type if any
		if (type)
			notificationContainer.classList.remove(type);
    }, 3000);
}
