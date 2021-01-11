//main.js
//Основная конфигуация для старта приложения
const electron = require('electron');

const app = electron.app;

const BrowserWindow = electron.BrowserWindow;
// отправка отчёта об ошибках, url укажем в будущем
const { crashReporter } = require('electron')

crashReporter.start({  compress: true, submitURL: '' })

let mainWindow;


function createWindow () {
  // Create the browser window.
  mainWindow = new BrowserWindow({
    titleBarStyle: 'hidden',
    width: 1200,
    height: 800,
    minWidth: 450,
    minHeight: 650,
    icon: __dirname + '/icon.ico'
    //fullscreen:true,

    }); //основная конфигуация


  mainWindow.loadURL('file://' + __dirname + '/index.html'); //загрузка html файла

 
  mainWindow.on('closed', function() {
    mainWindow = null;
  });
} //закрытие главного окна

app.on('ready', createWindow); //создание окна при готовности приложения

app.on('window-all-closed', function () {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});  //закрытие окна и сворачивание в док если это OS X

app.on('activate', function () {

  if (mainWindow === null) {
    createWindow();

  }
}); //восстановление окна

