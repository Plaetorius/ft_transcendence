// Do NOT give a type for normal notifications

// Create a function to append the notification and remove it after a time
function appendAndRemoveNotification(element_list, message, type, delay = 3000) {
	// Create a new list item
	const listItem = document.createElement('li');

	listItem.innerHTML = message;
	listItem.style.z_index = 999;

	listItem.classList.add('notif-item');

	if (type)
		listItem.classList.add(type);


	// Append the new list item to the list
	element_list.appendChild(listItem);

	// First show the notification, then remove it
	setTimeout(() => {
		listItem.classList.add('show');
		setTimeout(() => {
			listItem.classList.remove('show');
			setTimeout(() => {
				element_list.removeChild(listItem);
			}, 600);
		}, delay);
	}, 100);

}

function notification(message, pathToIcon, type, delay = 3) {
	// Set a default icon
	// if (!pathToIcon)
	// 	pathToIcon = '../static/icons/bell.png';
	// else
	// 	pathToIcon = '../static/icons/' + pathToIcon + '.png';


	// Select the notification container and its components
	// const notificationContainer = document.getElementById('notification');
	// const notificationIcon = notificationContainer.querySelector('.col-3 img');
	// const notificationMessage = notificationContainer.querySelector('.col-9');

	// Add type if any (types are: success, error)
	

	// ALAN's take at notifications
	const element_list = document.getElementById('list-notifications');
	// Call the function
	appendAndRemoveNotification(element_list, message, type, delay * 1000);


	// Update the icon's src attribute and message content
	// notificationIcon.src = pathToIcon;
	// notificationMessage.innerHTML = message;

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
