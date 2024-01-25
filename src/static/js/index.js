let pageSection = document.getElementsByClassName("page-section");
    
let i = 0;
document.getElementById("toggle-button").addEventListener('click', (e) => {
    // Add tab click behaviour 
    document.getElementById('active').removeAttribute('id');
    if (i % 2) {
        document.getElementsByClassName("dashboard")[0].id = "active"
    }
    else {
        document.getElementsByClassName("pipboy")[0].id = "active"
    }
    i += 1;
});