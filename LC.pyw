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
import tkinter.font as tkFont
from tkinter import ttk, messagebox
from ttkthemes import ThemedStyle
import sys
import os
import sqlite3
import datetime
from datetime import timedelta, date
import xlsxwriter
import threading
from tkcalendar import DateEntry
from tkinter import filedialog as fd
import pyglet

text = ''
values = ''
self_main = 'close'
self_info = 'close'
self_book = 'close'
self_main_book = 'close'
self_main_not = 'close'
self_book_info = 'close'
book_add = 0
prev_column = None
obj = ["Алгебра","Геометрия","Математика","Русский язык","Английский язык","Французский язык","Немецкий язык","Физика","Химия","География","Информатика","Обществознание","История","Литература"]

easter_egg = 0

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
            if "Сдана" in values:
                super().item(item, tag='A')
            elif "Просрочена" in values:
                super().item(item, tag='B')
            elif "На руках" in values:
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
            self['font'] = 'Arial 11'
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
        default_font = tkFont.nametofont("TkDefaultFont")# Получение дэфолтного значения шрифта
        default_font.configure(size=11, family='Arial')# Изменение дэфолтного значения шрифта

        self.option_add("*Font", default_font) # Использование нашего шрифта

        self.title("Мини Библиотека 2020") #Заголовок
        w = ((self.winfo_screenwidth() // 2) - 455) # ширина экрана
        h = ((self.winfo_screenheight() // 2) - 225) # высота экрана
        self.geometry('910x450+{}+{}'.format(w, h))#Размер
        self.resizable(False, False)#Изменение размера окна
        self.protocol("WM_DELETE_WINDOW", lambda: exit_main())
        theme = open(os.path.dirname(os.path.abspath(__file__))+'/theme.txt','r')
        style = ThemedStyle()
        var_style = tk.StringVar()
        var_style.set(theme.read())
        theme.close()
        style.set_theme(var_style.get())
        style.configure("Treeview.Heading", font=('Arial', 11))# Изменение шрифта столбцов в Treeview
        style.configure('Treeview', font=('Arial',11))
        style.configure('TButton', font=('Arial',11))
        style.configure('TMenubutton', font=('Arial',11))

        #================================ Меню ================================
        self.fr = ttk.Frame(self)
        self.fr.pack(fill='x')

        btn_file = ttk.Menubutton(self.fr, text='Файл')

        file_sohranit = tk.Menu(btn_file, tearoff = 0) # Запретить отделение
        first_and_last = first_and_last_day()
        file_sohranit.add_command(label = 'Загрузить читателей из TXT', command = lambda: threading.Thread(target = open_txt, args= [self,]).start())
        file_sohranit.add_separator()
        file_sohranit.add_command(label = "Статистика за месяц", command = lambda: threading.Thread(target = month_excel, args = [first_and_last,]).start())
        file_sohranit.add_command(label = "Статистика за год", command = lambda: threading.Thread(target = year_excel).start())  
        file_sohranit.add_command(label = "Статистика за выбранный срок", command = lambda: Excel())
        file_sohranit.add_separator()
        file_sohranit.add_command(label = "Учёт регистраций", command = lambda: threading.Thread(target = excel_uchet_reg).start())
        file_sohranit.add_command(label = "Учёт книг", command = lambda: threading.Thread(target = uchet_book).start())

        btn_file.config(menu=file_sohranit)
        btn_file.grid(row=0, column=0, padx=5, pady=5)

        btn_style = ttk.Menubutton(self.fr, text='Темы')

        style_menu = tk.Menu(btn_style, tearoff = 0, selectcolor = 'green')
        style_menu.add_radiobutton(label = 'Breeze - Светлая', variable=var_style, value='breeze', command = lambda: style_change(var_style.get()))
        style_menu.add_radiobutton(label = 'Breeze - Тёмная', variable=var_style, value='nightbreeze', command = lambda: style_change(var_style.get()))
        
        btn_uch = ttk.Button(self.fr, text='Учёт книг', command = lambda: self_book_open(self))
        btn_uch.grid(row=0, column=1, padx=5, pady=5)

        btn_not = ttk.Button(self.fr, text='Уведомления', command = lambda: self_not_open(self))
        btn_not.grid(row=0, column=2, padx=5, pady=5)

        btn_style.config(menu=style_menu)
        btn_style.grid(row=0, column=3, padx=5, pady=5)

        btn_inf = ttk.Menubutton(self.fr, text='Информация')
        
        file_infa = tk.Menu(btn_inf, tearoff = 0) # Запретить отделение
        file_infa.add_command(label = "Просмотреть справку", command = lambda: Spravka())
        file_infa.add_separator()
        file_infa.add_command(label = "О программе", command = lambda: Information())

        btn_inf.config(menu=file_infa)
        btn_inf.grid(row=0, column=4, padx=5, pady=5)
        
        #================================= Поиск ====================================
        self.frame_search1 = ttk.Frame(self)
        self.frame_search = ttk.Frame(self.frame_search1)

        self.search = Entry_Pl(self.frame_search, "Поиск")
        self.search.grid(row=0, column=0, padx=3, pady=3)
        
        self.bt_search = ttk.Button(self.frame_search, text='Найти', command = lambda: threading.Thread(target = search, args = [self,]).start())
        self.bt_search.grid(row=0, column=1, padx=3, pady=3)

        self.bt_cancel = ttk.Button(self.frame_search, text='Отмена', command = lambda: threading.Thread(target = update_main, args = [self,]).start())
        self.bt_cancel.grid(row=0, column=2, padx=3, pady=3)

        self.frame_search.pack()
        self.frame_search1.pack(fill='x')

        self.bind('<Return>', lambda event: search_enter(self))
        self.bt_search.bind('<Button-1>', lambda event: easter1())
        self.bt_cancel.bind('<Button-1>', lambda event: easter2())
        self.search.bind('<Button-1>', lambda event: easter3())

        #================================  Таблица  ================================

        self.fr_watch_both = tk.Canvas(self, background='#e9e9e9',width=900,height=450)

        def fixed_map(option):
            return [elm for elm in style.map('Treeview', query_opt=option)
                    if elm[:2] != ('!disabled', '!selected') and elm[0] != '!disabled !selected']

        style = ttk.Style()
        style.map('Treeview', foreground=fixed_map('foreground'), background=fixed_map('background'))

        # ttk.Style().configure("Treeview",fieldbackground="#e9e9e9")

        #Создание скроллбара
        self.scroll = ttk.Scrollbar(self.fr_watch_both)
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

        self.table.heading("#0", command=lambda : sort_0(self.table, "#0", False))

        columns = self.table['columns']
        
        for col in columns:
            self.table.heading(col, text=col, command=lambda _col=col: \
                             sort(self.table, _col, False))

        self.table.heading('#0', text='ФИО')
        self.table.heading('BirthDay', text='Дата рождения')
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

        
        self.bind('<KeyPress>', lambda event: event_handler_main(event, self))


        self.iconbitmap(os.path.dirname(os.path.abspath(__file__))+"/lib.ico")

        


#---------------- Добавить читателя ----------------
class Add_profile(tk.Toplevel):
    def __init__(self, *args, **kwargs):
        tk.Toplevel.__init__(self,*args, *kwargs)
        self.title("Добавить читателя") #Заголовок
        w = ((self.winfo_screenwidth() // 2) - 450) # ширина экрана
        h = ((self.winfo_screenheight() // 2) - 225) # высота экрана
        self.geometry('480x240+{}+{}'.format(w, h))#Размер
        self.resizable(False, False)#Изменение размера окна
        self.protocol("WM_DELETE_WINDOW", lambda: self_main_null(self))
        self.attributes("-topmost",True)

        
        self.focus_force()

        #надпись "ФИО"
        self.lb_fio=ttk.Label(self,text='ФИО', font= 'Arial 11')
        self.lb_fio.grid(row=0,column=0,pady=3)

        #место ввода "ФИО"
        self.en_fio2=ttk.Entry(self,width=49, font= 'Arial 11')
        self.en_fio2.grid_configure(row=0,column=1,columnspan=20, sticky='W')

        #надпись "Класс"
        self.lb_class=ttk.Label(self,text='Класс', font= 'Arial 11')
        self.lb_class.grid(row=1,column=0,pady=3)

        #место ввода "Класс"
        self.en_class2=ttk.Combobox(self,values=[1,2,3,4,5,6,7,8,9,10,11],width=3, font= 'Arial 11')
        self.en_class2.grid_configure(row=1,column=1, sticky='W')

        #надпись "Литера"
        self.lb_lit=ttk.Label(self,text='Литера', font= 'Arial 11')
        self.lb_lit.grid(row=1,column=2)

        #место ввода "Литера"
        self.en_lit2=ttk.Combobox(self,values=['А','Б','В','Г'],width=3, font= 'Arial 11')
        self.en_lit2.grid_configure(row=1,column=3,sticky='W')

        #надпись "Телефон"
        self.lb_phone=ttk.Label(self,text='Телефон', font= 'Arial 11')
        self.lb_phone.grid(row=2,column=0, pady=3)

        #место ввода "Телефон"
        self.en_phone2=ttk.Entry(self,width=14, font= 'Arial 11')
        self.en_phone2.grid_configure(row=2,column=1,sticky='W')

        #надпись "Адрес"
        self.lb_adr=ttk.Label(self,text='Адрес', font= 'Arial 11')
        self.lb_adr.grid(row=3,column=0,pady=3)

        #место ввода "Адрес"
        self.en_adr2=ttk.Entry(self,width=49, font= 'Arial 11')
        self.en_adr2.grid_configure(row=3,column=1, columnspan=20,sticky='W')

        self.lb_client = ttk.Label(self, text = 'Категория', font= 'Arial 11').grid(row=4, column=0, pady=3)

        self.en_client = ttk.Combobox(self,values=["Ученик", "Учитель", "Другой посетитель"],width=18, font= 'Arial 11')
        self.en_client.grid_configure(row=4,column=1, columnspan=20, sticky='W')

        #надпись "Дата рождения"
        self.lb_db=ttk.Label(self,text='Дата рождения', font= 'Arial 11')
        self.lb_db.grid(row=5,column=3,pady=3)


        #место ввода "Дата рождения"
        self.en_db2= DateEntry(self, width=12, background='darkblue',
                    foreground='white', borderwidth=2, year=2020, font= 'Arial 11')
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
        self.geometry('480x240+{}+{}'.format(w+300, h-125))#Размер
        self.resizable(False, False)#Изменение размера окна
        self.protocol("WM_DELETE_WINDOW", lambda: self_main_null(self))
        self.attributes("-topmost",True)

        
        self.focus_force()

        #надпись "ФИО"
        self.lb_fio=ttk.Label(self,text='ФИО', font= 'Arial 11')
        self.lb_fio.grid(row=0,column=0, ipady=3)

        #место ввода "ФИО"
        self.en_fio2=ttk.Entry(self,width=49, font= 'Arial 11')
        self.en_fio2.grid_configure(row=0,column=1, columnspan=40, sticky='W')

        #надпись "Класс"
        self.lb_class=ttk.Label(self,text='Класс', font= 'Arial 11')
        self.lb_class.grid(row=1,column=0, ipady=3)

        #место ввода "Класс"
        self.en_class2=ttk.Combobox(self,values=[1,2,3,4,5,6,7,8,9,10,11],width=3, font= 'Arial 11')
        self.en_class2.grid_configure(row=1,column=1,sticky='W')

        #надпись "Литера"
        self.lb_lit=ttk.Label(self,text='Литера', font= 'Arial 11')
        self.lb_lit.grid(row=1,column=2, padx=5)

        #место ввода "Литера"
        self.en_lit2=ttk.Combobox(self,values=['А','Б','В','Г'],width=3, font= 'Arial 11')
        self.en_lit2.grid_configure(row=1,column=3, sticky='W')

        #надпись "Телефон"
        self.lb_phone=ttk.Label(self,text='Телефон', font= 'Arial 11')
        self.lb_phone.grid(row=2,column=0, ipady=3)

        #место ввода "Телефон"
        self.en_phone2=ttk.Entry(self,width=14, font= 'Arial 11')
        self.en_phone2.grid_configure(row=2,column=1,columnspan=10, sticky='W')

        #надпись "Адрес"
        self.lb_adr=ttk.Label(self,text='Адрес', font= 'Arial 11')
        self.lb_adr.grid(row=3,column=0, ipady=3)

        #место ввода "Адрес"
        self.en_adr2=ttk.Entry(self,width=49, font= 'Arial 11')
        self.en_adr2.grid_configure(row=3,column=1,columnspan=20, sticky='W')

        #надпись "Дата рождения"
        self.lb_db=ttk.Label(self,text='Дата рождения', font= 'Arial 11')
        self.lb_db.grid(row=4,column=4, ipady=3)

        #место ввода "Дата рождения"
        self.en_db2= DateEntry(self, width=12, background='darkblue',
                    foreground='white', borderwidth=2, font= 'Arial 11')
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
        self.geometry('710x400+{}+{}'.format(w+300, h-125))#Размер
        self.resizable(False, False)#Изменение размера окна
        self.focus_force()
        self.protocol("WM_DELETE_WINDOW", lambda: self_main_null(self))
        
        self.frame = ttk.Frame(self)
        self.frame.pack(fill='x')

        self.fr_watch_both = ttk.Frame(self,width=660,height=400)

        def fixed_map(option):
            return [elm for elm in style.map('Treeview', query_opt=option)
                    if elm[:2] != ('!disabled', '!selected') and elm[0] != '!disabled !selected']

        style = ttk.Style()
        style.map('Treeview', foreground=fixed_map('foreground'), background=fixed_map('background'))

        # ttk.Style().configure("Treeview",fieldbackground="#e9e9e9")
        

        #Создание скроллбара
        self.scroll = ttk.Scrollbar(self.fr_watch_both)
        self.scroll.pack(side='right',fill='y')



        #Таблица
        self.info_table = MyTree(self.fr_watch_both, columns=('Author','Status','Col'), height=14, yscrollcommand = self.scroll.set)
        self.scroll.config(orient = 'vertical', command = self.info_table.yview) #Подключение скроллбара
        self.info_table.column('#0', width=250, minwidth=250, anchor=tk.CENTER)
        self.info_table.column('Author', width=250, minwidth=250, anchor=tk.CENTER)
        self.info_table.column('Status', width=140, minwidth=140, anchor=tk.CENTER)
        self.info_table.column('Col', width=50, minwidth=50, anchor=tk.CENTER)

        self.info_table.heading("#0", command=lambda : sort_0(self.info_table, "#0", False))

        columns = self.info_table['columns']
        
        for col in columns:
            self.info_table.heading(col, text=col, command=lambda _col=col: \
                             sort(self.info_table, _col, False))

        self.info_table.heading('#0', text='Книга')
        self.info_table.heading('Author', text='Автор')
        self.info_table.heading('Status', text='Статус')
        self.info_table.heading('Col', text='Кол-во')

        self.info_table.pack(side='left')
        self.fr_watch_both.pack(side='bottom', fill='both')

        self.profile_menu = tk.Menu(self.info_table, tearoff=0)

        self.profile_menu.add_command(label = "Добавить книгу", command= lambda: add_book(self)) 
        self.profile_menu.add_command(label = "Изменить статус книги", command= lambda: edit_lc(self))
        self.profile_menu.add_command(label = "Удалить книгу", command = lambda: threading.Thread(target = delete_lc, args = [self,]).start())         
        
        self.bind('<KeyPress>', lambda event: event_handler_info(event, self))

        self.info_table.bind('<Button-3>', lambda event:self.profile_menu.post(event.x_root,event.y_root))
        self.iconbitmap(os.path.dirname(os.path.abspath(__file__))+"/profile.ico")

#---------------- Добавить книгу читателю ----------------

class Add_lc(tk.Toplevel):
    def __init__(self, *args, **kwargs):
        tk.Toplevel.__init__(self,*args, *kwargs)
        self.title("Добавить книгу в ЧБ") #Заголовок
        w = ((self.winfo_screenwidth() // 2) - 450) # ширина экрана
        h = ((self.winfo_screenheight() // 2) - 225) # высота экрана
        self.geometry('480x240+{}+{}'.format(w+300, h-125))#Размер
        self.resizable(False, False)#Изменение размера окна
        self.protocol("WM_DELETE_WINDOW", lambda: self_info_null(self))
        self.attributes("-topmost",True)

        
        self.focus_force()

        #надпись "Книга"
        self.bookname=ttk.Label(self,text='Книга', font= 'Arial 11')
        self.bookname.grid(row=0, column=0, ipady=3)

        #место ввода "Книга"
        self.en_bookname=ttk.Entry(self,width=49, font= 'Arial 11')
        self.en_bookname.grid_configure(row=0, column=1, columnspan=40, sticky='W')

        #надпись "Автор"
        self.lb_author2=ttk.Label(self,text='Автор', font= 'Arial 11')
        self.lb_author2.grid(row=1, column=0, ipady=3)

        #место ввода "Автор"
        self.en_author2=ttk.Entry(self,width=49, font= 'Arial 11')
        self.en_author2.grid_configure(row=1,column=1, columnspan=40, sticky='W')

        #надпись "кол-во"
        self.lb_col = ttk.Label(self,text='Кол-во', font= 'Arial 11')
        self.lb_col.grid(row=2, column=0, ipady=3)

        #место ввода "кол-во"
        self.en_col = ttk.Entry(self,width=10, font= 'Arial 11')
        self.en_col.grid_configure(row=2,column=1, columnspan=40, sticky='W')

        #кнопка "Сохранить"
        self.btn_save=ttk.Button(self, text='Сохранить', command=lambda: threading.Thread(target = save_lc2, args = [self,]).start())
        self.btn_save.grid(row=3, column=2, padx=219, pady=3)

        self.iconbitmap(os.path.dirname(os.path.abspath(__file__))+"/add.ico")

#---------------- Изменить книгу читателя ----------------

class Edit_lc(tk.Toplevel):
    def __init__(self, *args, **kwargs):
        tk.Toplevel.__init__(self,*args, *kwargs)
        self.title("Изменить книгу в ЧБ") #Заголовок
        w = ((self.winfo_screenwidth() // 2) - 450) # ширина экрана
        h = ((self.winfo_screenheight() // 2) - 225) # высота экрана
        self.geometry('480x240+{}+{}'.format(w+300, h-125))#Размер
        self.resizable(False, False)#Изменение размера окна
        self.protocol("WM_DELETE_WINDOW", lambda: self_info_null(self))
        self.attributes("-topmost",True)

        
        self.focus_force()

        #надпись "Книга"
        self.bookname=ttk.Label(self,text='Книга', font= 'Arial 11')
        self.bookname.grid(row=0, column=0)

        #место ввода "Книга"
        self.en_bookname=ttk.Entry(self,width=49, font= 'Arial 11')
        self.en_bookname.grid_configure(row=0, column=1, columnspan=50, pady=3, sticky='W')

        #надпись "Автор"
        self.lb_author2=ttk.Label(self,text='Автор', font= 'Arial 11')
        self.lb_author2.grid(row=1, column=0)

        #место ввода "Автор"
        self.en_author2=ttk.Entry(self,width=49, font= 'Arial 11')
        self.en_author2.grid_configure(row=1, column=1, columnspan=50, pady=3, sticky='W')

        #надпись "Дата сдачи"
        self.lb_dc = ttk.Label(self, text='Дата сдачи', font= 'Arial 11').grid(row=2, column=0)

        #место ввода "Дата сдачи"
        self.en_dc = DateEntry(self, width=12, background='darkblue',
                    foreground='white', borderwidth=2, font= 'Arial 11')
        self.en_dc.grid_configure(row=2, column=1, columnspan=15, pady=3, sticky='W')

        #надпись "Статус"
        self.lb_stat = ttk.Label(self, text='Статус', font= 'Arial 11').grid(row=3,column=0)

        #место ввода "Статус"
        self.en_stat = ttk.Combobox(self,values=['На руках','Просрочена','Сдана'],width=15, font= 'Arial 11')
        self.en_stat.grid_configure(row=3,column=1, columnspan=15, pady=3, sticky='W')

        #кнопка "Сохранить"
        self.btn_save=ttk.Button(self, text='Сохранить', command=lambda: threading.Thread(target = save_stat, args = [self,]).start())
        self.btn_save.grid(row=4, column=2, padx=220, pady=3)
        self.iconbitmap(os.path.dirname(os.path.abspath(__file__))+"/edit.ico")

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
        self.protocol("WM_DELETE_WINDOW", lambda: self_main_book_null(self))

        self.focus_force()
        
        
        #================================ Поиск ====================================
        self.frame_search1 = ttk.Frame(self)
        self.frame_search = ttk.Frame(self.frame_search1)

        self.search = Entry_Pl(self.frame_search, "Поиск")
        self.search.grid(row=0, column=0, padx=3, pady=3)
        
        self.bt_search = ttk.Button(self.frame_search, text='Найти', command = lambda: threading.Thread(target = search_book, args = [self,]).start())
        self.bt_search.grid(row=0, column=1, padx=3, pady=3)

        self.bt_cancel = ttk.Button(self.frame_search, text='Отмена', command = lambda: update_search(self))
        self.bt_cancel.grid(row=0, column=2, padx=3, pady=3)

        self.frame_search.pack()
        self.frame_search1.pack(fill='x')

        self.bind('<Return>', lambda event: search_b_enter(self))

        #================================  Таблица  ================================

        self.note = ttk.Notebook(self)

        #=========================== Учебники ===========================================
        self.fr_watch_both = tk.Canvas(self, background='#e9e9e9',width=900,height=450)

        def fixed_map(option):
            return [elm for elm in style.map('Treeview', query_opt=option)
                    if elm[:2] != ('!disabled', '!selected') and elm[0] != '!disabled !selected']

        style = ttk.Style()
        style.map('Treeview', foreground=fixed_map('foreground'), background=fixed_map('background'))

        # ttk.Style().configure("Treeview",fieldbackground="#e9e9e9")

        #Создание скроллбара
        self.scroll = ttk.Scrollbar(self.fr_watch_both)
        self.scroll.pack(side='right',fill='y')

        #Таблица
        self.book_table = MyTree(self.fr_watch_both, columns=('AUT','COL'), height=21, yscrollcommand = self.scroll.set)
        self.scroll.config(orient = 'vertical', command = self.book_table.yview) #Подключение скроллбара
        self.book_table.column('#0', minwidth = 230, width=230, anchor=tk.CENTER)
        self.book_table.column('AUT', minwidth = 230, width=230, anchor=tk.CENTER)
        self.book_table.column('COL', minwidth = 230, width=230, anchor=tk.CENTER)

        self.book_table.heading("#0", command=lambda : sort_0(self.book_table, "#0", False))

        columns = self.book_table['columns']
        
        for col in columns:
            self.book_table.heading(col, text=col, command=lambda _col=col: \
                             sort(self.book_table, _col, False))

        self.book_table.heading('#0', text='Название')
        self.book_table.heading('AUT', text='Автор(ы)')
        self.book_table.heading('COL', text='Кол-во')

        self.schbook_menu = tk.Menu(self.book_table, tearoff=0)

        self.schbook_menu.add_command(label = "Добавить книги", command= lambda: schbook(self))
        self.schbook_menu.add_command(label = "Изменить кол-во книг", command = lambda: edit_schbooks(self))
        self.schbook_menu.add_command(label = "Удалить книги", command = lambda: threading.Thread(target = del_schbook, args = [self,]).start())

        self.book_table.pack(side='left')
        self.book_table.bind('<Button-3>', lambda event:self.schbook_menu.post(event.x_root,event.y_root))
        self.fr_watch_both.pack(side='bottom', fill='both')

        threading.Thread(target = update_schbook, args = [self,]).start()

        #============================ Литература ======================================

        self.fr_lit = tk.Canvas(self, background='#e9e9e9',width=900,height=450)

        # ttk.Style().configure("Treeview",fieldbackground="#e9e9e9")

        #Создание скроллбара
        self.scroll1 = ttk.Scrollbar(self.fr_lit)
        self.scroll1.pack(side='right',fill='y')

        #Таблица
        self.book_table1 = MyTree(self.fr_lit, columns=('AUT','COL'), height=21, yscrollcommand = self.scroll1.set)
        self.scroll1.config(orient = 'vertical', command = self.book_table1.yview) #Подключение скроллбара
        self.book_table1.column('#0', minwidth = 230, width=230, anchor=tk.CENTER)
        self.book_table1.column('AUT', minwidth = 230, width=230, anchor=tk.CENTER)
        self.book_table1.column('COL', minwidth = 230, width=230, anchor=tk.CENTER)

        self.book_table1.heading("#0", command=lambda : sort_0(self.book_table1, "#0", False))

        columns = self.book_table1['columns']
        
        for col in columns:
            self.book_table1.heading(col, text=col, command=lambda _col=col: \
                             sort(self.book_table1, _col, False))

        self.book_table1.heading('#0', text='Название')
        self.book_table1.heading('AUT', text='Автор(ы)')
        self.book_table1.heading('COL', text='Кол-во')

        self.book_menu = tk.Menu(self.book_table1, tearoff=0)

        self.book_menu.add_command(label = "Добавить книги", command= lambda: lit(self))
        self.book_menu.add_command(label = "Изменить кол-во книг", command = lambda: edit_lit(self))
        self.book_menu.add_command(label = "Удалить книги", command = lambda: threading.Thread(target = del_book, args = [self,]).start())

        self.book_table1.pack(side='left')
        self.book_table1.bind('<Button-3>', lambda event:self.book_menu.post(event.x_root,event.y_root))
        self.fr_lit.pack(side='bottom', fill='both')

        threading.Thread(target = update_book, args = [self,]).start()

        self.note.add(self.fr_watch_both, text='Учебники')
        self.book_table.bind("<Double-Button-1>", lambda event: threading.Thread(target = schbook_info, args = [self,]).start())
        self.book_table1.bind("<Double-Button-1>", lambda event: threading.Thread(target = lit_info, args = [self,]).start())
        
        self.book_table.bind('<KeyPress>', lambda event: event_handler_schbook(event, self))
        self.book_table1.bind('<KeyPress>', lambda event: event_handler_lit(event, self))

        self.note.add(self.fr_lit, text='Литература')
        self.note.bind("<<NotebookTabChanged>>", lambda event: book_bind_add(self))
        self.note.pack(fill='both')

        self.iconbitmap(os.path.dirname(os.path.abspath(__file__))+"/books.ico")

#!---------------- Добавить книгу ----------------
class Add_book(tk.Toplevel):
    def __init__(self, *args, **kwargs):
        tk.Toplevel.__init__(self,*args, *kwargs)
        self.title("Добавить книги") #Заголовок
        w = ((self.winfo_screenwidth() // 2) - 450) # ширина экрана
        h = ((self.winfo_screenheight() // 2) - 225) # высота экрана
        self.geometry('360x200+{}+{}'.format(w+300, h-125))#Размер
        self.resizable(False, False)#Изменение размера окна
        self.protocol("WM_DELETE_WINDOW", lambda: self_book_null(self))
        self.attributes("-topmost",True)

        self.focus_force()

        


        self.lb_name = ttk.Label(self,text='Название', font= 'Arial 11')
        self.lb_aut = ttk.Label(self,text='Автор', font= 'Arial 11')
        self.lb_col = ttk.Label(self,text='Кол-во', font= 'Arial 11')
        #поле ввода "Название"
        self.en_name = ttk.Entry(self, width=35, font= 'Arial 11')
        #поле ввода "Автор"
        self.en_aut = ttk.Entry(self, width=35, font= 'Arial 11')
        #поле ввода "Кол-во"
        self.en_col = ttk.Entry(self, width=10, font= 'Arial 11')
        #
        #кнопка "Сохранить"
        self.save = ttk.Button(self,text='Сохранить', command = lambda: threading.Thread(target = save_book, args = [self,]).start())
        self.save_sch = ttk.Button(self, text='Сохранить', command = lambda: threading.Thread(target = save_schbook, args = [self,]).start())
        self.iconbitmap(os.path.dirname(os.path.abspath(__file__))+"/add.ico")

#!---------------- Изменить книгу ----------------
class Edit_books(tk.Toplevel):
    def __init__(self, *args, **kwargs):
        tk.Toplevel.__init__(self,*args, *kwargs)
        self.title("Редактировать книги") #Заголовок
        w = ((self.winfo_screenwidth() // 2) - 450) # ширина экрана
        h = ((self.winfo_screenheight() // 2) - 225) # высота экрана
        self.geometry('480x240+{}+{}'.format(w+300, h-125))#Размер
        self.resizable(False, False)#Изменение размера окна
        self.protocol("WM_DELETE_WINDOW", lambda: self_book_null(self))
        self.attributes("-topmost",True)

        self.focus_force()

        

        self.lb_name = ttk.Label(self,text='Название', font= 'Arial 11').grid(row=0,column=0)
        self.lb_aut = ttk.Label(self,text='Автор', font= 'Arial 11').grid(row=1,column=0)
        self.lb_col = ttk.Label(self,text='Кол-во', font= 'Arial 11').grid(row=2,column=0)
        #поле ввода "Название"
        self.en_name = ttk.Entry(self, width=35, font= 'Arial 11')
        self.en_name.grid_configure(row=0, column=1,columnspan=35, pady=3, sticky='W')
        #поле ввода "Автор"
        self.en_aut = ttk.Entry(self, width=35, font= 'Arial 11')
        self.en_aut.grid_configure(row=1, column=1,columnspan=35, pady=3, sticky='W')
        #поле ввода "Кол-во"
        self.en_col = ttk.Entry(self, width=10, font= 'Arial 11')
        self.en_col.grid_configure(row=2, column=1,columnspan=35, pady=3, sticky='W')
        #кнопка "Сохранить"
        self.save = ttk.Button(self,text='Сохранить', command = lambda: threading.Thread(target = edit_book, args = [self,]).start())
        self.save_sch = ttk.Button(self,text='Сохранить', command = lambda: threading.Thread(target = edit_schbook, args = [self,]).start())
        self.iconbitmap(os.path.dirname(os.path.abspath(__file__))+"/edit.ico")

class INFO_Book(tk.Toplevel):
    def __init__(self, *args, **kwargs):
        tk.Toplevel.__init__(self,*args, *kwargs)
        self.title("Добавить книги") #Заголовок
        w = ((self.winfo_screenwidth() // 2) - 450) # ширина экрана
        h = ((self.winfo_screenheight() // 2) - 225) # высота экрана
        self.geometry('830x450+{}+{}'.format(w+300, h-125))#Размер
        self.resizable(False, False)#Изменение размера окна
        self.protocol("WM_DELETE_WINDOW", lambda: self_book_inf_null(self))

        self.focus_force()

        

        #============================= Контейнер информации =================

        self.fr_info = ttk.Frame(self)

        self.fr_info.pack(side='top', fill='x')

        #================================ Таблица ===========================

        self.frame = ttk.Frame(self)

        self.scroll = ttk.Scrollbar(self.frame)
        self.scroll.pack(side='right',fill='y')

        self.table = MyTree(self.frame, columns=('DB','PHONE','DI','DC','STAT','COL'), height=21, yscrollcommand = self.scroll.set)
        self.scroll.config(orient = 'vertical', command = self.table.yview) #Подключение скроллбара
        self.table.column('#0', minwidth = 160, width=160, anchor=tk.CENTER)
        self.table.column('DB', minwidth = 100, width=100, anchor=tk.CENTER)
        self.table.column('PHONE', minwidth = 150, width=150, anchor=tk.CENTER)
        self.table.column('DI', minwidth = 100, width=100, anchor=tk.CENTER)
        self.table.column('DC', minwidth = 100, width=100, anchor=tk.CENTER)
        self.table.column('STAT', minwidth = 150, width=150, anchor=tk.CENTER)
        self.table.column('COL', minwidth = 50, width=50, anchor=tk.CENTER)

        self.table.heading("#0", command=lambda : sort_0(self.table, "#0", False))

        columns = self.table['columns']
        
        for col in columns:
            self.table.heading(col, text=col, command=lambda _col=col: \
                             sort(self.table, _col, False))

        self.table.heading('#0', text='ФИО')
        self.table.heading('DB', text='Дата рождения')
        self.table.heading('PHONE', text='Телефон')
        self.table.heading('DI', text='Дата взятия')
        self.table.heading('DC', text='Дата сдачи')
        self.table.heading('STAT', text='Статус')
        self.table.heading('COL', text='Кол-во')

        self.table.pack(side='left', fill='both')
        self.iconbitmap(os.path.dirname(os.path.abspath(__file__))+"/book.ico")
        

#================================ Уведомления ================================
class Not(tk.Toplevel):
      def __init__(self,*args, **kwargs):
        tk.Toplevel.__init__(self,*args, *kwargs)
        self.title("Электронный читательский билет - Уведомления")#Заголовок
        self.geometry("770x450+0+0")#Размер окна
        self.resizable(False,False)#Изменение размера окна
        self.configure(background='#e9e9e9')#Фон окна
        self.focus_force()
        self.protocol("WM_DELETE_WINDOW", lambda: self_not_close(self))
        self.attributes("-topmost",True)

        #Контейнер уведомлений
        self.fr_watch_both = ttk.Frame(self)
        self.fr_watch_both.configure(width=750,height=456)
        self.fr_watch_both.pack(side='left',fill='both')

        #Создание скроллбара
        self.scroll = ttk.Scrollbar(self.fr_watch_both)
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
        self.geometry('480x240+{}+{}'.format(w+300, h))
        self.resizable(False,False)#Изменение размера окна
        self.configure(background='#e9e9e9')#Фон окна
        self.focus_force()

        self.lb_excel = ttk.Label(self, text='Вывести отчёт в Excel', font= 'Arial 11')
        self.lb_excel.pack()

        self.frame = ttk.Frame(self)
        self.lb_date1 = ttk.Label(self.frame, text='С:', font= 'Arial 11')
        self.lb_date1.grid(row=0, column=0)

        self.en_date1 = DateEntry(self.frame, width=12, background='blue',
                    foreground='white', borderwidth=2, font= 'Arial 11')
        self.en_date1.grid_configure(row=0, column=1, pady=3)

        self.lb_date2 = ttk.Label(self.frame, text='До:', font= 'Arial 11')
        self.lb_date2.grid(row=1,column=0)

        self.en_date2 = DateEntry(self.frame, width=12, background='darkblue',
                    foreground='white', borderwidth=2, font= 'Arial 11')
        self.en_date2.grid_configure(row=1,column=1, pady=3)

        self.btn = ttk.Button(self.frame, text='Сохранить отчёт', command= lambda: threading.Thread(target = lub_period_excel, args = [self,]).start())
        self.btn.grid(row=2, column=1, pady=3)


        self.frame.pack(fill='both')


class Spravka(tk.Toplevel):

    def __init__(self, *args, **kwargs):
        tk.Toplevel.__init__(self,*args, *kwargs)
        self.title("Справка") #Заголовок
        w = ((self.winfo_screenwidth() // 2) - 450) # ширина экрана
        h = ((self.winfo_screenheight() // 2) - 225) # высота экрана
        self.geometry('713x450+{}+{}'.format(w-100, h-150))#Размер
        self.resizable(False, False)#Изменение размера окна
        self.protocol("WM_DELETE_WINDOW", lambda: self_main_book_null(self))

        self.focus_force()
        
        

        file = open(os.path.dirname(os.path.abspath(__file__))+"/spravka.txt", 'r')
        row=0
        for line in file:
            ttk.Label(self, text=line, font= 'Arial 11').grid(row=row, column=0)
            row+=1

        #Иконка
        self.iconbitmap(os.path.dirname(os.path.abspath(__file__))+"/ask.ico")


class Information(tk.Toplevel):

    def __init__(self, *args, **kwargs):
        tk.Toplevel.__init__(self,*args, *kwargs)
        self.title("Информация") #Заголовок
        w = ((self.winfo_screenwidth() // 2) - 450) # ширина экрана
        h = ((self.winfo_screenheight() // 2) - 225) # высота экрана
        self.geometry('713x450+{}+{}'.format(w-100, h-150))#Размер
        self.resizable(False, False)#Изменение размера окна
        self.protocol("WM_DELETE_WINDOW", lambda: self_main_inf_null(self))

        self.focus_force()
        
        

        file = open(os.path.dirname(os.path.abspath(__file__))+"/information.txt", 'r')
        row=0
        for line in file:
            ttk.Label(self, text=line, font= 'Arial 11').grid(row=row, column=0)
            row+=1

        #Иконка
        self.iconbitmap(os.path.dirname(os.path.abspath(__file__))+"/ask.ico")
        global easter_egg
        if easter_egg == 3:
            threading.Thread(target = easter4, args = [self,]).start()


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

def update_schbook(self):
    global obj
    self.book_table.delete(*self.book_table.get_children())
    conn = sqlite3.connect(os.path.dirname(os.path.abspath(__file__))+"/LC.db")
    cur = conn.cursor()

    for less in obj:
        x = self.book_table.insert('', tk.END, text=less)
        cur.execute("SELECT NAME, AUT, COL FROM SCHBOOK WHERE OBJ = (?)",(less,))
        rows = cur.fetchall()
        for row in rows:
            cur.execute("SELECT COL FROM LC WHERE BOOK = (?) AND AUT = (?) AND (STAT = 'На руках' OR STAT = 'Просрочена')",(row[0],row[1]))
            line = cur.fetchall()
            if line != []:
                res = (row[0], row[1], row[2] - line[0][0])
                self.book_table.insert(x, tk.END, text = res[0], values=res[1:])
            else:
                self.book_table.insert(x, tk.END, text = row[0], values=row[1:])

def update_book(self):
    self.book_table1.delete(*self.book_table1.get_children())
    conn = sqlite3.connect(os.path.dirname(os.path.abspath(__file__))+"/LC.db")
    cur = conn.cursor()

    #Вывовд всех учеников
    cur.execute("SELECT * FROM BOOK")
    rows = cur.fetchall()
    for row in rows:
        cur.execute("SELECT COUNT(*) FROM LC WHERE BOOK = (?) AND AUT = (?) AND (STAT = 'На руках' OR STAT = 'Просрочена')",(row[0],row[1]))
        line = cur.fetchall()
        if line != []:
            res = (row[0], row[1], row[2] - line[0][0])
            self.book_table1.insert('', tk.END, text = res[0], values=res[1:])
        else:
            self.book_table1.insert('', tk.END, text = row[0], values=row[1:])

def update_search(self):
    threading.Thread(target = update_book, args = [self,]).start()
    threading.Thread(target = update_schbook, args = [self,]).start()
    
    
def update_info(root):
    conn = sqlite3.connect(os.path.dirname(os.path.abspath(__file__))+"/LC.db")
    cur = conn.cursor()

    root.fio = ttk.Label(root.frame,text= text, font='Arial 15').pack()
    root.db = ttk.Label(root.frame,text="Дата рождения: " + values[0], font='Arial 12').pack()
    if (values[1] == '') and (values[2] == ''):
        root.adr = ttk.Label(root.frame, text='Адрес: '+values[3], font='Arial 12').pack()
        root.phone = ttk.Label(root.frame,text='Телефон: '+values[4], font='Arial 12').pack()
    else:
        root.clas = ttk.Label(root.frame, text='Класс: '+values[1]+' '+values[2], font='Arial 12').pack()
        root.adr = ttk.Label(root.frame, text='Адрес: '+values[3], font='Arial 12').pack()
        root.phone = ttk.Label(root.frame,text='Телефон: '+values[4], font='Arial 12').pack()
    
    db = datetime.datetime.strptime(values[0], '%d.%m.%Y')#Парсит дату
    db = db.strftime('%Y-%m-%d')#Переводит дату в другой формат
    #Вывовд всех учеников
    cur.execute("SELECT BOOK, AUT, STAT, COL FROM LC WHERE FIO=(?) AND DB=(?) AND PHONE=(?)",(text,db,values[4]))
    rows = cur.fetchall()
    for row in rows:
        root.info_table.insert('', tk.END, text=row[0], values=row[1:])

    root.title("Профиль: {}".format(text)) #Заголовок
    root.fr_watch_both.pack(side='bottom', fill='both')

        

def info(self):
    global self_main
    global text
    global values
    selected_item = self.table.selection()
    # Получаем значения в выделенной строке
    values = self.table.item(selected_item, option="values")
    text = self.table.item(selected_item, option="text")
    if self_main == 'close':
        if text != '':
            self_main = self
            root = INFO()
            threading.Thread(target = update_info, args = [root,]).start()
    

def add_profile(self):
    global self_main
    if self_main == 'close':
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
    dreg = datetime.date.today()
    line = [fio,db,clas,lit,adr,phone,client,dreg]
    if null in (fio,db,phone,adr):   #Проверка на пустоту полей
        messagebox.showerror('ОШИБКА!!!','Ошибка! Поля не могут быть пустыми!', parent=self)  #Вывод ошибки
    else:
        conn = sqlite3.connect(os.path.dirname(os.path.abspath(__file__))+"/LC.db")    #Занесение данных в базу данных
        con_cur = conn.cursor()
        con_cur.execute('INSERT INTO PROFILE VALUES (?,?,?,?,?,?,?,?)',line)
        conn.commit()

    messagebox.showinfo('Успех!','Данные сохранены!', parent=self)

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
    if self_main == 'close':
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
        messagebox.showerror('ОШИБКА!!!','Ошибка! Поля не могут быть пустыми!',parent=self)  #Вывод ошибки
        self.focus_force()
    else:
        conn = sqlite3.connect(os.path.dirname(os.path.abspath(__file__))+"/LC.db")    #Занесение данных в базу данных
        con_cur = conn.cursor()
        con_cur.execute('UPDATE PROFILE SET FIO = (?), DB = (?), CLA = (?), LIT = (?), ADR = (?), PHONE = (?) WHERE FIO = (?) AND DB = (?) AND PHONE = (?)',line)
        conn.commit()

    messagebox.showinfo('Успех!','Данные сохранены!', parent=self)

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
    ask = messagebox.askyesno('Удалить','Вы точно хотите удалить читателя {}?'.format(text), parent=self)
    if ask == True:
        self.focus_force()
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
    if self_info == 'close':
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
    col = self.en_col.get()
    if col == '':
        col = 1
    line = [fio,db,phone,di,dc,aut,book,stat,col]
    if null in (book,aut,col):   #Проверка на пустоту полей
        messagebox.showerror('ОШИБКА!!!','Ошибка! Поля не могут быть пустыми!',parent=self)  #Вывод ошибки
    else:
        conn = sqlite3.connect(os.path.dirname(os.path.abspath(__file__))+"/LC.db")    #Занесение данных в базу данных
        con_cur = conn.cursor()
        con_cur.execute('INSERT INTO LC VALUES (?,?,?,?,?,?,?,?,?)',line)
        conn.commit()

    messagebox.showinfo('Успех!','Данные сохранены!', parent=self)

    #Обновление таблицы при нажатии на кнопку никак не хочет работать потому сделал как коммент
    self_info.info_table.delete(*self_info.info_table.get_children())
    conn = sqlite3.connect(os.path.dirname(os.path.abspath(__file__))+"/LC.db")
    cur = conn.cursor()

    #Вывовд всех учеников
    cur.execute("SELECT BOOK, AUT, STAT, COL FROM LC WHERE FIO=(?) AND DB=(?) AND PHONE=(?)",(fio,db,phone))
    rows = cur.fetchall()
    for row in rows:
        self_info.info_table.insert("" , tk.END , text=row[0], values=row[1:])

def edit_lc(self):
    global self_info
    global text
    global values
    if self_info == 'close':
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
    line = (name, aut, stat, dc, text, db, values[4], text1, values1[0], values1[1], values1[2])
    if null in (name, aut, stat):   #Проверка на пустоту полей
        messagebox.showerror('ОШИБКА!!!','Ошибка! Поля не могут быть пустыми!', parent=self)  #Вывод ошибки
    else:
        conn = sqlite3.connect(os.path.dirname(os.path.abspath(__file__))+"/LC.db")    #Занесение данных в базу данных
        con_cur = conn.cursor()
        con_cur.execute('UPDATE LC SET BOOK=(?), AUT=(?), STAT=(?), DC=(?) WHERE FIO=(?) AND DB=(?) AND PHONE=(?) AND BOOK=(?) AND AUT=(?) AND STAT=(?) AND COL=(?)',line)
        conn.commit()

    messagebox.showinfo('Успех!','Данные сохранены!', parent=self)

    self_info.info_table.delete(*self_info.info_table.get_children())
    conn = sqlite3.connect(os.path.dirname(os.path.abspath(__file__))+"/LC.db")
    cur = conn.cursor()

    db = datetime.datetime.strptime(values[0],'%d.%m.%Y')
    db = db.strftime('%Y-%m-%d')
    #Вывовд всех учеников
    cur.execute("SELECT BOOK, AUT, STAT, COL FROM LC WHERE FIO=(?) AND DB=(?) AND PHONE=(?)",(text,db,values[4]))
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
    ask = messagebox.askyesno('Удалить','Вы точно хотите удалить книгу: {}?'.format(text1), parent=self)

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
    cur.execute("SELECT BOOK, AUT, STAT, COL FROM LC WHERE FIO=(?) AND DB=(?) AND PHONE=(?)",(text,db,values[4]))
    rows = cur.fetchall()
    for row in rows:
        self.info_table.insert("" , tk.END , text=row[0], values=row[1:])


def search(self):
    search = self.search.get()
    if search != 'Поиск':
        self.table.delete(*self.table.get_children())
        if len(search) > 1:
            search = search.lower().title()
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
    self.book_table1.delete(*self.book_table1.get_children())
    search = self.search.get()
    if search[0]!='"':
        if len(search) > 1:
            search = search.lower().title()
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
        self.book_table1.insert("" , tk.END ,text=res[0], values=res[1:])
    cur.execute("SELECT * FROM SCHBOOK WHERE (NAME LIKE '%{0}%' OR '{0}%' OR '%{0}') OR (AUT LIKE '%{0}%' OR '{0}%' OR '%{0}')".format(search))
    rows = cur.fetchall()
    for row in rows:
        cur.execute("SELECT COUNT(*) FROM LC WHERE BOOK = (?) AND AUT = (?) AND (STAT = 'На руках' OR STAT = 'Просрочена')",(row[0],row[1]))
        line = cur.fetchall()
        res = (row[0], row[1], row[2] - line[0][0])
        self.book_table.insert("" , tk.END ,text=res[0], values=res[1:])


def search_enter(self):
    if self.search.get() != 'Поиск':
        threading.Thread(target = search, args = [self,]).start()
    else:
        threading.Thread(target = update_main, args = [self,]).start()

def search_b_enter(self):
    if self.search.get() != 'Поиск':
        threading.Thread(target = search_book, args = [self,]).start()
    else:
        threading.Thread(target = update_search, args = [self,]).start()




def book(self):
    global self_book
    if self_book == 'close':
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
        messagebox.showerror('ОШИБКА!!!','Ошибка! Поля не могут быть пустыми!', parent=self)  #Вывод ошибки
    else:
        conn = sqlite3.connect(os.path.dirname(os.path.abspath(__file__))+"/LC.db")    #Занесение данных в базу данных
        con_cur = conn.cursor()
        con_cur.execute('INSERT INTO BOOK VALUES (?,?,?)',line)
        conn.commit()

    messagebox.showinfo('Успех!','Данные сохранены!', parent=self)

    self_book.book_table1.delete(*self_book.book_table1.get_children())
    conn = sqlite3.connect(os.path.dirname(os.path.abspath(__file__))+"/LC.db")
    cur = conn.cursor()

    #Вывовд всех учеников
    cur.execute("SELECT * FROM BOOK")
    rows = cur.fetchall()
    for row in rows:
        cur.execute("SELECT COUNT(*) FROM LC WHERE BOOK = (?) AND AUT = (?) AND (STAT = 'На руках' OR STAT = 'Просрочена')",(row[0],row[1]))
        line = cur.fetchall()
        res = (row[0], row[1], row[2] - line[0][0])
        self_book.book_table1.insert("" , tk.END ,text=res[0], values=res[1:])

def edit_lit(self):
    global self_book
    if self_book == 'close':
        self_book = self
        root = Edit_books()
        selected_item = self_book.book_table1.selection()
        # Получаем значения в выделенной строке
        values1 = self_book.book_table1.item(selected_item, option="values")
        text1 = self_book.book_table1.item(selected_item, option="text")
        conn = sqlite3.connect(os.path.dirname(os.path.abspath(__file__))+"/LC.db")    #Занесение данных в базу данных
        con_cur = conn.cursor()
        line = (text1,values1[0])
        con_cur.execute('SELECT COL FROM BOOK WHERE NAME=(?) AND AUT=(?)',line)
        col = con_cur.fetchall()
        root.en_name.insert(0, text1)
        root.en_aut.insert(0, values1[0])
        root.en_col.insert(0, col)
        root.save.grid(row=3, column=1,pady=3, padx=134)

def edit_schbooks(self):
    global self_book
    if self_book == 'close':
        self_book = self
        root = Edit_books()
        selected_item = self_book.book_table.selection()
        # Получаем значения в выделенной строке
        values1 = self_book.book_table.item(selected_item, option="values")
        text1 = self_book.book_table.item(selected_item, option="text")
        conn = sqlite3.connect(os.path.dirname(os.path.abspath(__file__))+"/LC.db")    #Занесение данных в базу данных
        con_cur = conn.cursor()
        line = (text1,values1[0])
        con_cur.execute('SELECT COL FROM SCHBOOK WHERE NAME=(?) AND AUT=(?)',line)
        col = con_cur.fetchall()
        root.en_name.insert(0, text1)
        root.en_aut.insert(0, values1[0])
        root.en_col.insert(0, col)
        root.save_sch.grid(row=3, column=1,pady=3, padx=134)
    

def edit_book(self):
    global self_book
    selected_item = self_book.book_table1.selection()
    # Получаем значения в выделенной строке
    values1 = self_book.book_table1.item(selected_item, option="values")
    text1 = self_book.book_table1.item(selected_item, option="text")

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
        messagebox.showerror('ОШИБКА!!!','Ошибка! Поля не могут быть пустыми!', parent=self)  #Вывод ошибки
    else:
        con_cur = conn.cursor()
        con_cur.execute('UPDATE BOOK SET NAME=(?), AUT=(?), COL=(?) WHERE NAME=(?) AND AUT=(?) AND COL=(?)',line)
        conn.commit()

    messagebox.showinfo('Успех!','Данные сохранены!', parent=self)

    self_book.book_table1.delete(*self_book.book_table1.get_children())
    conn = sqlite3.connect(os.path.dirname(os.path.abspath(__file__))+"/LC.db")
    cur = conn.cursor()

    #Вывовд всех учеников
    cur.execute("SELECT * FROM BOOK")
    rows = cur.fetchall()
    for row in rows:
        cur.execute("SELECT COUNT(*) FROM LC WHERE BOOK = (?) AND AUT = (?) AND (STAT = 'На руках' OR STAT = 'Просрочена')",(row[0],row[1]))
        line = cur.fetchall()
        if line != []:
            res = (row[0], row[1], row[2] - line[0][0])
            self_book.book_table1.insert('', tk.END, text = res[0], values=res[1:])
        else:
            self_book.book_table1.insert('', tk.END, text = row[0], values=row[1:])

def edit_schbook(self):
    global self_book
    selected_item = self_book.book_table.selection()
    # Получаем значения в выделенной строке
    values1 = self_book.book_table.item(selected_item, option="values")
    text1 = self_book.book_table.item(selected_item, option="text")

    conn = sqlite3.connect(os.path.dirname(os.path.abspath(__file__))+"/LC.db")    #Занесение данных в базу данных
    con_cur = conn.cursor()

    con_cur.execute('SELECT COL FROM SCHBOOK WHERE NAME = (?) AND AUT = (?)',(text1, values1[0]))
    f = con_cur.fetchall()
    null = ''
    name = self.en_name.get()
    aut = self.en_aut.get()
    col = self.en_col.get()
    line = (name,aut,col, text1, values1[0], f[0][0])
    if null in (name,aut,col):   #Проверка на пустоту полей
        messagebox.showerror('ОШИБКА!!!','Ошибка! Поля не могут быть пустыми!', parent=self)  #Вывод ошибки
    else:
        con_cur = conn.cursor()
        con_cur.execute('UPDATE SCHBOOK SET NAME=(?), AUT=(?), COL=(?) WHERE NAME=(?) AND AUT=(?) AND COL=(?)',line)
        conn.commit()

    messagebox.showinfo('Успех!','Данные сохранены!', parent=self)

    self_book.book_table.delete(*self_book.book_table.get_children())
    conn = sqlite3.connect(os.path.dirname(os.path.abspath(__file__))+"/LC.db")
    cur = conn.cursor()

    #Вывовд всех учеников
    for less in obj:
        x = self_book.book_table.insert('', tk.END, text=less)
        cur.execute("SELECT NAME, AUT, COL FROM SCHBOOK WHERE OBJ = (?)",(less,))
        rows = cur.fetchall()
        for row in rows:
            cur.execute("SELECT COL FROM LC WHERE BOOK = (?) AND AUT = (?) AND (STAT = 'На руках' OR STAT = 'Просрочена')",(row[0],row[1]))
            line = cur.fetchall()
            if line != []:
                res = (row[0], row[1], row[2] - line[0][0])
                self_book.book_table.insert(x, tk.END, text = res[0], values=res[1:])
            else:
                self_book.book_table.insert(x, tk.END, text = row[0], values=row[1:])

def del_book(self):
    selected_item = self.book_table1.selection()
    # Получаем значения в выделенной строке
    values1 = self.book_table1.item(selected_item, option="values")
    text1 = self.book_table1.item(selected_item, option="text")
    ask = messagebox.askyesno('Удалить','Вы точно хотите удалить книгу: {}?'.format(text1), parent=self)

    conn = sqlite3.connect(os.path.dirname(os.path.abspath(__file__))+"/LC.db")    #Занесение данных в базу данных
    con_cur = conn.cursor()

    if ask == True:
        line = (text1, values1[0], values1[1])
        con_cur.execute('DELETE FROM BOOK WHERE NAME = (?) AND AUT = (?) AND COL = (?)',line)
        conn.commit()

    self.book_table1.delete(*self.book_table1.get_children())
    conn = sqlite3.connect(os.path.dirname(os.path.abspath(__file__))+"/LC.db")
    cur = conn.cursor()

    #Вывовд всех учеников
    cur.execute("SELECT * FROM BOOK")
    rows = cur.fetchall()
    for row in rows:
        cur.execute("SELECT COUNT(*) FROM LC WHERE BOOK = (?) AND AUT = (?) AND (STAT = 'На руках' OR STAT = 'Просрочена')",(row[0],row[1]))
        line = cur.fetchall()
        if line != []:
            res = (row[0], row[1], row[2] - line[0][0])
            self.book_table1.insert('', tk.END, text = res[0], values=res[1:])
        else:
            self.book_table1.insert('', tk.END, text = row[0], values=row[1:])


def del_schbook(self):
    selected_item = self.book_table.selection()
    # Получаем значения в выделенной строке
    values1 = self.book_table.item(selected_item, option="values")
    text1 = self.book_table.item(selected_item, option="text")
    ask = messagebox.askyesno('Удалить','Вы точно хотите удалить книгу: {}?'.format(text1), parent=self)

    conn = sqlite3.connect(os.path.dirname(os.path.abspath(__file__))+"/LC.db")    #Занесение данных в базу данных
    con_cur = conn.cursor()

    if ask == True:
        line = (text1, values1[0], values1[1]) 
        con_cur.execute('DELETE FROM SCHBOOK WHERE NAME = (?) AND AUT = (?) AND COL = (?)',line)
        conn.commit()

    self.book_table.delete(*self.book_table.get_children())
    conn = sqlite3.connect(os.path.dirname(os.path.abspath(__file__))+"/LC.db")
    cur = conn.cursor()

    #Вывовд всех учеников
    for less in obj:
        x = self.book_table.insert('', tk.END, text=less)
        cur.execute("SELECT NAME, AUT, COL FROM SCHBOOK WHERE OBJ = (?)",(less,))
        rows = cur.fetchall()
        for row in rows:
            cur.execute("SELECT COL FROM LC WHERE BOOK = (?) AND AUT = (?) AND (STAT = 'На руках' OR STAT = 'Просрочена')",(row[0],row[1]))
            line = cur.fetchall()
            if line != []:
                res = (row[0], row[1], row[2] - line[0][0])
                self.book_table.insert(x, tk.END, text = res[0], values=res[1:])
            else:
                self.book_table.insert(x, tk.END, text = row[0], values=row[1:])

def save_schbook(self):
    global self_book
    null = ''
    name = self.en_name.get()
    aut = self.en_aut.get()
    col = self.en_col.get()
    less = self.en_less.get()
    line = (name,aut,col,less)
    if null in (name,aut,col):   #Проверка на пустоту полей
        messagebox.showerror('ОШИБКА!!!','Ошибка! Поля не могут быть пустыми!', parent=self)  #Вывод ошибки
    else:
        conn = sqlite3.connect(os.path.dirname(os.path.abspath(__file__))+"/LC.db")    #Занесение данных в базу данных
        con_cur = conn.cursor()
        con_cur.execute('INSERT INTO SCHBOOK VALUES (?,?,?,?)',line)
        conn.commit()

    messagebox.showinfo('Успех!','Данные сохранены!', parent=self)

    self_book.book_table.delete(*self_book.book_table.get_children())
    conn = sqlite3.connect(os.path.dirname(os.path.abspath(__file__))+"/LC.db")
    cur = conn.cursor()

    #Вывовд всех учеников
    for less in obj:
        x = self_book.book_table.insert('', tk.END, text=less)
        cur.execute("SELECT NAME, AUT, COL FROM SCHBOOK WHERE OBJ = (?)",(less,))
        rows = cur.fetchall()
        for row in rows:
            cur.execute("SELECT COL FROM LC WHERE BOOK = (?) AND AUT = (?) AND (STAT = 'На руках' OR STAT = 'Просрочена')",(row[0],row[1]))
            line = cur.fetchall()
            if line != []:
                res = (row[0], row[1], row[2] - line[0][0])
                self_book.book_table.insert(x, tk.END, text = res[0], values=res[1:])
            else:
                self_book.book_table.insert(x, tk.END, text = row[0], values=row[1:])
    
    
def schbook(self):
    global obj
    global self_book
    self_book = self
    self = Add_book()
    w = ((self.winfo_screenwidth() // 2) - 450) # ширина экрана
    h = ((self.winfo_screenheight() // 2) - 225) # высота экрана
    self.geometry('360x200+{}+{}'.format(w+300, h-125))#Размер
    self.lb_name.grid(row=0,column=0)
    self.lb_aut.grid(row=1,column=0)
    self.lb_col.grid(row=2,column=0)
    self.en_name.grid_configure(row=0, column=1,columnspan=35, pady=3, sticky='W')
    self.en_aut.grid_configure(row=1, column=1,columnspan=35, pady=3, sticky='W')
    self.en_col.grid_configure(row=2, column=1,columnspan=35, pady=3, sticky='W')
    self.lb_less = ttk.Label(self, text='Урок', font= 'Arial 11').grid(row=3,column=0)
    self.en_less = ttk.Combobox(self,values=obj,width=17, font= 'Arial 11')
    self.en_less.grid_configure(row=3, column=1, columnspan=35, pady=3, sticky='W')
    self.save_sch.grid(row=4, column=1,pady=3, padx=134)

def lit(self):
    global self_book
    self_book = self
    self = Add_book()
    self.lb_name.grid(row=0,column=0)
    self.lb_aut.grid(row=1,column=0)
    self.lb_col.grid(row=2,column=0)
    self.en_name.grid_configure(row=0, column=1,columnspan=35, pady=3, sticky='W')
    self.en_aut.grid_configure(row=1, column=1,columnspan=35, pady=3, sticky='W')
    self.en_col.grid_configure(row=2, column=1,columnspan=35, pady=3, sticky='W')
    self.save.grid(row=3, column=1,pady=3, padx=134)

def self_main_null(self):
    global self_main
    self_main = 'close'
    self.destroy()

def self_info_null(self):
    global self_info
    self_info = 'close'
    self.destroy()

def self_book_null(self):
    global self_book
    self_book = 'close'
    self.destroy()

def self_book_inf_null(self):
    global self_book_info
    self_book_info = 'close'
    self.destroy()

def self_main_book_null(self):
    global book_add
    global self_main_book
    self_main_book = 'close'
    book_add = 0
    self.destroy()

def self_main_inf_null(self):
    global book_add
    global self_main_book
    self_main_book = 'close'
    book_add = 0
    self.destroy()

def music_stop():
    pyglet.app.exit()

def self_book_open(self):
    global self_main_book
    if self_main_book == 'close':
        self_main_book = self
        Book()

def self_not_open(self):
    global self_main_not
    if self_main_not == 'close':
        self_main_not = self
        Not()

def self_not_close(self):
    global self_main_not
    self_main_not = 'close'
    self.destroy()

def book_bind_add(self):
    global book_add
    if book_add == 0:
        self.bind('<KeyPress>', lambda event: event_handler_schbook_a(event, self))
        book_add = 1
    elif book_add == 1:
        self.bind('<KeyPress>', lambda event: event_handler_lit_a(event, self))
        book_add = 0

def schbook_info(self):
    global self_book_info
    if self_book_info == 'close':
        self_book_info = self
        selected_item = self.book_table.selection()
        # Получаем значения в выделенной строке
        values = self.book_table.item(selected_item, option="values")
        text = self.book_table.item(selected_item, option="text")

        conn = sqlite3.connect(os.path.dirname(os.path.abspath(__file__))+"/LC.db") 
        cur = conn.cursor()
        cur.execute("SELECT * FROM SCHBOOK WHERE NAME = (?) AND AUT =(?)",(text,values[0]))
        info = cur.fetchall()


        root = INFO_Book()

        root.aut = ttk.Label(root.fr_info, text=info[0][1], font= 'Arial 11')
        root.aut.pack()
        root.name = ttk.Label(root.fr_info, text=info[0][0], font= 'Arial 11')
        root.name.pack()
        root.col_v = ttk.Label(root.fr_info, text='Всего: '+str(info[0][2]), font= 'Arial 11')
        root.col_v.pack()
        root.col_ost = ttk.Label(root.fr_info, text='Осталось: '+str(values[1]), font= 'Arial 11')
        root.col_ost.pack()
        root.obj = ttk.Label(root.fr_info, text='Предмет: '+info[0][3], font= 'Arial 11')
        root.obj.pack()
        root.frame.pack(side='bottom', fill='both')

        cur.execute("SELECT FIO, DB, PHONE, DI, DC, STAT, COL FROM LC WHERE BOOK =(?) AND AUT=(?)",(text,values[0]))
        rows = cur.fetchall()
        for row in rows:
            root.table.insert('', tk.END, text=row[0], values=row[1:])


def lit_info(self):
    global self_book_info
    if self_book_info == 'close':
        self_book_info = self
        selected_item = self.book_table1.selection()
        # Получаем значения в выделенной строке
        values = self.book_table1.item(selected_item, option="values")
        text = self.book_table1.item(selected_item, option="text")
    
        conn = sqlite3.connect(os.path.dirname(os.path.abspath(__file__))+"/LC.db") 
        cur = conn.cursor()
        cur.execute("SELECT * FROM BOOK WHERE NAME = (?) AND AUT =(?)",(text,values[0]))
        info = cur.fetchall()


        root = INFO_Book()

        root.aut = ttk.Label(root.fr_info, text=info[0][1], font= 'Arial 11')
        root.aut.pack()
        root.name = ttk.Label(root.fr_info, text=info[0][0], font= 'Arial 11')
        root.name.pack()
        root.col_v = ttk.Label(root.fr_info, text='Всего: '+str(info[0][2]), font= 'Arial 11')
        root.col_v.pack()
        root.col_ost = ttk.Label(root.fr_info, text='Осталось: '+str(values[1]), font= 'Arial 11')
        root.col_ost.pack()
        root.frame.pack(side='bottom', fill='both')

        cur.execute("SELECT FIO, DB, PHONE, DI, DC, STAT, COL FROM LC WHERE BOOK =(?) AND AUT=(?)",(text,values[0]))
        rows = cur.fetchall()
        for row in rows:
            root.table.insert('', tk.END, text=row[0], values=row[1:])

#================================ Сортировка ==================================
def sort(tv, col, reverse):
    global prev_column

    if prev_column == col:
        # Если предыдущая колонка та же что и сечас, то меняем направление сортировки
        reverse = not reverse
    else:
        # Если была другая колонка, то делаем прямую сортировку
        reverse = False

    prev_column = col

    l = [(tv.set(k, col), k) for k in tv.get_children()]
    l.sort(reverse=reverse)

    for index, (val, k) in enumerate(l):
        tv.move(k, '', index)

    tv.heading(col, command=lambda: sort(tv, col, reverse))


def sort_0(tv, col, reverse):
    global prev_column

    if prev_column == col:
        reverse = not reverse
    else:
        reverse = False

    prev_column = col

    l = [(tv.item(k)["text"], k) for k in tv.get_children()] #Display column #0 cannot be set
    l.sort(key=lambda t: t[0], reverse=reverse)

    for index, (val, k) in enumerate(l):
        tv.move(k, '', index)

    tv.heading(col, command=lambda: sort_0(tv, col, reverse))

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
    y = datetime.datetime.strptime(y, '%Y-%m-%d')
    y = y.strftime('%d_%m_%Y')
    ask = fd.asksaveasfilename(filetypes = (('Excel', '*.xlsx'),), defaultextension=".xlsx")
    if ask != '':
        workbook = xlsxwriter.Workbook(ask)
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
        worksheet.write('I1','Кол-во', bold)

        row = 1
        col = 0

        conn = sqlite3.connect(os.path.dirname(os.path.abspath(__file__))+"/LC.db") 
        cur = conn.cursor()
        cur.execute("SELECT * FROM LC WHERE DI BETWEEN (?) and (?)",x)
        rows = cur.fetchall()
        for fio,db,phone,di,dc,aut,book,stat, colvo in (rows):
            worksheet.write(row,col,fio)
            db = datetime.datetime.strptime(db, '%Y-%m-%d')
            db = db.strftime('%d.%m.%Y')
            worksheet.write(row,col+1,db)
            worksheet.write(row,col+2,phone)
            di = datetime.datetime.strptime(di, '%Y-%m-%d')
            di = di.strftime('%d.%m.%Y')
            worksheet.write(row,col+3,di)
            dc = datetime.datetime.strptime(dc, '%Y-%m-%d')
            dc = dc.strftime('%d.%m.%Y')
            worksheet.write(row,col+4,dc)
            worksheet.write(row,col+5,aut)
            worksheet.write(row,col+6,book)
            worksheet.write(row,col+7,stat)
            worksheet.write(row,col+8,colvo)
            row+=1
        conn.commit()
        workbook.close()

def year_excel():
    x = date.today().replace(day=1,month=1).isoformat()
    y = date.today().isoformat()
    y = datetime.datetime.strptime(y, '%Y-%m-%d')
    y = y.strftime('%d_%m_%Y')
    z = date.today().replace(day=31,month=12).isoformat()
    ask = fd.asksaveasfilename(filetypes = (('Excel', '*.xlsx'),), defaultextension=".xlsx")
    if ask != '':
        workbook = xlsxwriter.Workbook(ask)
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
        worksheet.write('I1','Кол-во', bold)

        row = 1
        col = 0

        conn = sqlite3.connect(os.path.dirname(os.path.abspath(__file__))+"/LC.db") 
        cur = conn.cursor()
        cur.execute("SELECT * FROM LC WHERE DI BETWEEN (?) and (?)",(x,z))
        rows = cur.fetchall()
        for fio,db,phone,di,dc,aut,book,stat, colvo in (rows):
            worksheet.write(row,col,fio)
            db = datetime.datetime.strptime(db, '%Y-%m-%d')
            db = db.strftime('%d.%m.%Y')
            worksheet.write(row,col+1,db)
            worksheet.write(row,col+2,phone)
            di = datetime.datetime.strptime(di, '%Y-%m-%d')
            di = di.strftime('%d.%m.%Y')
            worksheet.write(row,col+3,di)
            dc = datetime.datetime.strptime(dc, '%Y-%m-%d')
            dc = dc.strftime('%d.%m.%Y')
            worksheet.write(row,col+4,dc)
            worksheet.write(row,col+5,aut)
            worksheet.write(row,col+6,book)
            worksheet.write(row,col+7,stat)
            worksheet.write(row,col+8,colvo)
            row+=1
        conn.commit()
        workbook.close()

def lub_period_excel(self):

    x = self.en_date1.get()
    x1 = datetime.datetime.strptime(x, '%d.%m.%Y')
    x1 = x1.strftime('%d_%m_%Y')

    y = self.en_date2.get()
    y1 = datetime.datetime.strptime(y, '%d.%m.%Y')
    y1 = y1.strftime('%d_%m_%Y')

    ask = fd.asksaveasfilename(filetypes = (('Excel', '*.xlsx'),), defaultextension=".xlsx")
    if ask != '':
        workbook = xlsxwriter.Workbook(ask)
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
        worksheet.write('I1','Кол-во', bold)

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
        for fio,db,phone,di,dc,aut,book,stat,colvo in (rows):
            worksheet.write(row,col,fio)
            db = datetime.datetime.strptime(db, '%Y-%m-%d')
            db = db.strftime('%d.%m.%Y')
            worksheet.write(row,col+1,db)
            worksheet.write(row,col+2,phone)
            di = datetime.datetime.strptime(di, '%Y-%m-%d')
            di = di.strftime('%d.%m.%Y')
            worksheet.write(row,col+3,di)
            dc = datetime.datetime.strptime(dc, '%Y-%m-%d')
            dc = dc.strftime('%d.%m.%Y')
            worksheet.write(row,col+4,dc)
            worksheet.write(row,col+5,aut)
            worksheet.write(row,col+6,book)
            worksheet.write(row,col+7,stat)
            worksheet.write(row,col+8,colvo)
            row+=1
        conn.commit()
        workbook.close()

def month(x):
    if x == '01':
        x = 'Январь'
    elif x == '02':
        x = 'Февраль'
    elif x == '03':
        x = 'Март'
    elif x == '04':
        x = 'Апрель'
    elif x == '05':
        x = 'Май' 
    elif x == '06':
        x = 'Июнь' 
    elif x == '07':
        x = 'Июль' 
    elif x == '08':
        x = 'Август' 
    elif x == '09':
        x = 'Сентябрь' 
    elif x == '10':
        x = 'Октябрь' 
    elif x == '11':
        x = 'Ноябрь' 
    elif x == '12':
        x = 'Декабрь'
    return x 

def excel_uchet_reg():
    y = date.today().isoformat()
    y = datetime.datetime.strptime(y, '%Y-%m-%d')
    y1 = y.strftime('%d_%m_%Y')

    ask = fd.asksaveasfilename(filetypes = (('Excel', '*.xlsx'),), defaultextension=".xlsx")
    if ask != '':
        workbook = xlsxwriter.Workbook(ask)
        worksheet = workbook.add_worksheet()

        bold = workbook.add_format({'bold' : True})
        bold_wrap = workbook.add_format({'bold' : True})
        bold_wrap.set_text_wrap()

        mon = y.strftime('%m')
        mon = month(mon)
        year = y.strftime('%Y')

        worksheet.merge_range('A1:P1', 'Учёт выдачи книг, брошюр и журналов за ____{0}____{1}г. '.format(mon,year), bold)
        worksheet.merge_range('A2:A3', 'Числа месяца', bold_wrap)
        worksheet.merge_range('B2:B3', 'Всего', bold)
        worksheet.merge_range('C2:O2', 'В том числе', bold)
        worksheet.write('C3', '1 кл.', bold)
        worksheet.write('D3', '2 кл.', bold)
        worksheet.write('E3', '3 кл.', bold)
        worksheet.write('F3', '4 кл.', bold)
        worksheet.write('G3', '5 кл.', bold)
        worksheet.write('H3', '6 кл.', bold)
        worksheet.write('I3', '7 кл.', bold)
        worksheet.write('J3', '8 кл.', bold)
        worksheet.write('K3', '9 кл.', bold)
        worksheet.write('L3', '10 кл.', bold)
        worksheet.write('M3', '11 кл.', bold)
        worksheet.write('N3', 'Проч', bold)
        worksheet.write('O3', 'Учителя', bold)
        worksheet.write('P3', 'Число посещений', bold_wrap)
        x = 1
        row = 3
        col = 0
        while x <= 16:
            worksheet.write(row,col, x, bold)
            x+=1
            col+=1

        worksheet.write('A5', 'Состоит на начало месяца', bold_wrap)

        conn = sqlite3.connect(os.path.dirname(os.path.abspath(__file__))+"/LC.db") 
        cur = conn.cursor()
    
        chisl = (1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31)

        last = first_and_last_day()
        last_day = datetime.datetime.strptime(last[1], '%Y-%m-%d')
        last_day = int(last_day.strftime('%d'))

        first_day = y.replace(day=1)

        now_chisl = int(first_day.strftime('%d'))
        cl = 1
        ro = 5
        column = 0
        vsego = 0
        vsego_it = 0

        while (now_chisl <= last_day) and (now_chisl in chisl):
            worksheet.write(ro,column, now_chisl, bold)
            date_n = first_day.replace(day=now_chisl)
            date_n = date_n.strftime('%Y-%m-%d')
            column +=1
            col_vseg = column
            while cl <= 11:
                cur.execute("SELECT COUNT(*) FROM PROFILE WHERE DREG = (?) AND CLIENT =(?) AND CLA = (?)",(date_n,'Ученик',cl))
                rows = cur.fetchall()
                for row in rows:
                    if row[0] != 0:
                        worksheet.write(ro,column+1, row[0])
                    else:
                        worksheet.write(ro,column+1, '')
                    column+=1
                    cl+=1
                    vsego += int(row[0])
            cur.execute("SELECT COUNT(*) FROM PROFILE WHERE DREG = (?) AND CLIENT =(?)",(date_n,'Другой посетитель'))
            rows = cur.fetchall()
            for row in rows:
                if row[0] != 0:
                    worksheet.write(ro,column+1, row[0])
                else:
                    worksheet.write(ro,column+1, '')
                column+=1
                cl+=1
                vsego += int(row[0])
            cur.execute("SELECT COUNT(*) FROM PROFILE WHERE DREG = (?) AND CLIENT =(?)",(date_n,'Учитель'))
            rows = cur.fetchall()
            for row in rows:
                if row[0] != 0:
                    worksheet.write(ro,column+1, row[0])
                else:
                    worksheet.write(ro,column+1, '')
                column+=1
                cl+=1
                vsego += int(row[0])
            worksheet.write(ro,col_vseg, vsego, bold)
            vsego_it += vsego
            vsego = 0
            column = 0
            ro += 1
            cl = 1
            now_chisl+=1
        worksheet.write(ro,column, 'Всего за месяц', bold_wrap)
        column += 1
        worksheet.write(ro,column, vsego_it, bold)
        column = 0
        ro += 1
        worksheet.write(ro,column, 'Итого с начала', bold_wrap)
        conn.commit()
        workbook.close()


def uchet_book():
    y = date.today().isoformat()
    y = datetime.datetime.strptime(y, '%Y-%m-%d')
    y1 = y.strftime('%d_%m_%Y')

    ask = fd.asksaveasfilename(filetypes = (('Excel', '*.xlsx'),), defaultextension=".xlsx")
    if ask != '':
        workbook = xlsxwriter.Workbook(ask)
        worksheet = workbook.add_worksheet()

        bold = workbook.add_format({'bold' : True})
        bold_wrap = workbook.add_format({'bold' : True})
        bold_wrap.set_text_wrap()

        mon = y.strftime('%m')
        mon = month(mon)
        year = y.strftime('%Y')

        worksheet.merge_range('A1:R1', 'Учёт выдачи книг, брошюр и журналов за ____{0}____{1}г. '.format(mon,year), bold)
        worksheet.merge_range('A2:A3', 'Числа месяца', bold_wrap)
        worksheet.merge_range('B2:B3', 'Всего выдано', bold_wrap)
        worksheet.merge_range('C2:E2', 'ОПЛ', bold)
        worksheet.merge_range('F2:G2', 'ЕНЛ', bold)
        worksheet.write('C3','1, 6, 86, 87', bold_wrap)
        worksheet.write('D3','9', bold)
        worksheet.write('E3','74', bold)
        worksheet.write('F3','2', bold)
        worksheet.write('G3','5', bold)
        worksheet.merge_range('H2:H3', '3', bold)
        worksheet.merge_range('I2:I3', '4', bold)
        worksheet.merge_range('J2:J3', '85', bold)
        worksheet.merge_range('K2:K3', '75', bold)
        worksheet.merge_range('L2:L3', '81, 82, 83', bold_wrap)
        worksheet.merge_range('M2:M3', '84', bold)
        worksheet.merge_range('N2:N3', 'Д', bold)
        worksheet.merge_range('O2:O3', 'Электр. изд', bold_wrap)
        worksheet.merge_range('P2:P3', 'Учебники', bold_wrap)
        worksheet.merge_range('Q2:Q3', 'Периодика', bold_wrap)
        worksheet.merge_range('R2:R3', 'Справки', bold_wrap)
    
        row = 3
        column = 0
        x = 1
        while x<=18:
            worksheet.write(row,column,x, bold)
            x+=1
            column+=1
    
        row +=1
        column=0
        worksheet.write(row,column,'Кол-во предыдущих книговыд.', bold_wrap)
        ro = row + 1
    

        conn = sqlite3.connect(os.path.dirname(os.path.abspath(__file__))+"/LC.db") 
        cur = conn.cursor()
    
        chisl = (1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31)

        last = first_and_last_day()
        last_day = datetime.datetime.strptime(last[1], '%Y-%m-%d')
        last_day = int(last_day.strftime('%d'))

        first_day = y.replace(day=1)

        now_chisl = int(first_day.strftime('%d'))

        vsego = 0

        while (now_chisl <= last_day) and (now_chisl in chisl):
            worksheet.write(ro,column, now_chisl, bold)
            date_n = first_day.replace(day=now_chisl)
            date_n = date_n.strftime('%Y-%m-%d')
            column +=1
            cur.execute("SELECT COUNT(*) FROM LC WHERE DI = (?)",(date_n,))
            rows = cur.fetchall()
            for row in rows:
                if row[0] != 0:
                    worksheet.write(ro,column, row[0], bold)
                else:
                    worksheet.write(ro,column, '', bold)
                vsego+=row[0]
            ro+=1
            column=0
            now_chisl+=1
        
        worksheet.write(ro, column, 'Всего за месяц', bold_wrap)
        column+=1
        worksheet.write(ro, column, vsego, bold)
        column=0
        ro+=1
        worksheet.write(ro, column, 'Итого с начала года', bold_wrap)

        conn.commit()
        workbook.close()

#================================== Изменение темы ================================
def style_change(var_style):
    theme = open(os.path.dirname(os.path.abspath(__file__))+'/theme.txt','w')
    theme.write(var_style)
    theme.close()
    ask = messagebox.askyesno('Перезапустить?', 'Чтобы изменения вступили в силу, необходимо перезапустить программу.\n \nПерезапустить программу прямо сейчас?\n(Перед этим действием убедитесь, что вы сохранили \nвсе изменения, иначе они будут утеряны)')
    if ask == True:
        os.execl(sys.executable, sys.executable, *sys.argv)      
    

#================================= Обработчики событий ============================
def event_handler_main(event, self):
    if event.keycode==65 and event.state == 4: # Ctrl + A
        add_profile(self)
    elif event.keycode==83 and event.state == 4: # Ctrl + S
        edit_profile(self)
    elif event.keycode==46: # Delete
        threading.Thread(target = del_profile, args = [self,]).start()

def event_handler_info(event, self):
    if event.keycode==65 and event.state == 4: # Ctrl + A
        add_book(self)
    elif event.keycode==83 and event.state == 4: # Ctrl + S
        edit_lc(self)
    elif event.keycode==46: # Delete
        threading.Thread(target = delete_lc, args = [self,]).start()

def event_handler_schbook(event, self):
    if event.keycode==83 and event.state == 4: # Ctrl + S
        edit_schbooks(self)
    elif event.keycode==46: # Delete
        threading.Thread(target = del_schbook, args = [self,]).start()

def event_handler_lit(event, self):
    if event.keycode==83 and event.state == 4: # Ctrl + S
        edit_lit(self)
    elif event.keycode==46: # Delete
        threading.Thread(target = del_book, args = [self,]).start()

def event_handler_schbook_a(event, self):
    if event.keycode==65 and event.state == 4: # Ctrl + A
        schbook(self)

def event_handler_lit_a(event, self):
    if event.keycode==65 and event.state == 4: # Ctrl + A
        lit(self)

def easter1():
    global easter_egg
    easter_egg += 1

def easter2():
    global easter_egg
    if easter_egg == 1:
        easter_egg += 1
    else:
        easter_egg = 0

def easter3():
    global easter_egg
    if easter_egg == 2:
        easter_egg += 1
    else:
        easter_egg = 0

def easter4(self):
    filename = os.path.dirname(os.path.abspath(__file__))+"/imper.mp3"
    music = pyglet.media.load(filename)
    music.play()
    pyglet.app.run()

def exit_main():
    threading.Thread(target = music_stop).start()
    sys.exit(0)

def open_txt(self):
    ask = fd.askopenfilename(filetypes = (('TXT', '*.txt'),), defaultextension=".txt")
    if ask != '':
        f = open(ask,'r')
        spis = f.readlines()
        for s in spis:
            lst = s.split()
            i = 0
            res_spis = []
            while i < len(lst):
                res = lst[i]
                res = res.replace('.', '')
                res = res.replace('-', '.')
                res_spis.append(res)
                i+=1
            if len(res_spis) == 11:
                result = [res_spis[0]+' '+res_spis[1]+' '+res_spis[2],
                            datetime.datetime.strptime(res_spis[3], '%d.%m.%Y').strftime('%Y-%m-%d'), res_spis[4], res_spis[5],
                            res_spis[6]+' '+res_spis[7]+' '+res_spis[8],
                            res_spis[9], res_spis[10], datetime.date.today().isoformat()]
            elif len(res_spis) == 12:
                result = [res_spis[0]+' '+res_spis[1]+' '+res_spis[2],
                            datetime.datetime.strptime(res_spis[3], '%d.%m.%Y').strftime('%Y-%m-%d'), res_spis[4], res_spis[5],
                            res_spis[6]+' '+res_spis[7]+' '+res_spis[8],
                            res_spis[9], res_spis[10]+' '+res_spis[11], datetime.date.today().isoformat()]
        
            conn = sqlite3.connect(os.path.dirname(os.path.abspath(__file__))+"/LC.db")
            cur = conn.cursor()
            cur.execute('INSERT INTO PROFILE VALUES (?,?,?,?,?,?,?,?)',result)
            conn.commit()
    update_main(self)
            

if __name__ == "__main__":
    app = Main()
    app.mainloop()