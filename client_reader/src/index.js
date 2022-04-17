const ipc = require('electron').ipcRenderer

ipc.on('login', function (event, arg){
    console.log(arg);
    var blur = 10;
    let timer = setInterval(function(){
        blur = blur - 0.2
        if (blur <= 0){
            clearInterval(timer);
        }
        else{
            document.getElementById('body').style.filter = 'blur('+blur+'px)';
        }
    }, 20)
})


function myDropdown() {
    document.getElementById("myDropdown").classList.toggle("show");
}
  
window.onclick = function(event) {
    if (!event.target.matches('.project-btn-more')) {
  
      var dropdowns = document.getElementsByClassName("dropdown-content");
      for (var i = 0; i < dropdowns.length; i++) {
        var openDropdown = dropdowns[i];
        if (openDropdown.classList.contains('show')) {
          openDropdown.classList.remove('show');
        }
      }
    }
}

// как вариант можно удалять через жс див

// function delete_this_div() {    
//   var elem = document.getElementById("chitatel_1");
//   elem.parentNode.removeChild(elem);
// }

function addElement() {
  // переменные для создания читателей
  var _data = "Unknown", _deadline = "Unknown", name_person = "Unknown", name_book = "Unknown", user_char = "Unknown", user_class = "Unknown";
  library.insertAdjacentHTML('afterbegin', `<div class="project-box-wrapper" id=""><div class="project-box" style="background-color: #fee4cb;"><div class="project-box-header"><span>${_data}</span><div class="more-wrapper"><div class="dropdown"><button onclick="myDropdown()" class="project-btn-more"><!-- меню в другом виде списка открывается за пределами браузера --><div id="myDropdown" class="dropdown-content"><a onclick="addElement()" href="#">Добавить</a><a href="#">Выбрать</a><a href="#">Подробнее</a></div><svg xmlns="http://www.w3.org/2000/svg" pointer-events="none" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-more-vertical"><circle cx="12" cy="12" r="1" /><circle cx="12" cy="5" r="1" /><circle cx="12" cy="19" r="1" /></svg></button></div></div></div><div class="project-box-content-header"><p class="box-content-header">Ученик(-ца) ${user_class} "${user_char}"</p><p class="box-content-subheader">${name_person}</p></div><div class="box-progress-wrapper"><p class="box-progress-header">Взял(-а) книги: </p><!-- <div class="box-progress-bar"><span class="box-progress" style="width: 60%; background-color: #ff942e"></span></div><p class="box-progress-percentage">60%</p> --><div class="box-content-reader"><p class="box-content-reader">${name_book}</p></div></div><div class="project-box-footer"><div class="participants"><button class="add-participant" style="color: #ff942e;"><svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" class="feather feather-plus"><path d="M12 5v14M5 12h14" /></svg></button></div><div class="days-left" style="color: #ff942e;">${_deadline}</div><!-- ЗВЁЗДОЧКА --><div class="star-checkbox"><input type="checkbox" id="star-1"><label for="star-1"><svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-star"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2" /></svg></label></div></div></div></div>`);       
}
