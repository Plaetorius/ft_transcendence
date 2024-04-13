const newspaper_title = document.getElementById('newspaperTitle');
newspaper_title.addEventListener('click', () => {
    if (newspaper_title.innerHTML == 'Boston Bugle')
        console.log('Congrats for finding the easter egg :)'); 
});

window.addEventListener('scroll', () => {
    const currentScroll = window.scrollY;
    if (currentScroll <= 0) {
        header.classList.remove('scrolled');
        return ;
    }
    
    if (currentScroll > lastScroll && !header.classList.contains('scrolled'))
        header.classList.add('scrolled');
    else if (currentScroll < lastScroll && header.classList.contains('scrolled'))
        header.classList.remove('scrolled');
    lastScroll = currentScroll;
});

function blur_background() {
	main.classList.add("blurry");
	header.classList.add("blurry");
}

function unblur_background() {
	main.classList.remove("blurry");
	header.classList.remove("blurry");
}

if (accessToken) {
	showProfile();
	// getPodium();
	// setOnline();
	// setupSettingsForm();
}
