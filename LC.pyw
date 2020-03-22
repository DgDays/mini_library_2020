'''
Важно!!!

Краткая информация о комментариях:

!!! - То, что нужно сделать в близжайшее время
! - То, что тоже нужно сделать, однако имеет меньший приоритет и нет ограничений по времени

Обозначение окон:
================================ [Главное окно] ================================
Обозначение функций или подокон главных окон:
---------------- [Функция] ----------------

Прошу соблюдать эти условия, для того, чтобы было проще работать.
Так же советую соблюдать и длину ограничителей (слева и справа от надписи одинаковое кол-во)

Спасибо за прочтение

'''
import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
import sqlite3
import datetime
from datetime import timedelta, date
import xlsxwriter
import threading
from tkcalendar import DateEntry

text = ''
values = ''
self_main = ''
self_info = ''
self_book = ''
obj = ["Алгебра","Геометрия","Математика","Русский язык","Английский язык","Французский язык","Немецкий язык","Физика","Химия","География","Информатика","Обществознание","История","Литература"]
class MyTree(ttk.Treeview):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Элементам с тегом green назначить зеленый фон, элементам с тегом red назначить красный фон
        self.tag_configure('A', background='green', foreground='white')
        self.tag_configure('B', background='red', foreground='white')
        self.tag_configure('C', background='yellow')

    def insert(self, parent_node, index, **kwargs):
        '''Назначение тега при добавлении элемента в дерево'''

        item = super().insert(parent_node, index, **kwargs)

        values = kwargs.get('values', None)

        if values:
            if values[1]=="Сдана":
                super().item(item, tag='A')
            elif values[1]=="Просрочена":
                super().item(item, tag='B')
            elif values[1]=="На руках":
                super().item(item, tag='C')

        return item


#================================ Entry с Placeholder =========================

class Entry_Pl(ttk.Entry):
    def __init__(self, master=None, placeholder=None):
        self.entry_var = tk.StringVar()
        super().__init__(master, textvariable=self.entry_var)
  
        if placeholder is not None:
            self.placeholder = placeholder
            self.placeholder_color = 'grey'
            self.default_fg_color = self['foreground']
            self.placeholder_on = False
            self.put_placeholder()
  
            self.entry_var.trace("w", self.entry_change)
  
            # При всех перечисленных событиях, если placeholder отображается, ставить курсор на 0 позицию
            self.bind("<FocusIn>", self.reset_cursor)
            self.bind("<KeyRelease>", self.reset_cursor)
            self.bind("<ButtonRelease>", self.reset_cursor)
  
    def entry_change(self, *args):
        if not self.get():
            self.put_placeholder()
        elif self.placeholder_on:
            self.remove_placeholder()
            self.entry_change()  # На случай, если после удаления placeholder остается пустое поле
  
    def put_placeholder(self):
        self.insert(0, self.placeholder)
        self['foreground'] = self.placeholder_color
        self.icursor(0)
        self.placeholder_on = True
  
    def remove_placeholder(self):
        # Если был вставлен какой-то символ в начало, удаляем не весь текст, а только placeholder:
        text = self.get()[:-len(self.placeholder)]
        self.delete('0', 'end')
        self['foreground'] = self.default_fg_color
        self.insert(0, text)
        self.placeholder_on = False
  
    def reset_cursor(self, *args):
        if self.placeholder_on:
            self.icursor(0)


