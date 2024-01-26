let pageSection = document.getElementsByClassName("page-section");
    
let view = false;
document.addEventListener("keydown", (e) => {
    if (e.key === 'p') {
        document.getElementById('active').removeAttribute('id');
        if (view) {
            document.getElementsByClassName("dashboard")[0].id = "active"
        }
        else {
            document.getElementsByClassName("pipboy")[0].id = "active"
        }
        view = !view;  
    }
});

let activeSectionFields = document.querySelectorAll("#active .current .section-field");
let fieldNb = 0; // TODO reset when changing current
document.addEventListener("keydown", (e) => {
    if (e.key === 'ArrowUp' || e.key === 'ArrowDown') {
        document.getElementsByClassName("selected-field")[0].classList.remove('selected-field');
        if (e.key === 'ArrowUp') {
            fieldNb = ++fieldNb >= activeSectionFields.length ? 0 : fieldNb;
        } else if (e.key === 'ArrowDown') {
            fieldNb = --fieldNb < 0 ? activeSectionFields.length - 1 : fieldNb;
        }
        activeSectionFields[fieldNb].classList.add("selected-field");
    }
});

document.addEventListener('keydown', (e) => {
    // TODO Add check to be sure that user is in the terminal not playing a game / seding a message
    if (e.key === 'Enter') {
        console.log('Test')
        const selectedFieldElem = document.getElementsByClassName("selected-field")[0];
        switch (selectedFieldElem.id) {
            case "register-field":
                //TODO add history stack elements
                document.getElementsByClassName("current")[0].classList.remove("current");
                let current = document.getElementById('register-section').classList.add("current");
                break;
        }
    }
})

document.addEventListener('keydown', (e) => {
    if (e.key === 'f' || e.key === 'F') {
      if (!document.fullscreenElement) {
        openFullscreen(document.documentElement); // Enter full screen
      } else {
        closeFullscreen(); // Exit full screen
      }
    }
  });
  
  function openFullscreen(elem) {
    if (elem.requestFullscreen) {
      elem.requestFullscreen();
    } else if (elem.mozRequestFullScreen) { /* Firefox */
      elem.mozRequestFullScreen();
    } else if (elem.webkitRequestFullscreen) { /* Chrome, Safari & Opera */
      elem.webkitRequestFullscreen();
    } else if (elem.msRequestFullscreen) { /* IE/Edge */
      elem.msRequestFullscreen();
    }
  }
  
  function closeFullscreen() {
    if (document.exitFullscreen) {
      document.exitFullscreen();
    } else if (document.mozCancelFullScreen) { /* Firefox */
      document.mozCancelFullScreen();
    } else if (document.webkitExitFullscreen) { /* Chrome, Safari & Opera */
      document.webkitExitFullscreen();
    } else if (document.msExitFullscreen) { /* IE/Edge */
      document.msExitFullscreen();
    }
  }
  