let view = false;
document.addEventListener("keydown", (e) => {

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

function setDefaultSection() {
    let hash = window.location.hash;
    let section = hash ? hash.substring(1) : 'home'; // Default to 'home' if no hash
    let selectedFieldElem = document.querySelector(`#${section}-field`);
    if (selectedFieldElem) {
        changeSectionSwitch(selectedFieldElem, section);
    }
}

document.addEventListener('keydown', (e) => {
	// TODO check if user isn't in an input
	const activeElement = document.activeElement;
	if (activeElement.tagName === 'INPUT' || activeElement.tagName === 'TEXTAREA' || activeElement.tagName === 'SELECT') {
        return;
    }
	// Field listener
	if (e.key === 'Enter') {
		changeSection()
    }

	// Fullscreen listener
	if (e.key === 'f' || e.key === 'F') {
		if (!document.fullscreenElement) {
		  openFullscreen(document.documentElement); // Enter full screen
		} else {
		  closeFullscreen(); // Exit full screen
		}
	  }

	// TODO add history management 
	// BUG crashes everything has section-fields aren't updated
	// DO NOT USE NOW
	if (e.key === 'p') {
		document.getElementById('active').removeAttribute('id');
		if (view) {
			document.querySelector(".terminal").id = "active";
		} else {
			document.querySelector(".pipboy").id = "active";
		}
		view = !view;
		updateFieldSelection();
	}
});

function changeSectionSwitch(selectedFieldElem, destinationSection) {
  document.querySelector(".current").classList.remove("current");
  let current = document.getElementById(`${destinationSection}-section`);
  if (current) {
    current.classList.add("current");
    current.querySelector('.section-field').classList.add("selected-field");
  }
  if (selectedFieldElem) {
    selectedFieldElem.classList.remove("selected-field");
  }

  history.pushState({ section: destinationSection }, '', `#${destinationSection}`);
  updateFieldSelection();
}

function changeSection(sectionName) {
  let selectedFieldElem = document.querySelector(".selected-field");
  let fieldName;
  if (sectionName) {
    fieldName = sectionName;
  } else if (selectedFieldElem) {
    fieldName = selectedFieldElem.id.replace('-field', '');
  }

  const fieldElements = document.querySelectorAll('[id$="-field"]');
  const fieldExists = Array.from(fieldElements).some(element => element.id.replace('-field', '') === fieldName);
  const sectionExists = Array.from(document.querySelectorAll('[id$="-section"]')).some(element => element.id.replace('-section', '') === fieldName);

  if (fieldExists && sectionExists) {
    changeSectionSwitch(selectedFieldElem, fieldName);
  } else {
    console.log("Bad field name or destination section doesn't exist in changeSection()");
  }
}

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
