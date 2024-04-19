const body = document.body;
const header = document.getElementsByTagName('header')[0];
const nav = document.getElementsByTagName("nav")[0];
const main = document.getElementsByTagName("main")[0];
const pages = document.getElementById("pages");
let activeSection = document.querySelector("section.active");
let lastScroll = 0;
const accessToken = localStorage.getItem('accessToken');
let user = undefined;

//TODO when page is reloaded, add relevent listeners (ex: reloading on friends page removes listeners to profile pictures)