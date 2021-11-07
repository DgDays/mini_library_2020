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


function myFunction() {
    document.getElementById("myDropdown").classList.toggle("show");
  }
  
  window.onclick = function(event) {
    if (!event.target.matches('.project-btn-more')) {
  
      var dropdowns = document.getElementsByClassName("dropdown-content");
      var i;
      for (i = 0; i < dropdowns.length; i++) {
        var openDropdown = dropdowns[i];
        if (openDropdown.classList.contains('show')) {
          openDropdown.classList.remove('show');
        }
      }
    }
  }