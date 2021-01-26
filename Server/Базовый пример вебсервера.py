'''
WS Сервер (базовый пример)
'''

import asyncio    # Библиотека стандартной архитектуры асинхронного ввода - вывода в Python
import websockets # Библиотека вебсокетов
import pymysql    # Библиотека для обращения к MySQL
import json       # Библиотека для работы с json
import datetime   # Библиотека для корректного преобразования данных в DD.MM.YYYY
import smtplib    # Библиотека для отправки email сообщений

HOST = '92.49.138.74'
USER = 'DGDays'
PASSWORD = '669202Qazwerty+'

EMAIL = 'mini.lib.2020@gmail.com'
PASS_EMAIL = '669202qaz'

async def hello(websocket, path): # На стороне сервера websocket выполняет 
    # сопрограмму обработчика hello один раз для каждого соединения
    ask = await websocket.recv() # Получение данных с клиента
    ask = json.loads(ask)        # Чтение  json
    
    if ask["comm"] == 'login':   # Проверка комманды. Если comm == login, запуск регистрации
        con = pymysql.connect(host=HOST, user=USER, 
            password=PASSWORD, db='library')
        
        with con:                # Подключение к MySQL
            cur = con.cursor()
            cur.execute('SELECT * FROM users WHERE Login=(%s) AND Password=(%s)', (ask['login'], ask['password'])) # Получение данных пользователя под этим логином и паролем
            greeting = cur.fetchone() # Получение одной единственной записи аккаунта
            if greeting: # Проверка ответа MySQL. Если не None, то создаёт json с данными пользователя и ответом сервера Good
                greeting = { # Сам json с данными юзера
                    "id": greeting[0],
                    "Login": greeting[1],
                    "Password": greeting[2],
                    "Name": greeting[3],
                    "Phone": greeting[4],
                    "Date_of_birthday": greeting[7].strftime("%d.%m.%Y") if greeting[7] != None else greeting[7],
                    'res': "Good"
                } 
            else:
                greeting = {'res': 'None'} # Если ответ MySQL None, то отправляет ответ сервера None
            greeting = json.dumps(greeting) # Преобразование в json для отправки данных
            await websocket.send(greeting) # Отправка json в клиент, который обратился
            
    elif ask["comm"] == 'signup':
        con = pymysql.connect(host=HOST, user=USER,
                              password=PASSWORD, db='library')
        with con:
            cur = con.cursor()
            cur.execute('SELECT * FROM users WHERE (Login=(%s)) OR (Email=(%s))', (ask['login'], ask['email']))
            res = cur.fetchone()
            if (res == None):
                cur.execute(
                    f'INSERT INTO users (Login, Password, Email) VALUES (%s, %s, %s)',
                    (ask['login'], ask['password'], ask['email']))
                con.commit()
                greeting = {'res': 'Good'}
            else:
                greeting = {'res': 'UserFound'}
            greeting = json.dumps(greeting) # Преобразование в json для отправки данных
            await websocket.send(greeting)
    
    elif ask['comm'] == 'repass':
        con = pymysql.connect(host=HOST, user=USER,
                              password=PASSWORD, db='library')
        with con:
            cur = con.cursor()
            cur.execute("SELECT Email FROM users WHERE Login=(%s)",(ask['login'],))
            email = cur.fetchone()[0]
        smtpObj = smtplib.SMTP('smtp.gmail.com', 587)
        smtpObj.starttls()
        smtpObj.login(EMAIL,PASS_EMAIL)
        smtpObj.sendmail(EMAIL,email,"go to bed!")
        smtpObj.quit()


start_server = websockets.serve(hello, "localhost", 8765) # Старт сервака

asyncio.get_event_loop().run_until_complete(start_server) # Асинхронный запуск до тех пор, пока сервак не заработает
asyncio.get_event_loop().run_forever()                    # Запускает петлю работы сервака
# Закрывает соединение после возврата
# async/await -(специальный синтаксис для работы с промисами)
# Промис- это объект,
# представляющий возможное завершение передачи или сбой асинхронной операции
# В Python async гарантирует, что функция вернет промис и обернет в него не промисы. 
