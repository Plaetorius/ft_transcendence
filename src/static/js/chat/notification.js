// Do NOT give a type for normal notifications

// Create a function to append the notification and remove it after a time
function appendAndRemoveNotification(element_list, message, delay = 3000) {
	// Create a new list item
	const listItem = document.createElement('li');
	listItem.classList.add('notification');
	listItem.innerHTML = message;

	// Append the new list item to the list
	element_list.appendChild(listItem);

	// Set a timeout to remove the list item after the specified delay
	setTimeout(() => {
		element_list.removeChild(listItem);
	}, delay);
}

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

	// Add type if any
	if (type)
		notificationContainer.classList.add(type);


	// ALAN's take at notifications
	const element_list = document.getElementById('list-notifications');
	// Call the function
	appendAndRemoveNotification(element_list, message);


	// Update the icon's src attribute and message content
	notificationIcon.src = pathToIcon;
	notificationMessage.innerHTML = message;

	// // Make the notification visible
	// notificationContainer.classList.remove('d-none');

	// // Hide the notification after 3 seconds (3000 milliseconds)
	// setTimeout(() => {
	// 	notificationContainer.classList.add('d-none');
	// 	// Remove type if any
	// 	if (type)
	// 		notificationContainer.classList.remove(type);
	// }, 3000);
}

// TODO remove
// notification("Hey this is a test", 'check', 'success');
