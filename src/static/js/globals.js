const body = document.body;
const header = document.getElementsByTagName('header')[0];
const nav = document.getElementsByTagName("nav")[0];
const main = document.getElementsByTagName("main")[0];
const pages = document.getElementById("pages");
let activeSection = document.querySelector("section.active");
let lastScroll = 0;
let user = undefined;
