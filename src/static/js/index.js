let view = false;
document.addEventListener("keydown", (e) => {
  // TODO add history management 
  // BUG crashes everything has section-fields aren't updated
  // DO NOT USE NOW
    if (e.key === 'p') {
        document.getElementById('active').removeAttribute('id');
        if (view) {
            document.querySelector(".dashboard").id = "active";
        } else {
            document.querySelector(".pipboy").id = "active";
        }
        view = !view;
        updateFieldSelection();
    }
});

function updateFieldSelection() {
    let activeSectionFields = document.querySelectorAll("#active .current .section-field");
    let fieldNb = 0;
    document.addEventListener("keydown", (e) => {
        if (e.key === 'ArrowUp' || e.key === 'ArrowDown') {
            document.querySelector(".selected-field").classList.remove('selected-field');
            if (e.key === 'ArrowUp') {
                fieldNb = (fieldNb - 1 + activeSectionFields.length) % activeSectionFields.length;
            } else if (e.key === 'ArrowDown') {
                fieldNb = (fieldNb + 1) % activeSectionFields.length;
            }
            activeSectionFields[fieldNb].classList.add("selected-field");
        }
    });
}

function changeSection(selectedFieldElem, destinationSection) {
    document.querySelector(".current").classList.remove("current");
    let current = document.getElementById(`${destinationSection}-section`);
    current.classList.add("current");
    current.querySelector('.section-field').classList.add("selected-field");
    selectedFieldElem.classList.remove("selected-field");

    history.pushState({ section: destinationSection }, '', `#${destinationSection}`);
    updateFieldSelection();
}

function setDefaultSection() {
    let hash = window.location.hash;
    let section = hash ? hash.substring(1) : 'home'; // Default to 'home' if no hash
    let selectedFieldElem = document.querySelector(`#${section}-field`);
    if (selectedFieldElem) {
        changeSection(selectedFieldElem, section);
    }
}

document.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
        let selectedFieldElem = document.querySelector(".selected-field");
        switch (selectedFieldElem.id) {
            case "home-field":
                changeSection(selectedFieldElem, "home");
                break;
            case "register-field":
                changeSection(selectedFieldElem, "register");
                break;
            case "login-field":
                changeSection(selectedFieldElem, "login");
                break;
            default:
                break;
        }
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

window.addEventListener('popstate', (event) => {
    if (event.state && event.state.section) {
        let section = event.state.section;
        document.querySelector(".current").classList.remove("current");
        let newCurrent = document.getElementById(`${section}-section`);
        newCurrent.classList.add("current");
        newCurrent.querySelector('.section-field').classList.add("selected-field");
        updateFieldSelection();
    }
});

// Call setDefaultSection initially to set the initial section
setDefaultSection();
// Call updateFieldSelection initially to set up the field navigation
updateFieldSelection();
