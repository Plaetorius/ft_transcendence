// document.addEventListener('DOMContentLoaded', function() {

// // Toggles navbar on hamburger menu click
// document.getElementById('hamburgerMenu').addEventListener('click', function() {
//     document.getElementById('navbar').classList.toggle('open');
// });

// // document.getElementById('navbar').classList.toggle('open'); // TODO REMOVE

// // Closes navbar when clicking outside of it
// document.addEventListener('click', function(event) {
//     let navbar = document.getElementById('navbar');
//     let isClickInsideNavbar = navbar.contains(event.target);
//     let isHamburgerMenu = event.target === document.getElementById('hamburgerMenu');
//     if (!isClickInsideNavbar && !isHamburgerMenu && navbar.classList.contains('open'))
//         navbar.classList.remove('open');
// });

// // Change header apperance on scroll
// let lastScrollTop = 0;
// window.addEventListener("scroll", () => {
// 	let currentScroll = document.documentElement.scrollTop;
// 	let headerClassList = document.querySelector('header').classList;
// 	currentScroll > lastScrollTop ? headerClassList.add('scroll') : headerClassList.remove('scroll'); // Adds 'scroll' if scrolling down, removes it on scrolling up
// 	lastScrollTop = currentScroll <= 0 ? 0 : currentScroll; // For mobile or negative scroll
// }, false);

// console.log('hey');
// });