#================================ Главное окно ================================
class Main(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self,*args, *kwargs)
        self.title("Мини Библиотека 2020") #Заголовок
        w = ((self.winfo_screenwidth() // 2) - 450) # ширина экрана
        h = ((self.winfo_screenheight() // 2) - 225) # высота экрана
        self.geometry('900x450+{}+{}'.format(w, h))#Размер
        self.resizable(False, False)#Изменение размера окна
        self.protocol("WM_DELETE_WINDOW", lambda: sys.exit(0))
        
        self.s = ttk.Style(self)#Использование темы
        self.s.theme_use('clam')

        #================================ Меню ================================
        mainmenu = tk.Menu(self)

        self.config(menu = mainmenu) # Добавляет меню в главное окно

        file_sohranit = tk.Menu(mainmenu, tearoff = 0) # Запретить отделение
        first_and_last = first_and_last_day()
        file_sohranit.add_command(label = "Статистика за месяц", command = lambda: threading.Thread(target = month_excel, args = [first_and_last,]).start())
        file_sohranit.add_command(label = "Статистика за год", command = lambda: threading.Thread(target = year_excel).start())  
        file_sohranit.add_command(label = "Статистика за выбранный срок", command = lambda: Excel())
        file_sohranit.add_separator()
        file_sohranit.add_command(label = "Учёт регистраций")
        file_sohranit.add_command(label = "Учёт книг")
        
        file_infa = tk.Menu(mainmenu, tearoff = 0) # Запретить отделение
        file_infa.add_command(label = "Просмотреть справку")
        file_infa.add_separator()
        file_infa.add_command(label = "О программе")

        mainmenu.add_cascade(label = "Сохранить в Excel", menu = file_sohranit) # Добавляет пункт "Сохранить в отчёт" в меню
        mainmenu.add_command(label = "Учёт книг", command = lambda: Book())
        mainmenu.add_cascade(label = "Информация", menu = file_infa) # Добавляет пункт "Информация" в меню
        mainmenu.add_command(label = 'Уведомления', command= lambda: Not())  
        
        #================================= Поиск ====================================
        self.frame_search = tk.Frame(self)

        self.search = Entry_Pl(self.frame_search, "Поиск")
        self.search.grid(row=0, column=0, padx=3, pady=3)
        
        self.bt_search = ttk.Button(self.frame_search, text='Найти', command = lambda: threading.Thread(target = search, args = [self,]).start())
        self.bt_search.grid(row=0, column=1, padx=3, pady=3)

        self.bt_cancel = ttk.Button(self.frame_search, text='Отмена', command = lambda: threading.Thread(target = update_main, args = [self,]).start())
        self.bt_cancel.grid(row=0, column=2, padx=3, pady=3)

        self.frame_search.pack()

        #================================  Таблица  ================================

        self.fr_watch_both = tk.Canvas(self, background='#e9e9e9',width=900,height=450)

        def fixed_map(option):
            return [elm for elm in style.map('Treeview', query_opt=option)
                    if elm[:2] != ('!disabled', '!selected') and elm[0] != '!disabled !selected']

        style = ttk.Style()
        style.map('Treeview', foreground=fixed_map('foreground'), background=fixed_map('background'))

        # ttk.Style().configure("Treeview",fieldbackground="#e9e9e9")

        #Создание скроллбара
        self.scroll = tk.Scrollbar(self.fr_watch_both)
        self.scroll.pack(side='right',fill='y')

        #Таблица
        self.table = MyTree(self.fr_watch_both, columns=('BirthDay','Class','Litera','Adress','Phone'), height=21, yscrollcommand = self.scroll.set)
        self.scroll.config(orient = 'vertical', command = self.table.yview) #Подключение скроллбара
        self.table.column('#0', minwidth = 260, width=260, anchor=tk.CENTER)
        self.table.column('BirthDay', minwidth = 110, width=110, anchor=tk.CENTER)
        self.table.column('Class', minwidth = 60, width=60, anchor=tk.CENTER)
        self.table.column('Litera', minwidth = 60, width=60, anchor=tk.CENTER)
        self.table.column('Phone', minwidth = 130, width=130, anchor=tk.CENTER)
        self.table.column('Adress', minwidth = 260, width=260, anchor=tk.CENTER)

        self.table.heading('#0', text='ФИО')
        self.table.heading('BirthDay', text='День рождения')
        self.table.heading('Class', text='Класс')
        self.table.heading('Litera', text='Литера')
        self.table.heading('Phone', text='Телефон')
        self.table.heading('Adress', text='Адрес')

        self.profile_menu = tk.Menu(self.table, tearoff=0)

        self.profile_menu.add_command(label = "Добавить читателя", command= lambda: add_profile(self))
        self.profile_menu.add_command(label = "Изменить читателя", command = lambda: edit_profile(self))
        self.profile_menu.add_command(label = "Удалить читателя", command = lambda: threading.Thread(target = del_profile, args = [self,]).start())
        
        self.table.pack(side='left')
        self.table.bind('<Double-Button-1>', lambda event: info(self))
        self.table.bind('<Button-3>', lambda event:self.profile_menu.post(event.x_root,event.y_root))
        self.fr_watch_both.pack(side='bottom', fill='both')

        threading.Thread(target = update_main, args = [self,]).start()

        self.iconbitmap(os.path.dirname(os.path.abspath(__file__))+"/lib.ico")

        


#---------------- Добавить читателя ----------------
class Add_profile(tk.Toplevel):
    def __init__(self, *args, **kwargs):
        tk.Toplevel.__init__(self,*args, *kwargs)
        self.title("Добавить читателя") #Заголовок
        w = ((self.winfo_screenwidth() // 2) - 450) # ширина экрана
        h = ((self.winfo_screenheight() // 2) - 225) # высота экрана
        self.geometry('380x200+{}+{}'.format(w, h))#Размер
        self.resizable(False, False)#Изменение размера окна
        self.s = ttk.Style(self)#Использование темы
        self.s.theme_use('clam')
        self.focus_force()

        #надпись "ФИО"
        self.lb_fio=tk.Label(self,text='ФИО')
        self.lb_fio.grid(row=0,column=0,pady=3)

        #место ввода "ФИО"
        self.en_fio2=ttk.Entry(self,width=49)
        self.en_fio2.grid_configure(row=0,column=1,columnspan=20, sticky='W')

        #надпись "Класс"
        self.lb_class=tk.Label(self,text='Класс')
        self.lb_class.grid(row=1,column=0,pady=3)

        #место ввода "Класс"
        self.en_class2=ttk.Combobox(self,values=[1,2,3,4,5,6,7,8,9,10,11],width=3)
        self.en_class2.grid_configure(row=1,column=1, sticky='W')

        #надпись "Литера"
        self.lb_lit=tk.Label(self,text='Литера')
        self.lb_lit.grid(row=1,column=2)

        #место ввода "Литера"
        self.en_lit2=ttk.Combobox(self,values=['А','Б','В','Г'],width=3)
        self.en_lit2.grid_configure(row=1,column=3,sticky='W')

        #надпись "Телефон"
        self.lb_phone=tk.Label(self,text='Телефон')
        self.lb_phone.grid(row=2,column=0, pady=3)

        #место ввода "Телефон"
        self.en_phone2=ttk.Entry(self,width=14)
        self.en_phone2.grid_configure(row=2,column=1,sticky='W')

        #надпись "Адрес"
        self.lb_adr=tk.Label(self,text='Адрес')
        self.lb_adr.grid(row=3,column=0,pady=3)

        #место ввода "Адрес"
        self.en_adr2=ttk.Entry(self,width=49)
        self.en_adr2.grid_configure(row=3,column=1, columnspan=20,sticky='W')

        self.lb_client = tk.Label(self, text = 'Категория').grid(row=4, column=0, pady=3)

        self.en_client = ttk.Combobox(self,values=["Ученик", "Учитель", "Другой посетитель"],width=18)
        self.en_client.grid_configure(row=4,column=1, columnspan=20, sticky='W')

        #надпись "Дата рождения"
        self.lb_db=tk.Label(self,text='Дата рождения')
        self.lb_db.grid(row=5,column=3,pady=3)


        #место ввода "Дата рождения"
        self.en_db2= DateEntry(self, width=12, background='darkblue',
                    foreground='white', borderwidth=2, year=2020)
        self.en_db2.grid_configure(row=5,column=4,sticky='W')

        #кнопка "Сохранить"
        self.btn_save=ttk.Button(self, text='Сохранить',command=lambda: threading.Thread(target = save_stud2, args = [self,]).start()) #Пример многопоточности
        self.btn_save.grid(row=6,column=4,pady=3)
        self.iconbitmap(os.path.dirname(os.path.abspath(__file__))+"/add.ico")

#---------------- Изменить читателя ----------------
class Edit_profile(tk.Toplevel):
    def __init__(self, *args, **kwargs):
        tk.Toplevel.__init__(self,*args, *kwargs)
        self.title("Редактировать читателя") #Заголовок
        w = ((self.winfo_screenwidth() // 2) - 450) # ширина экрана
        h = ((self.winfo_screenheight() // 2)) # высота экрана
        self.geometry('375x180+{}+{}'.format(w+300, h-125))#Размер
        self.resizable(False, False)#Изменение размера окна
        self.s = ttk.Style(self)#Использование темы
        self.s.theme_use('clam')
        self.focus_force()

        #надпись "ФИО"
        self.lb_fio=tk.Label(self,text='ФИО')
        self.lb_fio.grid(row=0,column=0, ipady=3)

        #место ввода "ФИО"
        self.en_fio2=ttk.Entry(self,width=49)
        self.en_fio2.grid_configure(row=0,column=1, columnspan=40, sticky='W')

        #надпись "Класс"
        self.lb_class=tk.Label(self,text='Класс')
        self.lb_class.grid(row=1,column=0, ipady=3)

        #место ввода "Класс"
        self.en_class2=ttk.Combobox(self,values=[1,2,3,4,5,6,7,8,9,10,11],width=3)
        self.en_class2.grid_configure(row=1,column=1,sticky='W')

        #надпись "Литера"
        self.lb_lit=tk.Label(self,text='Литера')
        self.lb_lit.grid(row=1,column=2, padx=5)

        #место ввода "Литера"
        self.en_lit2=ttk.Combobox(self,values=['А','Б','В','Г'],width=3)
        self.en_lit2.grid_configure(row=1,column=3, sticky='W')

        #надпись "Телефон"
        self.lb_phone=tk.Label(self,text='Телефон')
        self.lb_phone.grid(row=2,column=0, ipady=3)

        #место ввода "Телефон"
        self.en_phone2=ttk.Entry(self,width=14)
        self.en_phone2.grid_configure(row=2,column=1,columnspan=10, sticky='W')

        #надпись "Адрес"
        self.lb_adr=tk.Label(self,text='Адрес')
        self.lb_adr.grid(row=3,column=0, ipady=3)

        #место ввода "Адрес"
        self.en_adr2=ttk.Entry(self,width=49)
        self.en_adr2.grid_configure(row=3,column=1,columnspan=20, sticky='W')

        #надпись "Дата рождения"
        self.lb_db=tk.Label(self,text='Дата рождения')
        self.lb_db.grid(row=4,column=4, ipady=3)

        #место ввода "Дата рождения"
        self.en_db2= DateEntry(self, width=12, background='darkblue',
                    foreground='white', borderwidth=2)
        self.en_db2.grid_configure(row=4,column=5,sticky='W')

        #кнопка "Сохранить"
        self.btn_save=ttk.Button(self, text='Сохранить',command=lambda: threading.Thread(target = edit_stud, args = [self,]).start())
        self.btn_save.grid(row=5,column=5, ipady=3)
        self.iconbitmap(os.path.dirname(os.path.abspath(__file__))+"/edit.ico")



#================================ Информация о читателе ================================
class INFO(tk.Toplevel):
    def __init__(self, *args, **kwargs):
        tk.Toplevel.__init__(self,*args, *kwargs)
        w = ((self.winfo_screenwidth() // 2) - 450) # ширина экрана
        h = ((self.winfo_screenheight() // 2) - 225) # высота экрана
        self.geometry('660x400+{}+{}'.format(w+300, h-125))#Размер
        self.resizable(False, False)#Изменение размера окна
        self.focus_force()
        
        self.s = ttk.Style(self)#Использование темы
        self.s.theme_use('clam')

        self.fr_watch_both = tk.Frame(self, background='#e9e9e9',width=660,height=400)

        def fixed_map(option):
            return [elm for elm in style.map('Treeview', query_opt=option)
                    if elm[:2] != ('!disabled', '!selected') and elm[0] != '!disabled !selected']

        style = ttk.Style()
        style.map('Treeview', foreground=fixed_map('foreground'), background=fixed_map('background'))

        # ttk.Style().configure("Treeview",fieldbackground="#e9e9e9")

        #Создание скроллбара
        self.scroll = tk.Scrollbar(self.fr_watch_both)
        self.scroll.pack(side='right',fill='y')



        #Таблица
        self.info_table = MyTree(self.fr_watch_both, columns=('Author','Status'), height=14, yscrollcommand = self.scroll.set)
        self.scroll.config(orient = 'vertical', command = self.info_table.yview) #Подключение скроллбара
        self.info_table.column('#0', width=250, minwidth=250, anchor=tk.CENTER)
        self.info_table.column('Author', width=250, minwidth=250, anchor=tk.CENTER)
        self.info_table.column('Status', width=140, minwidth=140, anchor=tk.CENTER)

        self.info_table.heading('#0', text='Книга')
        self.info_table.heading('Author', text='Автор')
        self.info_table.heading('Status', text='Статус')

        self.info_table.pack(side='left')
        self.fr_watch_both.pack(side='bottom', fill='both')

        self.profile_menu = tk.Menu(self.info_table, tearoff=0)

        self.profile_menu.add_command(label = "Добавить книгу", command= lambda: add_book(self)) 
        self.profile_menu.add_command(label = "Изменить статус книги", command= lambda: edit_lc(self))
        self.profile_menu.add_command(label = "Удалить книгу", command = lambda: threading.Thread(target = delete_lc, args = [self,]).start())         
        


        self.info_table.bind('<Button-3>', lambda event:self.profile_menu.post(event.x_root,event.y_root))
        self.iconbitmap(os.path.dirname(os.path.abspath(__file__))+"/profile.ico")

#---------------- Добавить книгу читателю ----------------

class Add_lc(tk.Toplevel):
    def __init__(self, *args, **kwargs):
        tk.Toplevel.__init__(self,*args, *kwargs)
        self.title("Добавить книгу в ЧБ") #Заголовок
        w = ((self.winfo_screenwidth() // 2) - 450) # ширина экрана
        h = ((self.winfo_screenheight() // 2) - 225) # высота экрана
        self.geometry('370x100+{}+{}'.format(w+300, h-125))#Размер
        self.resizable(False, False)#Изменение размера окна
        self.s = ttk.Style(self)#Использование темы
        self.s.theme_use('clam')
        self.focus_force()

        #надпись "Книга"
        self.bookname=tk.Label(self,text='Книга')
        self.bookname.grid(row=0, column=0, ipady=3)

        #место ввода "Книга"
        self.en_bookname=ttk.Entry(self,width=49)
        self.en_bookname.grid_configure(row=0, column=1, columnspan=40, sticky='W')

        #надпись "Автор"
        self.lb_author2=tk.Label(self,text='Автор')
        self.lb_author2.grid(row=1, column=0, ipady=3)

        #место ввода "Автор"
        self.en_author2=ttk.Entry(self,width=49)
        self.en_author2.grid_configure(row=1,column=1, columnspan=40, sticky='W')

        #кнопка "Сохранить"
        self.btn_save=ttk.Button(self, text='Сохранить', command=lambda: threading.Thread(target = save_lc2, args = [self,]).start())
        self.btn_save.grid(row=2, column=2, padx=219, pady=3)
        self.iconbitmap(os.path.dirname(os.path.abspath(__file__))+"/add.ico")

#---------------- Изменить книгу читателя ----------------

class Edit_lc(tk.Toplevel):
    def __init__(self, *args, **kwargs):
        tk.Toplevel.__init__(self,*args, *kwargs)
        self.title("Изменить книгу в ЧБ") #Заголовок
        w = ((self.winfo_screenwidth() // 2) - 450) # ширина экрана
        h = ((self.winfo_screenheight() // 2) - 225) # высота экрана
        self.geometry('400x160+{}+{}'.format(w+300, h-125))#Размер
        self.resizable(False, False)#Изменение размера окна
        self.s = ttk.Style(self)#Использование темы
        self.s.theme_use('clam')
        self.focus_force()

        #надпись "Книга"
        self.bookname=tk.Label(self,text='Книга')
        self.bookname.grid(row=0, column=0)

        #место ввода "Книга"
        self.en_bookname=ttk.Entry(self,width=49)
        self.en_bookname.grid_configure(row=0, column=1, columnspan=50, pady=3, sticky='W')

        #надпись "Автор"
        self.lb_author2=tk.Label(self,text='Автор')
        self.lb_author2.grid(row=1, column=0)

        #место ввода "Автор"
        self.en_author2=ttk.Entry(self,width=49)
        self.en_author2.grid_configure(row=1, column=1, columnspan=50, pady=3, sticky='W')

        #надпись "Дата сдачи"
        self.lb_dc = tk.Label(self, text='Дата сдачи').grid(row=2, column=0)

        #место ввода "Дата сдачи"
        self.en_dc = DateEntry(self, width=12, background='darkblue',
                    foreground='white', borderwidth=2)
        self.en_dc.grid_configure(row=2, column=1, columnspan=15, pady=3, sticky='W')

        #надпись "Статус"
        self.lb_stat = tk.Label(self, text='Статус').grid(row=3,column=0)

        #место ввода "Статус"
        self.en_stat = ttk.Combobox(self,values=['На руках','Просрочена','Сдана'],width=15)
        self.en_stat.grid_configure(row=3,column=1, columnspan=15, pady=3, sticky='W')

        #кнопка "Сохранить"
        self.btn_save=ttk.Button(self, text='Сохранить', command=lambda: threading.Thread(target = save_stat, args = [self,]).start())
        self.btn_save.grid(row=4, column=2, padx=220, pady=3)
        self.iconbitmap(os.path.dirname(os.path.abspath(__file__))+"/add.ico")

#!!!---------------- Удалить книгу у читателя ----------------

#!================================ Окно с учётом книг ================================
class Book(tk.Toplevel):

    def __init__(self, *args, **kwargs):
        tk.Toplevel.__init__(self,*args, *kwargs)
        self.title("Учёт книг") #Заголовок
        w = ((self.winfo_screenwidth() // 2) - 450) # ширина экрана
        h = ((self.winfo_screenheight() // 2) - 225) # высота экрана
        self.geometry('713x450+{}+{}'.format(w-100, h-150))#Размер
        self.resizable(False, False)#Изменение размера окна
        
        self.s = ttk.Style(self)#Использование темы
        self.s.theme_use('clam')
        #================================ Поиск ====================================
        self.frame_search = tk.Frame(self)

        self.search = Entry_Pl(self.frame_search, "Поиск")
        self.search.grid(row=0, column=0, padx=3, pady=3)
        
        self.bt_search = ttk.Button(self.frame_search, text='Найти', command = lambda: threading.Thread(target = search_book, args = [self,]).start())
        self.bt_search.grid(row=0, column=1, padx=3, pady=3)

        self.bt_cancel = ttk.Button(self.frame_search, text='Отмена', command = lambda: threading.Thread(target = update_book, args = [self,]).start())
        self.bt_cancel.grid(row=0, column=2, padx=3, pady=3)

        self.frame_search.pack()

        #================================  Таблица  ================================

        self.fr_watch_both = tk.Canvas(self, background='#e9e9e9',width=900,height=450)

        def fixed_map(option):
            return [elm for elm in style.map('Treeview', query_opt=option)
                    if elm[:2] != ('!disabled', '!selected') and elm[0] != '!disabled !selected']

        style = ttk.Style()
        style.map('Treeview', foreground=fixed_map('foreground'), background=fixed_map('background'))

        # ttk.Style().configure("Treeview",fieldbackground="#e9e9e9")

        #Создание скроллбара
        self.scroll = tk.Scrollbar(self.fr_watch_both)
        self.scroll.pack(side='right',fill='y')

        #Таблица
        self.book_table = MyTree(self.fr_watch_both, columns=('AUT','COL'), height=21, yscrollcommand = self.scroll.set)
        self.scroll.config(orient = 'vertical', command = self.book_table.yview) #Подключение скроллбара
        self.book_table.column('#0', minwidth = 230, width=230, anchor=tk.CENTER)
        self.book_table.column('AUT', minwidth = 230, width=230, anchor=tk.CENTER)
        self.book_table.column('COL', minwidth = 230, width=230, anchor=tk.CENTER)

        self.book_table.heading('#0', text='Название')
        self.book_table.heading('AUT', text='Автор(ы)')
        self.book_table.heading('COL', text='Кол-во')

        self.book_menu = tk.Menu(self.book_table, tearoff=0)

        self.book_menu.add_command(label = "Добавить книги", command= lambda: book(self))
        self.book_menu.add_command(label = "Изменить кол-во книг", command = lambda: edit_books(self))
        self.book_menu.add_command(label = "Удалить книги", command = lambda: threading.Thread(target = del_book, args = [self,]).start())

        self.book_table.pack(side='left')
        self.book_table.bind('<Button-3>', lambda event:self.book_menu.post(event.x_root,event.y_root))
        self.fr_watch_both.pack(side='bottom', fill='both')

        threading.Thread(target = update_book, args = [self,]).start()

        self.iconbitmap(os.path.dirname(os.path.abspath(__file__))+"/lib.ico")

#!---------------- Добавить книгу ----------------
class Add_book(tk.Toplevel):
    def __init__(self, *args, **kwargs):
        tk.Toplevel.__init__(self,*args, *kwargs)
        self.title("Добавить книги") #Заголовок
        w = ((self.winfo_screenwidth() // 2) - 450) # ширина экрана
        h = ((self.winfo_screenheight() // 2) - 225) # высота экрана
        self.geometry('280x125+{}+{}'.format(w+300, h-125))#Размер
        self.resizable(False, False)#Изменение размера окна
        self.s = ttk.Style(self)#Использование темы
        self.s.theme_use('clam')

        self.fr = tk.Frame(self)
        self.btn_lit = ttk.Button(self.fr, text='Добавить книгу', command = lambda: lit(self)).grid(row=0,column=0, padx=5)
        self.btn_schbook = ttk.Button(self.fr, text='Добавить учебник', command = lambda: schbook(self)).grid(row=0,column=1, padx=5)
        self.fr.place(relx=0.5,rely=0.5,anchor=tk.CENTER)

        self.lb_name = tk.Label(self,text='Название')
        self.lb_aut = tk.Label(self,text='Автор')
        self.lb_col = tk.Label(self,text='Кол-во')
        #поле ввода "Название"
        self.en_name = ttk.Entry(self, width=35)
        #поле ввода "Автор"
        self.en_aut = ttk.Entry(self, width=35)
        #поле ввода "Кол-во"
        self.en_col = ttk.Entry(self, width=10)
        #
        #кнопка "Сохранить"
        self.save = ttk.Button(self,text='Сохранить', command = lambda: threading.Thread(target = save_book, args = [self,]).start())
        self.save_sch = ttk.Button(self, text='Сохранить', command = lambda: threading.Thread(target = save_schbook, args = [self,]).start())

#!---------------- Изменить книгу ----------------
class Edit_books(tk.Toplevel):
    def __init__(self, *args, **kwargs):
        tk.Toplevel.__init__(self,*args, *kwargs)
        self.title("Редактировать книги") #Заголовок
        w = ((self.winfo_screenwidth() // 2) - 450) # ширина экрана
        h = ((self.winfo_screenheight() // 2) - 225) # высота экрана
        self.geometry('280x125+{}+{}'.format(w+300, h-125))#Размер
        self.resizable(False, False)#Изменение размера окна
        self.s = ttk.Style(self)#Использование темы
        self.s.theme_use('clam')

        self.lb_name = tk.Label(self,text='Название').grid(row=0,column=0)
        self.lb_aut = tk.Label(self,text='Автор').grid(row=1,column=0)
        self.lb_col = tk.Label(self,text='Кол-во').grid(row=2,column=0)
        #поле ввода "Название"
        self.en_name = ttk.Entry(self, width=35)
        self.en_name.grid_configure(row=0, column=1,columnspan=35, pady=3, sticky='W')
        #поле ввода "Автор"
        self.en_aut = ttk.Entry(self, width=35)
        self.en_aut.grid_configure(row=1, column=1,columnspan=35, pady=3, sticky='W')
        #поле ввода "Кол-во"
        self.en_col = ttk.Entry(self, width=10)
        self.en_col.grid_configure(row=2, column=1,columnspan=35, pady=3, sticky='W')
        #кнопка "Сохранить"
        self.save = ttk.Button(self,text='Сохранить', command = lambda: threading.Thread(target = edit_book, args = [self,]).start()).grid(row=3, column=1,pady=3, padx=134)

#================================ Уведомления ================================
class Not(tk.Toplevel):
      def __init__(self,*args, **kwargs):
        tk.Toplevel.__init__(self,*args, *kwargs)
        self.title("Электронный читательский билет - Уведомления")#Заголовок
        self.geometry("770x450+0+0")#Размер окна
        self.resizable(False,False)#Изменение размера окна
        self.configure(background='#e9e9e9')#Фон окна
        self.focus_force()

        #Контейнер уведомлений
        self.fr_watch_both = tk.Frame(self)
        self.fr_watch_both.configure(background='#e9e9e9',width=750,height=456)
        self.fr_watch_both.pack(side='left',fill='both')

        #Создание скроллбара
        self.scroll = tk.Scrollbar(self.fr_watch_both)
        self.scroll.pack(side='right',fill='y')

        #Таблица
        self.table = ttk.Treeview(self.fr_watch_both, columns=('FIO','Phone','Book','CompleteDate','Status'), height=21, show='headings', yscrollcommand = self.scroll.set)

        #Подключение скролбара
        self.scroll.config(orient='vertical', command=self.table.yview)

        self.table.column('FIO', width=150, anchor=tk.CENTER)
        self.table.column('Phone', width=150, anchor=tk.CENTER)
        self.table.column('Book', width=150, anchor=tk.CENTER)
        self.table.column('CompleteDate', width=150, anchor=tk.CENTER)
        self.table.column('Status', width=150, anchor=tk.CENTER)

        self.table.heading('FIO', text='ФИО')
        self.table.heading('Phone', text='Телефон')
        self.table.heading('Book', text='Книга')
        self.table.heading('CompleteDate', text='Дата сдачи')
        self.table.heading('Status', text='Статус')

        self.table.pack(side='left')

        threading.Thread(target = update_not, args = [self,]).start()


        #Иконка
        self.iconbitmap(os.path.dirname(os.path.abspath(__file__))+"/bell.ico")

class Excel(tk.Toplevel):
      def __init__(self,*args, **kwargs):
        tk.Toplevel.__init__(self,*args, *kwargs)
        w = ((self.winfo_screenwidth() // 2) - 450) # ширина экрана
        h = ((self.winfo_screenheight() // 2) - 225) # высота экрана
        self.title("Сохранить в Excel")#Заголовок
        self.geometry('140x120+{}+{}'.format(w+300, h))
        self.resizable(False,False)#Изменение размера окна
        self.configure(background='#e9e9e9')#Фон окна
        self.focus_force()

        self.lb_excel = tk.Label(self, text='Вывести отчёт в Excel')
        self.lb_excel.pack()

        self.frame = tk.Frame(self)
        self.lb_date1 = tk.Label(self.frame, text='С:')
        self.lb_date1.grid(row=0, column=0)

        self.en_date1 = DateEntry(self.frame, width=12, background='darkblue',
                    foreground='white', borderwidth=2)
        self.en_date1.grid_configure(row=0, column=1, pady=3)

        self.lb_date2 = tk.Label(self.frame, text='До:')
        self.lb_date2.grid(row=1,column=0)

        self.en_date2 = DateEntry(self.frame, width=12, background='darkblue',
                    foreground='white', borderwidth=2)
        self.en_date2.grid_configure(row=1,column=1, pady=3)

        self.btn = ttk.Button(self.frame, text='Сохранить отчёт', command= lambda: threading.Thread(target = lub_period_excel, args = [self,]).start())
        self.btn.grid(row=2, column=1, pady=3)


        self.frame.pack(fill='both')


#================================ Работа с БД ================================
def update_not(self):
    x = datetime.date.today().isoformat()#Текущая дата в ISO формате
    #Подключение к БД
    conn = sqlite3.connect(os.path.dirname(os.path.abspath(__file__))+"/LC.db")
    cur = conn.cursor()
    cur.execute('SELECT * FROM LC')#Получение всех значений из таблицы LC БД
    rows = cur.fetchall()
    for row in rows:
        cur.execute("UPDATE LC SET STAT = 'Просрочена' WHERE DC<(?) AND STAT = 'На руках'",(x,))#Обновление статуса если время сдачи < текущего
        conn.commit()
    cur.execute("SELECT FIO, PHONE, BOOK, DC, STAT FROM LC WHERE STAT = 'Просрочена'")#Выборка просроченных книг из БД
    rows = cur.fetchall()
    for row in rows:
        self.table.insert("" , tk.END , values=row)#Вывод в таблицу

def update_main(self):
    self.table.delete(*self.table.get_children())
    conn = sqlite3.connect(os.path.dirname(os.path.abspath(__file__))+"/LC.db")
    cur = conn.cursor()

    #Вывовд всех учеников
    cur.execute("SELECT * FROM PROFILE")
    rows = cur.fetchall()
    for row in rows:
        db = row[1]
        db = datetime.datetime.strptime(db, '%Y-%m-%d')
        db = db.strftime('%d.%m.%Y')
        row = (row[0],db, row[2], row[3], row[4], row[5])
        self.table.insert("" , tk.END ,text=row[0], values=row[1:])

def update_book(self):
    global obj
    self.book_table.delete(*self.book_table.get_children())
    conn = sqlite3.connect(os.path.dirname(os.path.abspath(__file__))+"/LC.db")
    cur = conn.cursor()

    schbook = self.book_table.insert("", tk.END, text='Учебники')
    for less in obj:
        x = self.book_table.insert(schbook, tk.END, text=less)
        cur.execute("SELECT NAME, AUT, COL FROM SCHBOOK WHERE OBJ = (?)",(less,))
        rows = cur.fetchall()
        for row in rows:
            self.book_table.insert(x, tk.END, text = row[0], values=row[1:])

    #Вывовд всех учеников
    cur.execute("SELECT * FROM BOOK")
    rows = cur.fetchall()
    for row in rows:
        cur.execute("SELECT COUNT(*) FROM LC WHERE BOOK = (?) AND AUT = (?) AND (STAT = 'На руках' OR STAT = 'Просрочена')",(row[0],row[1]))
        line = cur.fetchall()
        res = (row[0], row[1], row[2] - line[0][0])
        self.book_table.insert("" , tk.END ,text=res[0], values=res[1:])
    

def update_info(root):
    conn = sqlite3.connect(os.path.dirname(os.path.abspath(__file__))+"/LC.db")
    cur = conn.cursor()

    root.fio = tk.Label(root,text= text, font='Times 15').place(x=250,y=10)
    root.db = tk.Label(root,text="Дата рождения: " + values[0], font='Times 12').place(x=10, y=45)
    if (values[1] == '') and (values[2] == ''):
        root.adr = tk.Label(root, text='Адрес: '+values[3], font='Times 12').place(x=240, y=45)
        root.phone = tk.Label(root,text='Телефон: '+values[4], font='Times 12').place(x=450,y=45)
    else:
        root.clas = tk.Label(root, text='Класс: '+values[1]+' '+values[2], font='Times 12').place(x=240, y=45)
        root.adr = tk.Label(root, text='Адрес: '+values[3], font='Times 12').place(x=10, y=65)
        root.phone = tk.Label(root,text='Телефон: '+values[4], font='Times 12').place(x=260,y=65)
    
    db = datetime.datetime.strptime(values[0], '%d.%m.%Y')#Парсит дату
    db = db.strftime('%Y-%m-%d')#Переводит дату в другой формат
    #Вывовд всех учеников
    cur.execute("SELECT BOOK, AUT, STAT FROM LC WHERE FIO=(?) AND DB=(?) AND PHONE=(?)",(text,db,values[4]))
    rows = cur.fetchall()
    for row in rows:
        root.info_table.insert('', tk.END, text=row[0], values=row[1:])

    root.title("Профиль: {}".format(text)) #Заголовок

        

def info(self):
    global text
    global values
    selected_item = self.table.selection()
    # Получаем значения в выделенной строке
    values = self.table.item(selected_item, option="values")
    text = self.table.item(selected_item, option="text")
    if text != '':
        root = INFO()
        threading.Thread(target = update_info, args = [root,]).start()
    

def add_profile(self):
    global self_main
    self_main = self
    Add_profile()

def save_stud2(self):
    global self_main
    null = ''
    fio = self.en_fio2.get()    #Присваивание переменным значение из полей ввода
    clas = self.en_class2.get()
    lit = self.en_lit2.get()
    phone = self.en_phone2.get()
    db = self.en_db2.get()
    db = datetime.datetime.strptime(db, '%d.%m.%Y')
    db = db.strftime('%Y-%m-%d')
    adr = self.en_adr2.get()
    client = self.en_client.get()
    line = [fio,db,clas,lit,adr,phone,client]
    if null in (fio,db,phone,adr):   #Проверка на пустоту полей
        messagebox.showerror('ОШИБКА!!!','Ошибка! Поля не могут быть пустыми!')  #Вывод ошибки
    else:
        conn = sqlite3.connect(os.path.dirname(os.path.abspath(__file__))+"/LC.db")    #Занесение данных в базу данных
        con_cur = conn.cursor()
        con_cur.execute('INSERT INTO PROFILE VALUES (?,?,?,?,?,?,?)',line)
        conn.commit()

    self_main.table.delete(*self_main.table.get_children())
    conn = sqlite3.connect(os.path.dirname(os.path.abspath(__file__))+"/LC.db")
    cur = conn.cursor()

    #Вывовд всех учеников
    cur.execute("SELECT * FROM PROFILE")
    rows = cur.fetchall()
    for row in rows:
        db = row[1]
        db = datetime.datetime.strptime(db, '%Y-%m-%d')
        db = db.strftime('%d.%m.%Y')
        row = (row[0],db, row[2], row[3], row[4], row[5])
        self_main.table.insert("" , tk.END ,text=row[0], values=row[1:])

def edit_profile(self):
    global self_main
    global text
    global values
    self_main = self
    selected_item = self_main.table.selection()
    # Получаем значения в выделенной строке
    values = self_main.table.item(selected_item, option="values")
    text = self_main.table.item(selected_item, option="text")
    root = Edit_profile()
    root.en_fio2.insert(0,text)
    root.en_db2.set_date(values[0])
    root.en_class2.insert(0, values[1])
    root.en_lit2.insert(0, values[2])
    root.en_adr2.insert(0, values[3])
    root.en_phone2.insert(0, values[4])


def edit_stud(self):
    global self_main
    global text
    global values
    null = ''
    fio = self.en_fio2.get()
    clas = self.en_class2.get()
    lit = self.en_lit2.get()
    phone = self.en_phone2.get()
    db = self.en_db2.get()
    db = datetime.datetime.strptime(db, '%d.%m.%Y')
    db = db.strftime('%Y-%m-%d')
    adr = self.en_adr2.get()
    fio2 = text
    db2 = datetime.datetime.strptime(values[0], '%d.%m.%Y')
    db2 = db2.strftime('%Y-%m-%d')
    phone2 = values[4]
    line = [fio,db,clas,lit,adr,phone,fio2, db2, phone2]
    if null in (fio,db,phone,adr):   #Проверка на пустоту полей
        messagebox.showerror('ОШИБКА!!!','Ошибка! Поля не могут быть пустыми!')  #Вывод ошибки
    else:
        conn = sqlite3.connect(os.path.dirname(os.path.abspath(__file__))+"/LC.db")    #Занесение данных в базу данных
        con_cur = conn.cursor()
        con_cur.execute('UPDATE PROFILE SET FIO = (?), DB = (?), CLA = (?), LIT = (?), ADR = (?), PHONE = (?) WHERE FIO = (?) AND DB = (?) AND PHONE = (?)',line)
        conn.commit()

    self_main.table.delete(*self_main.table.get_children())
    conn = sqlite3.connect(os.path.dirname(os.path.abspath(__file__))+"/LC.db")
    cur = conn.cursor()

    #Вывовд всех учеников
    cur.execute("SELECT * FROM PROFILE")
    rows = cur.fetchall()
    for row in rows:
        db = row[1]
        db = datetime.datetime.strptime(db, '%Y-%m-%d')
        db = db.strftime('%d.%m.%Y')
        row = (row[0],db, row[2], row[3], row[4], row[5])
        self_main.table.insert("" , tk.END ,text=row[0], values=row[1:])

def del_profile(self):
    selected_item = self.table.selection()
    values = self.table.item(selected_item, option="values")
    text = self.table.item(selected_item, option="text")
    ask = messagebox.askyesno('Удалить','Вы точно хотите удалить читателя {}?'.format(text))
    if ask == True:
        db = datetime.datetime.strptime(values[0], '%d.%m.%Y')
        db = db.strftime( '%Y-%m-%d')
        line = (text, db, values[4])
        conn = sqlite3.connect(os.path.dirname(os.path.abspath(__file__))+"/LC.db")    #Занесение данных в базу данных
        con_cur = conn.cursor()
        con_cur.execute('DELETE FROM PROFILE WHERE FIO = (?) AND DB = (?) AND PHONE = (?)',line)
        con_cur.execute('DELETE FROM LC WHERE FIO = (?) AND DB = (?) AND PHONE = (?)',line)
        conn.commit()

    self.table.delete(*self.table.get_children())
    conn = sqlite3.connect(os.path.dirname(os.path.abspath(__file__))+"/LC.db")
    cur = conn.cursor()

    #Вывовд всех учеников
    cur.execute("SELECT * FROM PROFILE")
    rows = cur.fetchall()
    for row in rows:
        db = row[1]
        db = datetime.datetime.strptime(db, '%Y-%m-%d')
        db = db.strftime('%d.%m.%Y')
        row = (row[0],db, row[2], row[3], row[4], row[5])
        self.table.insert("" , tk.END ,text=row[0], values=row[1:])
    
    


def add_book(self):
    global self_info
    self_info = self
    Add_lc()

def save_lc2(self):
    global self_info
    global text
    global values
    null = ''
    fio = text
    db = datetime.datetime.strptime(values[0], '%d.%m.%Y')
    db = db.strftime('%Y-%m-%d')
    phone = values[4]
    di = datetime.date.today() #Присвоение текущей даты
    dc = di + timedelta(days=14)#Определение срока сдачи книги
    book = self.en_bookname.get()    #Присваивание переменным значение из полей ввода
    aut = self.en_author2.get()
    stat = "На руках"
    line = [fio,db,phone,di,dc,aut,book,stat]
    if null in (book,aut,stat):   #Проверка на пустоту полей
        messagebox.showerror('ОШИБКА!!!','Ошибка! Поля не могут быть пустыми!')  #Вывод ошибки
    else:
        conn = sqlite3.connect(os.path.dirname(os.path.abspath(__file__))+"/LC.db")    #Занесение данных в базу данных
        con_cur = conn.cursor()
        con_cur.execute('INSERT INTO LC VALUES (?,?,?,?,?,?,?,?,0)',line)
        conn.commit()


    #Обновление таблицы при нажатии на кнопку никак не хочет работать потому сделал как коммент
    self_info.info_table.delete(*self_info.info_table.get_children())
    conn = sqlite3.connect(os.path.dirname(os.path.abspath(__file__))+"/LC.db")
    cur = conn.cursor()

    #Вывовд всех учеников
    cur.execute("SELECT BOOK, AUT, STAT FROM LC WHERE FIO=(?) AND DB=(?) AND PHONE=(?)",(fio,db,phone))
    rows = cur.fetchall()
    for row in rows:
        self_info.info_table.insert("" , tk.END , text=row[0], values=row[1:])

def edit_lc(self):
    global self_info
    global text
    global values
    self_info = self
    selected_item = self_info.info_table.selection()
    # Получаем значения в выделенной строке
    values1 = self_info.info_table.item(selected_item, option="values")
    text1 = self_info.info_table.item(selected_item, option="text")
    db = datetime.datetime.strptime(values[0],'%d.%m.%Y')
    db = db.strftime('%Y-%m-%d')
    values2 = (db,values[1],values[2],values[3], values[4])
    root = Edit_lc()
    root.en_bookname.insert(0,text1)
    root.en_author2.insert(0,values1[0])
    root.en_stat.insert(0, values1[1])
    line = (text1, values1[0], values1[1], text, values2[0], values2[4])
    conn = sqlite3.connect(os.path.dirname(os.path.abspath(__file__))+"/LC.db")    #Занесение данных в базу данных
    con_cur = conn.cursor()
    con_cur.execute('SELECT DC FROM LC WHERE BOOK = (?) AND AUT = (?) AND STAT = (?) AND FIO = (?) AND DB = (?) AND PHONE = (?)',line)
    rows = con_cur.fetchall()
    rows = datetime.datetime.strptime(rows[0][0], '%Y-%m-%d')
    row = rows.strftime('%d.%m.%Y')
    root.en_dc.set_date(row)
    conn.commit()

def save_stat(self):
    global self_info
    global text
    global values
    null = ''
    selected_item = self_info.info_table.selection()
    # Получаем значения в выделенной строке
    values1 = self_info.info_table.item(selected_item, option="values")
    text1 = self_info.info_table.item(selected_item, option="text")
    name = self.en_bookname.get()
    aut = self.en_author2.get()
    stat = self.en_stat.get()
    db = datetime.datetime.strptime(values[0],'%d.%m.%Y')
    db = db.strftime('%Y-%m-%d')
    dc = self.en_dc.get()
    dc = datetime.datetime.strptime(dc, '%d.%m.%Y')
    dc = dc.strftime('%Y-%m-%d')
    line = (name, aut, stat, dc, text, db, values[4], text1, values1[0], values1[1])
    if null in (name, aut, stat):   #Проверка на пустоту полей
        messagebox.showerror('ОШИБКА!!!','Ошибка! Поля не могут быть пустыми!')  #Вывод ошибки
    else:
        conn = sqlite3.connect(os.path.dirname(os.path.abspath(__file__))+"/LC.db")    #Занесение данных в базу данных
        con_cur = conn.cursor()
        con_cur.execute('UPDATE LC SET BOOK=(?), AUT=(?), STAT=(?), DC=(?) WHERE FIO=(?) AND DB=(?) AND PHONE=(?) AND BOOK=(?) AND AUT=(?) AND STAT=(?)',line)
        conn.commit()
    self_info.info_table.delete(*self_info.info_table.get_children())
    conn = sqlite3.connect(os.path.dirname(os.path.abspath(__file__))+"/LC.db")
    cur = conn.cursor()

    db = datetime.datetime.strptime(values[0],'%d.%m.%Y')
    db = db.strftime('%Y-%m-%d')
    #Вывовд всех учеников
    cur.execute("SELECT BOOK, AUT, STAT FROM LC WHERE FIO=(?) AND DB=(?) AND PHONE=(?)",(text,db,values[4]))
    rows = cur.fetchall()
    for row in rows:
        self_info.info_table.insert("" , tk.END , text=row[0], values=row[1:])

def delete_lc(self):
    global text
    global values
    selected_item = self.info_table.selection()
    # Получаем значения в выделенной строке
    values1 = self.info_table.item(selected_item, option="values")
    text1 = self.info_table.item(selected_item, option="text")
    ask = messagebox.askyesno('Удалить','Вы точно хотите удалить книгу: {}?'.format(text))

    if ask == True:
        db = datetime.datetime.strptime(values[0], '%d.%m.%Y')
        db = db.strftime('%Y-%m-%d')
        line = (text, db, values[4], text1, values1[0], values1[1])
        conn = sqlite3.connect(os.path.dirname(os.path.abspath(__file__))+"/LC.db")    #Занесение данных в базу данных
        con_cur = conn.cursor()
        con_cur.execute('DELETE FROM LC WHERE FIO = (?) AND DB = (?) AND PHONE = (?) AND BOOK = (?) AND AUT = (?) AND STAT = (?)',line)
        conn.commit()

    self.info_table.delete(*self.info_table.get_children())
    conn = sqlite3.connect(os.path.dirname(os.path.abspath(__file__))+"/LC.db")
    cur = conn.cursor()

    db = datetime.datetime.strptime(values[0], '%d.%m.%Y')
    db = db.strftime('%Y-%m-%d')
    #Вывовд всех учеников
    cur.execute("SELECT BOOK, AUT, STAT FROM LC WHERE FIO=(?) AND DB=(?) AND PHONE=(?)",(text,db,values[4]))
    rows = cur.fetchall()
    for row in rows:
        self.info_table.insert("" , tk.END , text=row[0], values=row[1:])


def search(self):
    self.table.delete(*self.table.get_children())
    search = self.search.get()
    self.search.delete('0', 'end')
    conn = sqlite3.connect(os.path.dirname(os.path.abspath(__file__))+"/LC.db")
    cur = conn.cursor()

    #Вывовд всех учеников
    cur.execute("SELECT * FROM PROFILE WHERE FIO LIKE '%{0}%' OR '{0}%' OR '%{0}'".format(search))
    rows = cur.fetchall()
    for row in rows:
        db = row[1]
        db = datetime.datetime.strptime(db, '%Y-%m-%d')
        db = db.strftime('%d.%m.%Y')
        row = (row[0],db, row[2], row[3], row[4], row[5])
        self.table.insert("" , tk.END ,text=row[0], values=row[1:])

def search_book(self):
    self.book_table.delete(*self.book_table.get_children())
    search = self.search.get()
    self.search.delete('0', 'end')
    conn = sqlite3.connect(os.path.dirname(os.path.abspath(__file__))+"/LC.db")
    cur = conn.cursor()

    #Вывовд всех учеников
    cur.execute("SELECT * FROM BOOK WHERE (NAME LIKE '%{0}%' OR '{0}%' OR '%{0}') OR (AUT LIKE '%{0}%' OR '{0}%' OR '%{0}')".format(search))
    rows = cur.fetchall()
    for row in rows:
        cur.execute("SELECT COUNT(*) FROM LC WHERE BOOK = (?) AND AUT = (?) AND (STAT = 'На руках' OR STAT = 'Просрочена')",(row[0],row[1]))
        line = cur.fetchall()
        res = (row[0], row[1], row[2] - line[0][0])
        self.book_table.insert("" , tk.END ,text=res[0], values=res[1:])



def book(self):
    global self_book
    self_book = self
    Add_book()

def save_book(self):
    global self_book
    null = ''
    name = self.en_name.get()
    aut = self.en_aut.get()
    col = self.en_col.get()
    line = (name,aut,col)
    if null in (name,aut,col):   #Проверка на пустоту полей
        messagebox.showerror('ОШИБКА!!!','Ошибка! Поля не могут быть пустыми!')  #Вывод ошибки
    else:
        conn = sqlite3.connect(os.path.dirname(os.path.abspath(__file__))+"/LC.db")    #Занесение данных в базу данных
        con_cur = conn.cursor()
        con_cur.execute('INSERT INTO BOOK VALUES (?,?,?)',line)
        conn.commit()

    self_book.book_table.delete(*self_book.book_table.get_children())
    conn = sqlite3.connect(os.path.dirname(os.path.abspath(__file__))+"/LC.db")
    cur = conn.cursor()

    #Вывовд всех учеников
    schbook = self_book.book_table.insert("", tk.END, text='Учебники')
    for less in obj:
        x = self_book.book_table.insert(schbook, tk.END, text=less)
        cur.execute("SELECT NAME, AUT, COL FROM SCHBOOK WHERE OBJ = (?)",(less,))
        rows = cur.fetchall()
        for row in rows:
            self_book.book_table.insert(x, tk.END, text = row[0], values=row[1:])

    #Вывовд всех учеников
    cur.execute("SELECT * FROM BOOK")
    rows = cur.fetchall()
    for row in rows:
        cur.execute("SELECT COUNT(*) FROM LC WHERE BOOK = (?) AND AUT = (?) AND (STAT = 'На руках' OR STAT = 'Просрочена')",(row[0],row[1]))
        line = cur.fetchall()
        res = (row[0], row[1], row[2] - line[0][0])
        self_book.book_table.insert("" , tk.END ,text=res[0], values=res[1:])

def edit_books(self):
    global self_book
    self_book = self
    root = Edit_books()
    selected_item = self_book.book_table.selection()
    # Получаем значения в выделенной строке
    values1 = self_book.book_table.item(selected_item, option="values")
    text1 = self_book.book_table.item(selected_item, option="text")
    conn = sqlite3.connect(os.path.dirname(os.path.abspath(__file__))+"/LC.db")    #Занесение данных в базу данных
    con_cur = conn.cursor()
    line = (text1,values1[0])
    con_cur.execute('SELECT COL FROM BOOK WHERE NAME=(?) AND AUT=(?)',line)
    col = con_cur.fetchall()
    root.en_name.insert(0, text1)
    root.en_aut.insert(0, values1[0])
    root.en_col.insert(0, col)
    

def edit_book(self):
    global self_book
    selected_item = self_book.book_table.selection()
    # Получаем значения в выделенной строке
    values1 = self_book.book_table.item(selected_item, option="values")
    text1 = self_book.book_table.item(selected_item, option="text")

    conn = sqlite3.connect(os.path.dirname(os.path.abspath(__file__))+"/LC.db")    #Занесение данных в базу данных
    con_cur = conn.cursor()
    con_cur.execute('SELECT COL FROM BOOK WHERE NAME = (?) AND AUT = (?)',(text1, values1[0]))
    f = con_cur.fetchall()

    null = ''
    name = self.en_name.get()
    aut = self.en_aut.get()
    col = self.en_col.get()
    line = (name,aut,col, text1, values1[0], f[0][0])
    if null in (name,aut,col):   #Проверка на пустоту полей
        messagebox.showerror('ОШИБКА!!!','Ошибка! Поля не могут быть пустыми!')  #Вывод ошибки
    else:
        con_cur = conn.cursor()
        con_cur.execute('UPDATE BOOK SET NAME=(?), AUT=(?), COL=(?) WHERE NAME=(?) AND AUT=(?) AND COL=(?)',line)
        conn.commit()

    self_book.book_table.delete(*self_book.book_table.get_children())
    conn = sqlite3.connect(os.path.dirname(os.path.abspath(__file__))+"/LC.db")
    cur = conn.cursor()

    #Вывовд всех учеников
    schbook = self_book.book_table.insert("", tk.END, text='Учебники')
    for less in obj:
        x = self_book.book_table.insert(schbook, tk.END, text=less)
        cur.execute("SELECT NAME, AUT, COL FROM SCHBOOK WHERE OBJ = (?)",(less,))
        rows = cur.fetchall()
        for row in rows:
            self_book.book_table.insert(x, tk.END, text = row[0], values=row[1:])

    #Вывовд всех учеников
    cur.execute("SELECT * FROM BOOK")
    rows = cur.fetchall()
    for row in rows:
        cur.execute("SELECT COUNT(*) FROM LC WHERE BOOK = (?) AND AUT = (?) AND (STAT = 'На руках' OR STAT = 'Просрочена')",(row[0],row[1]))
        line = cur.fetchall()
        res = (row[0], row[1], row[2] - line[0][0])
        self_book.book_table.insert("" , tk.END ,text=res[0], values=res[1:])

def del_book(self):
    selected_item = self.book_table.selection()
    # Получаем значения в выделенной строке
    values1 = self.book_table.item(selected_item, option="values")
    text1 = self.book_table.item(selected_item, option="text")
    ask = messagebox.askyesno('Удалить','Вы точно хотите удалить книгу: {}?'.format(text1))

    if ask == True:
        line = (text1, values1[0], values1[1]) 
        conn = sqlite3.connect(os.path.dirname(os.path.abspath(__file__))+"/LC.db")    #Занесение данных в базу данных
        con_cur = conn.cursor()
        con_cur.execute('DELETE FROM BOOK WHERE NAME = (?) AND AUT = (?) AND COL = (?)',line)
        conn.commit()

    self.book_table.delete(*self.book_table.get_children())
    conn = sqlite3.connect(os.path.dirname(os.path.abspath(__file__))+"/LC.db")
    cur = conn.cursor()

    #Вывовд всех учеников
    schbook = self.book_table.insert("", tk.END, text='Учебники')
    for less in obj:
        x = self.book_table.insert(schbook, tk.END, text=less)
        cur.execute("SELECT NAME, AUT, COL FROM SCHBOOK WHERE OBJ = (?)",(less,))
        rows = cur.fetchall()
        for row in rows:
            self.book_table.insert(x, tk.END, text = row[0], values=row[1:])

    #Вывовд всех учеников
    cur.execute("SELECT * FROM BOOK")
    rows = cur.fetchall()
    for row in rows:
        cur.execute("SELECT COUNT(*) FROM LC WHERE BOOK = (?) AND AUT = (?) AND (STAT = 'На руках' OR STAT = 'Просрочена')",(row[0],row[1]))
        line = cur.fetchall()
        res = (row[0], row[1], row[2] - line[0][0])
        self.book_table.insert("" , tk.END ,text=res[0], values=res[1:])

def save_schbook(self):
    global self_book
    null = ''
    name = self.en_name.get()
    aut = self.en_aut.get()
    col = self.en_col.get()
    less = self.en_less.get()
    line = (name,aut,col,less)
    if null in (name,aut,col):   #Проверка на пустоту полей
        messagebox.showerror('ОШИБКА!!!','Ошибка! Поля не могут быть пустыми!')  #Вывод ошибки
    else:
        conn = sqlite3.connect(os.path.dirname(os.path.abspath(__file__))+"/LC.db")    #Занесение данных в базу данных
        con_cur = conn.cursor()
        con_cur.execute('INSERT INTO SCHBOOK VALUES (?,?,?,?)',line)
        conn.commit()

    self_book.book_table.delete(*self_book.book_table.get_children())
    conn = sqlite3.connect(os.path.dirname(os.path.abspath(__file__))+"/LC.db")
    cur = conn.cursor()

    #Вывовд всех учеников
    schbook = self_book.book_table.insert("", tk.END, text='Учебники')
    for less in obj:
        x = self_book.book_table.insert(schbook, tk.END, text=less)
        cur.execute("SELECT NAME, AUT, COL FROM SCHBOOK WHERE OBJ = (?)",(less,))
        rows = cur.fetchall()
        for row in rows:
            self_book.book_table.insert(x, tk.END, text = row[0], values=row[1:])

    #Вывовд всех учеников
    cur.execute("SELECT * FROM BOOK")
    rows = cur.fetchall()
    for row in rows:
        cur.execute("SELECT COUNT(*) FROM LC WHERE BOOK = (?) AND AUT = (?) AND (STAT = 'На руках' OR STAT = 'Просрочена')",(row[0],row[1]))
        line = cur.fetchall()
        res = (row[0], row[1], row[2] - line[0][0])
        self_book.book_table.insert("" , tk.END ,text=res[0], values=res[1:])
    
    
def schbook(self):
    global obj
    w = ((self.winfo_screenwidth() // 2) - 450) # ширина экрана
    h = ((self.winfo_screenheight() // 2) - 225) # высота экрана
    self.geometry('280x145+{}+{}'.format(w+300, h-125))#Размер
    self.fr.place_forget()
    self.lb_name.grid(row=0,column=0)
    self.lb_aut.grid(row=1,column=0)
    self.lb_col.grid(row=2,column=0)
    self.en_name.grid_configure(row=0, column=1,columnspan=35, pady=3, sticky='W')
    self.en_aut.grid_configure(row=1, column=1,columnspan=35, pady=3, sticky='W')
    self.en_col.grid_configure(row=2, column=1,columnspan=35, pady=3, sticky='W')
    self.lb_less = tk.Label(self, text='Урок').grid(row=3,column=0)
    self.en_less = ttk.Combobox(self,values=obj,width=17)
    self.en_less.grid_configure(row=3, column=1, columnspan=35, pady=3, sticky='W')
    self.save_sch.grid(row=4, column=1,pady=3, padx=134)

def lit(self):
    self.fr.place_forget()
    self.lb_name.grid(row=0,column=0)
    self.lb_aut.grid(row=1,column=0)
    self.lb_col.grid(row=2,column=0)
    self.en_name.grid_configure(row=0, column=1,columnspan=35, pady=3, sticky='W')
    self.en_aut.grid_configure(row=1, column=1,columnspan=35, pady=3, sticky='W')
    self.en_col.grid_configure(row=2, column=1,columnspan=35, pady=3, sticky='W')
    self.save.grid(row=3, column=1,pady=3, padx=134)



#================================ Функции меню ================================
def first_and_last_day():
    x = date.today()
    if x.month in (1,3,5,7,8,10,12):
        first = x.replace(day=1).isoformat()
        last = x.replace(day=31).isoformat()
    elif x.month == 2:
        if x.year % 4 != 0 or (x.year % 100 == 0 and x.year % 400 != 0):
            first = x.replace(day=1).isoformat()
            last = x.replace(day=28).isoformat()
        else:
            first = x.replace(day=1).isoformat()
            last = x.replace(day=29).isoformat()
    else:
        first = x.replace(day=1).isoformat()
        last = x.replace(day=30).isoformat()
    return first,last

def month_excel(x):
    y = date.today().isoformat()
    workbook = xlsxwriter.Workbook('Отчёт {}.xlsx'.format(y))
    worksheet = workbook.add_worksheet()

    bold = workbook.add_format({'bold' : True})

    worksheet.write('A1','ФИО', bold)
    worksheet.write('B1','Дата рождения', bold)
    worksheet.write('C1','Телефон', bold)
    worksheet.write('D1','Дата взятия книги', bold)
    worksheet.write('E1','Дата сдачи книги', bold)
    worksheet.write('F1','Автор', bold)
    worksheet.write('G1','Книга', bold)
    worksheet.write('H1','Статус', bold)

    row = 1
    col = 0

    conn = sqlite3.connect(os.path.dirname(os.path.abspath(__file__))+"/LC.db") 
    cur = conn.cursor()
    cur.execute("SELECT * FROM LC WHERE DI BETWEEN (?) and (?)",x)
    rows = cur.fetchall()
    for fio,db,phone,di,dc,aut,book,stat in (rows):
        worksheet.write(row,col,fio)
        worksheet.write(row,col+1,db)
        worksheet.write(row,col+2,phone)
        worksheet.write(row,col+3,di)
        worksheet.write(row,col+4,dc)
        worksheet.write(row,col+5,aut)
        worksheet.write(row,col+6,book)
        worksheet.write(row,col+7,stat)
        row+=1
    conn.commit()
    workbook.close()

def year_excel():
    x = date.today().replace(day=1,month=1).isoformat()
    y = date.today().isoformat()
    z = date.today().replace(day=31,month=12).isoformat()
    workbook = xlsxwriter.Workbook(os.path.dirname(os.path.abspath(__file__))+'/Отчёт {}.xlsx'.format(y))
    worksheet = workbook.add_worksheet()

    bold = workbook.add_format({'bold' : True})

    worksheet.write('A1','ФИО', bold)
    worksheet.write('B1','Дата рождения', bold)
    worksheet.write('C1','Телефон', bold)
    worksheet.write('D1','Дата взятия книги', bold)
    worksheet.write('E1','Дата сдачи книги', bold)
    worksheet.write('F1','Автор', bold)
    worksheet.write('G1','Книга', bold)
    worksheet.write('H1','Статус', bold)

    row = 1
    col = 0

    conn = sqlite3.connect(os.path.dirname(os.path.abspath(__file__))+"/LC.db") 
    cur = conn.cursor()
    cur.execute("SELECT * FROM LC WHERE DI BETWEEN (?) and (?)",(x,z))
    rows = cur.fetchall()
    for fio,db,phone,di,dc,aut,book,stat in (rows):
        worksheet.write(row,col,fio)
        worksheet.write(row,col+1,db)
        worksheet.write(row,col+2,phone)
        worksheet.write(row,col+3,di)
        worksheet.write(row,col+4,dc)
        worksheet.write(row,col+5,aut)
        worksheet.write(row,col+6,book)
        worksheet.write(row,col+7,stat)
        row+=1
    conn.commit()
    workbook.close()

def lub_period_excel(self):

    x = self.en_date1.get()
    y = self.en_date2.get()

    workbook = xlsxwriter.Workbook(os.path.dirname(os.path.abspath(__file__))+'/Отчёт с {0} по {1} .xlsx'.format(x,y))
    worksheet = workbook.add_worksheet()

    bold = workbook.add_format({'bold' : True})

    worksheet.write('A1','ФИО', bold)
    worksheet.write('B1','Дата рождения', bold)
    worksheet.write('C1','Телефон', bold)
    worksheet.write('D1','Дата взятия книги', bold)
    worksheet.write('E1','Дата сдачи книги', bold)
    worksheet.write('F1','Автор', bold)
    worksheet.write('G1','Книга', bold)
    worksheet.write('H1','Статус', bold)

    row = 1
    col = 0

    x = datetime.datetime.strptime(x, '%d.%m.%Y')
    x = x.strftime('%Y-%m-%d')
    y = datetime.datetime.strptime(y, '%d.%m.%Y')
    y = y.strftime('%Y-%m-%d')

    conn = sqlite3.connect(os.path.dirname(os.path.abspath(__file__))+"/LC.db") 
    cur = conn.cursor()
    cur.execute("SELECT * FROM LC WHERE DI BETWEEN (?) and (?)",(x,y))
    rows = cur.fetchall()
    for fio,db,phone,di,dc,aut,book,stat in (rows):
        worksheet.write(row,col,fio)
        worksheet.write(row,col+1,db)
        worksheet.write(row,col+2,phone)
        worksheet.write(row,col+3,di)
        worksheet.write(row,col+4,dc)
        worksheet.write(row,col+5,aut)
        worksheet.write(row,col+6,book)
        worksheet.write(row,col+7,stat)
        row+=1
    conn.commit()
    workbook.close()



if __name__ == "__main__":
    app = Main()
    app.mainloop()