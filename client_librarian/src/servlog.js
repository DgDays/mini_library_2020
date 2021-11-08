// сохранение строк
      
function save() {
    var checkbox = document.getElementById('checkbox1zaal1');
    localStorage.setItem('checkbox1zaal1', checkbox.checked);

    var serialObj = document.getElementById('login');
    localStorage.setItem("login", serialObj.value);

    var serialObj = document.getElementById('region');
    localStorage.setItem("region", serialObj.value);

    var serialObj = document.getElementById('city');
    localStorage.setItem("city", serialObj.value);

    var serialObj = document.getElementById('address');
    localStorage.setItem("address", serialObj.value);

  }

// вывод сохранённых строк снова в свои строки

function load() {    
    var checked = JSON.parse(localStorage.getItem('checkbox1zaal1'));
    document.getElementById("checkbox1zaal1").checked = checked;

    var returnObj = localStorage.getItem("login");
    document.getElementById("login").value = returnObj;

    var returnObj = localStorage.getItem("region");
    document.getElementById("region").value = returnObj;

    var returnObj = localStorage.getItem("city");
    document.getElementById("city").value = returnObj;

    var returnObj = localStorage.getItem("address");
    document.getElementById("address").value = returnObj;
  }

document.getElementById('checkbox1zaal1').addEventListener('click', function () {
      var checked = this.checked;
      
      if (checked) {
        save();
      } else {
        wis()
      }
});

  var localValue = localStorage.getItem('login');
  var localValue2 = localStorage.getItem('region');
  var localValue3 = localStorage.getItem('city');
  var localValue4 = localStorage.getItem('address');
  console.log(localValue,localValue2,localValue3,localValue4);

function wis()  {
    localStorage.clear()
  }

load();

  // сохранение данных в файл.json

function export2json() {
    const originalData = {
      user: [{
          login: localStorage.getItem('login'),
          region: localStorage.getItem('region'),
          city: localStorage.getItem('city'),
          address: localStorage.getItem('address')
        }]
    };

    var fs = require('fs');

    fs.writeFile("./src/settings.json", JSON.stringify(originalData), function(error){

      if(error) throw error; // если возникла ошибка
      console.log("Асинхронная запись файла завершена. Содержимое файла:");
      let data = fs.readFileSync("./src/settings.json", "utf8");
      console.log(data);  // выводим считанные данные
    });
}
  
    document.getElementById('btn').comm = 'login';
    document.getElementById('signin').onclick = function() {
    document.getElementById('btn').comm = 'login';
    };

    document.getElementById('signup').onclick = function() {
    document.getElementById('btn').comm = 'signup';
    };

    document.getElementById('reset').onclick = function() {
    document.getElementById('btn').comm = 'reset';
  };

document.getElementById('btn').onclick = function() {
    if (this.comm == 'login'){
      var log = document.getElementById('login').value;
      var password = document.getElementById('password').value;
      var ret;
      var ws = new WebSocket("ws://127.0.0.1:8765/")
          ws.onopen = function () {
              let data = {
                  comm: 'login',
                  login: log,
                  password: password
              };
              let json = JSON.stringify(data);
              ws.send(json);
          };
          ws.onmessage = function (event) {
                ret = JSON.parse(event.data);
            
                if(ret.res != "None") {
                  // alert('Пароль верный'); 
                  window.close();
                } else {
                  alert('Пароль неверный');
                  document.getElementById('login').value = '';
                  document.getElementById('password').value = '';
                }
            };
    } else if (this.comm == 'signup'){
      var log = document.getElementById('login').value;
      var password = document.getElementById('password').value;
      var email = document.getElementById('email').value;
      if (password == document.getElementById('repass').value){
        var ret;
        var ws = new WebSocket("ws://127.0.0.1:8765/")
            ws.onopen = function () {
                let data = {
                    comm: 'signup',
                    login: log,
                    password: password,
                    email: email
                };
                let json = JSON.stringify(data);
                ws.send(json);
            };
            ws.onmessage = function (event) {
                  ret = JSON.parse(event.data);
                  console.log(ret.res);
                  if(ret.res != "None" && ret.res != 'UserFound') {
                    alert('Новый пользователь добавлен!'); 
                    document.getElementById('signin').click();
                  } else if (ret.res == 'UserFound'){
                    alert('Такой пользователь существует!');
                    document.getElementById('login').value = '';
                    document.getElementById('password').value = '';
                    document.getElementById('repass').value = '';
                    document.getElementById('email').value = '';
                  } else {
                    alert('Использованы неверные символы в пароле, почте или логине.\r\n Проверьте их ещё раз');
                    document.getElementById('login').value = '';
                    document.getElementById('password').value = '';
                    document.getElementById('repass').value = '';
                    document.getElementById('email').value = '';
                  };
              };
            }
    } else if (this.comm == 'reset') {
      var ret;
      var ws = new WebSocket("ws://127.0.0.1:8765/")
          ws.onopen = function () {
              let data = {
                  comm: 'repass'
              };
              let json = JSON.stringify(data);
              console.log(json)
              ws.send(json);
            };
    }
};

document.addEventListener("keydown", function onEvent(event) {
  if (event.key === "Enter") {
      export2json();
      document.getElementById("btn").click();
  }
});