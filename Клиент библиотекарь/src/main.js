const electron = require('electron');
const app = electron.app;
const BrowserWindow = electron.BrowserWindow;

//создаём окно
function createWindow() {
  let appWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    minWidth: 450,
    minHeight: 650,
    blur: true,
    autoHideMenuBar: true,
    icon: __dirname + '/icon.ico'
  });
  let child = new BrowserWindow({
    width: 800,
    height: 700,
    parent: appWindow,
    closable: false,
    modal: true,
    autoHideMenuBar: true, 
    icon: __dirname + '/icon.ico'
  });
  child.loadFile("src/login.html");
  child.once('ready-to-show', () => {
    child.show()
  })
  // appWindow.webContents.openDevTools();
  appWindow.loadURL(`file://${__dirname}/index.html`);
};

app.on('ready', () => {
  createWindow();
});

app.on('window-all-closed', function() {
  app.quit();
});

// // отправка отчёта об ошибках, url укажем в будущем
// const { crashReporter, globalShortcut } = require('electron')
// crashReporter.start({  compress: true, submitURL: '' })