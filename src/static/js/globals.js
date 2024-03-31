const body = document.body;
const header = document.getElementsByTagName('header')[0];
const nav = document.getElementsByTagName("nav")[0];
const main = document.getElementsByTagName("main")[0];
const pages = document.getElementById("pages");
let activeSection = document.querySelector("section.active");
let lastScroll = 0;
const accessToken = localStorage.getItem('accessToken');
let user = undefined;

// WARNING: Tokens are LOCAL based and not COOKIE based, thus you need to remove what's inside the storage to disconnect

// TODO use access Token to check if logged in before calling any other function