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
console.log(activeSectionFields);
console.log(activeSectionFields.length);
let fieldNb = 0; // TODO reset when changing current
document.addEventListener("keydown", (e) => {
    if (e.key === 'ArrowUp' || e.key === 'ArrowDown') {
        document.getElementById("selected-field").removeAttribute('id');
        if (e.key === 'ArrowUp') {
            fieldNb = ++fieldNb >= activeSectionFields.length ? 0 : fieldNb;
        } else if (e.key === 'ArrowDown') {
            fieldNb = --fieldNb < 0 ? activeSectionFields.length - 1 : fieldNb;
        }
        activeSectionFields[fieldNb].id = "selected-field";
    }
});

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
  