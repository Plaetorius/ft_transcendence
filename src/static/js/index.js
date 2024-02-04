// FIXME on a page, reloading the page and hitting return shows the register, has to do with
// previsously selected-field

let view = false;
document.addEventListener("keydown", (e) => {

});

function updateFieldSelection() {
    let activeSectionFields = document.querySelectorAll(".active .current .section-field");
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
    let section = hash ? hash.substring(1) : 'home'; // Replace blank url by url/#home
    let selectedFieldElem = document.querySelector(`#${section}-field`);
    if (selectedFieldElem) {
        changeSectionSwitch(selectedFieldElem, section);
    }
}

document.addEventListener('keydown', (e) => {
	const activeElement = document.activeElement;
	if (activeElement.tagName === 'INPUT' || activeElement.tagName === 'TEXTAREA' || activeElement.tagName === 'SELECT' || activeElement.tagName === 'BUTTON') {
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
	// if (e.key === 'p') {
	// 	document.querySelector('.active').classList.remove('active');
	// 	if (view) {
	// 		document.querySelector(".terminal").classList.add("active");
	// 	} else {
	// 		document.querySelector(".pipboy").classList.add("active");
	// 	}
	// 	view = !view;
	// 	updateFieldSelection();
	// }
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
  // const fieldElements = document.querySelectorAll('[id$="-field"]');
  // console.log(`Field elements: ${fieldElements.length}`);
  // let todiplay = '';
  // for (let i = 0; i < fieldElements.length; i++) {
  //   todiplay += fieldElements[i].innerHTML;
	// }
  // console.log(`${todiplay}`);
  // Probably useless
  // const fieldExists = Array.from(fieldElements).some(element => element.id.replace('-field', '') === fieldName);
  // if (!fieldExists) {
  //   console.log(`Field ${fieldName} doesn't exist!`);
  //   return ;
  // }
  // const sectionExists = Array.from(document.querySelectorAll('[id$="-section"]')).some(element => element.id.replace('-section', '') === fieldName);
  // if (!sectionExists) {
  //   console.log(`Section ${fieldName} doesn't exist!`);
  //   return ;
  // }
  changeSectionSwitch(selectedFieldElem, fieldName);
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
