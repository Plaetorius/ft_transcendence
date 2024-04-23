const newspaper_title = document.getElementById('newspaperTitle');
newspaper_title.addEventListener('click', () => {
    if (newspaper_title.innerHTML == 'Boston Bugle')
        notification('Congrats for finding the easter egg :)', 'check', 'success'); 
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

async function onPageReload() {
	const isAuthenticated = await checkAuthentication();
	if (isAuthenticated) {
		getProfile();
		getPodium();
		setOnline();
		actualiseFriendsSection();
		setupSettingsForm();
	} else {
		header.classList.add('d-none');
		navigateToSection('register');
	}
}

onPageReload();

document.querySelectorAll('.sentence').forEach(sentence => {
    sentence.addEventListener('mouseover', () => {
        sentence.classList.add('active');
    });
    sentence.addEventListener('mouseout', () => {
        sentence.classList.remove('active');
    });
});

document.addEventListener("DOMContentLoaded", function() {
    const sentences = document.querySelectorAll('.appear-on-load');
    sentences.forEach((span, index) => {
        // Delay each sentence's animation start time
        span.style.animationDelay = `${index * 0.03}s`;
    });
});