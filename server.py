import tkinter as tk 
from tkinter import messagebox
from tkinter import ttk
from tkinter import *
from tkinter.ttk import *

import socket
import threading
import pyodbc

LARGE_FONT = ("verdana", 13,"bold")

HIEU_HOSTNAME="LAPTOP-50CU9V8L"
HOST = "127.0.0.1"
PORT = 65432
HEADER = 64
FORMAT = "utf8"
DISCONNECT = "x"

#define sever name and database name
SEVER_NAME=HIEU_HOSTNAME+'\SQLEXPRESS'
DATABASE_NAME='Socket_MMT'

#option
SIGNUP = "signup"
LOGIN = "login"
LOGOUT = "logout"
SEARCH = "search"
LIST = "listall"


INSERT_NEW_MATCH = 'insert_a_match'
UPDATE_SCORE = "upd_score"
UPDATE_DATETIME = "upd_date_time"
INSERT_DETAIL = "insert_detail"
DELETE_MATCH = "delete_match"


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen(1)



def Insert_New_Account(user,password):
    cursor=ConnectToDB()
    cursor.execute( "insert into TaiKhoan(TenDangNhap,MatKhau) values(?,?);",(user,password))
    cursor.commit()


def check_clientSignUp(username):
    if username == "admin":
        return False
    cursor=ConnectToDB()
    cursor.execute("select TenDangNhap from TaiKhoan")
    for row in cursor:
        parse=str(row)
        parse_check =parse[2:]
        parse= parse_check.find("'")
        parse_check= parse_check[:parse]
        if parse_check == username:
            return False
    return True

Live_Account=[]
ID=[]
Ad=[]

def Check_LiveAccount(username):
    for row in Live_Account:
        parse= row.find("-")
        parse_check= row[(parse+1):]
        if parse_check== username:
            return False
    return True

def Remove_LiveAccount(conn,addr):
    for row in Live_Account:
        parse= row.find("-")
        parse_check=row[:parse]
        if parse_check== str(addr):
            parse= row.find("-")
            Ad.remove(parse_check)
            username= row[(parse+1):]
            ID.remove(username)
            Live_Account.remove(row)
            conn.sendall("True".encode(FORMAT))

       
def check_clientLogIn(username, password):
    cursor=ConnectToDB()
    cursor.execute("select T.TenDangNhap from TaiKhoan T")
    if Check_LiveAccount(username)== False:
        return 0
    
    # check if admin logged in
    if username == "admin" and password == "database":
        return 1
    
    for row in cursor:
        parse=str(row)
        parse_check =parse[2:]
        parse= parse_check.find("'")
        parse_check= parse_check[:parse]
        if parse_check == username:
            cursor.execute("select T.MatKhau from TaiKhoan T where T.TenDangNhap=(?)",(username))
            parse= str(cursor.fetchone())
            parse_check =parse[2:]
            parse= parse_check.find("'")
            parse_check= parse_check[:parse]
            if password== parse_check:
                return 1
    return 2


def clientSignUp(sck, addr):

    user = sck.recv(1024).decode(FORMAT)
    print("username:--" + user +"--")

    sck.sendall(user.encode(FORMAT))

    pswd = sck.recv(1024).decode(FORMAT)
    print("password:--" + pswd +"--")


    #a = input("accepting...")
    accepted = check_clientSignUp(user)
    print("accept:", accepted)
    sck.sendall(str(accepted).encode(FORMAT))

    if accepted:
        Insert_New_Account(user, pswd)

        # add client sign up address to live account
        Ad.append(str(addr))
        ID.append(user)
        account=str(Ad[Ad.__len__()-1])+"-"+str(ID[ID.__len__()-1])
        Live_Account.append(account)

    print("end-logIn()")
    print("")

def clientLogIn(sck):

    user = sck.recv(1024).decode(FORMAT)
    print("username:--" + user +"--")

    sck.sendall(user.encode(FORMAT))
    
    pswd = sck.recv(1024).decode(FORMAT)
    print("password:--" + pswd +"--")
    
    accepted = check_clientLogIn(user, pswd)
    if accepted == 1:
        ID.append(user)
        account=str(Ad[Ad.__len__()-1])+"-"+str(ID[ID.__len__()-1])
        Live_Account.append(account)
    
    print("accept:", accepted)
    sck.sendall(str(accepted).encode(FORMAT))
    print("end-logIn()")
    print("")


def getMatches():
    cursor=ConnectToDB()
    cursor.execute("select * from TranDau")
    res=[]
    for row in cursor:
        res.append(row)
    return res

# match : [ID, TeamA, TeamB, Score, Date, Time]

def Get_ALL_IDs():
    cursor=ConnectToDB()
    cursor.execute("select MaTD from TranDau")
    res=[]
    for row in cursor:
        parse=str(row)
        parse_check =parse[2:]
        parse= parse_check.find("'")
        parse_check= parse_check[:parse]
        res.append(parse_check)
    return res

def Insert_New_Match(sck):
    data = ""
    match=[]
    for i in range(6):
        data=sck.recv(1024).decode(FORMAT)
        print(data)
        sck.sendall(data.encode(FORMAT))
        match.append(data)
    res= Get_ALL_IDs()
    for row in res:
        if row==match[0]:
            sck.sendall("failed".encode(FORMAT))
            return False
    try:
        cursor=ConnectToDB()
        cursor.execute("insert into TranDau(MaTD,DoiA,DoiB,Score,NgayThiDau,GioThiDau) values (?,?,?,?,?,?)",
        (match[0],match[1],match[2],match[3],match[4],match[5]))
        cursor.commit()
    except pyodbc.Error:
        sck.sendall("failed".encode(FORMAT))
        return False
    

    sck.sendall("success".encode(FORMAT))
    return True


def Update_Score(sck):
   
    match=[]
    for i in range(2):
        data=sck.recv(1024).decode(FORMAT)
        print(data)
        sck.sendall(data.encode(FORMAT))
        match.append(data)
    
    res=Get_ALL_IDs()
    
    for row in res:
        if row == match[0]:
            try:
                cursor=ConnectToDB()
                cursor.execute('update TranDau set Score=? where MaTD=?',(match[1],match[0]))
                cursor.commit()
            except pyodbc.Error:
                sck.sendall("failed".encode(FORMAT))
                return False
            sck.sendall("success".encode(FORMAT))
            return True
    
    sck.sendall("failed".encode(FORMAT))
    return False

def Update_Date_Time(sck):
    match=[]
    for i in range(3):
        data=sck.recv(1024).decode(FORMAT)
        print(data)
        sck.sendall(data.encode(FORMAT))
        match.append(data)
    
    res= Get_ALL_IDs()
    for row in res:
        if row == match[0]:
            try:
                cursor=ConnectToDB()
                cursor.execute("update TranDau set NgayThiDau=?, GioThiDau=? where MaTD=? ",(match[1],match[2],match[0]))
                cursor.commit()
            except pyodbc.Error:
                sck.sendall("failed".encode(FORMAT))
                return False
            sck.sendall("success".encode(FORMAT))
            return True
    
    sck.sendall("failed".encode(FORMAT))
    return False

def Insert_Detail(sck):
    match=[]

    for i in range(5):
        data=sck.recv(1024).decode(FORMAT)
        print(data)
        sck.sendall(data.encode(FORMAT))
        match.append(data)
    
    res= Get_ALL_IDs()
    for row in res:
        if row==match[0]:
            try:
                cursor=ConnectToDB()
                cursor.execute('insert into CT_TranDau(MaTD,TenDoi,SuKien,TenCauThu,ThoiGian) values(?,?,?,?,?)'
                ,(match[0],match[1],match[2],match[3],match[4]))
                cursor.commit()
            except pyodbc.Error:
                sck.sendall("failed".encode(FORMAT))
                return False
            sck.sendall("success".encode(FORMAT))
            return True
    
    sck.sendall("failed".encode(FORMAT))
    return False

def Delete_Match(sck):
   
    data=sck.recv(1024).decode(FORMAT)
    print(data)
    sck.sendall(data.encode(FORMAT))
    
    res=Get_ALL_IDs()
    print(res)
    
    for row in res:
        if row == data:
            print("true")
            try:
                cursor=ConnectToDB()
                cursor.execute("Delete from CT_TranDau where MaTD=?",(data))
                cursor.execute("Delete from TranDau where MaTD=?",(data))
                cursor.commit()
                print("done")
            except pyodbc.Error:
                sck.sendall("failed".encode(FORMAT))
                print("error")
                return False
            sck.sendall("success".encode(FORMAT))
            return True
    
    sck.sendall("failed".encode(FORMAT))
    return False

       
def clientListMatches(sck):
    matches = getMatches()
    
    for match in matches:
        msg = "next"
        sck.sendall(msg.encode(FORMAT))
        sck.recv(1024)

        for data in match:
            data = str(data)
            print(data, end=' ')
            sck.sendall(data.encode(FORMAT))
            sck.recv(1024)

    
    msg = "end"
    sck.sendall(msg.encode(FORMAT))
    sck.recv(1024)


def find1Match(id):
    IDs=Get_ALL_IDs()
    for row in IDs:
        if row ==id:
            cursor=ConnectToDB()
            cursor.execute("select * from TranDau where MaTD=?",(id))
            match=cursor.fetchone()
            return match
    return False


def findDetails(id):
    IDs=Get_ALL_IDs()
    for row in IDs:
        if row == id:
            details=[]
            cursor=ConnectToDB()
            cursor.execute("select * from CT_TranDau where MaTD=? order by ThoiGian ",(id))
            for row in cursor:
                print(row)
                details.append(row)
            return details
    return False

def clientSearch(sck):

    #receive a match
    id = sck.recv(1024).decode(FORMAT)
    
    match =  find1Match(id)

    if match == False :
        msg = "noid"
        sck.sendall(msg.encode(FORMAT))
        return 
    else :
        msg = "ok"
        sck.sendall(msg.encode(FORMAT))

    for data in match:
        data = str(data)
        print(data, end=' ')
        sck.sendall(data.encode(FORMAT))
        sck.recv(1024)

    # receive match details
    msg = sck.recv(1024).decode(FORMAT)

    details = findDetails(id) 

    for row in details:
        msg = "next"
        sck.sendall(msg.encode(FORMAT))

        for data in row:
            data = str(data)
            sck.sendall(data.encode(FORMAT))
            sck.recv(1024)

    msg = "end"
    sck.sendall(msg.encode(FORMAT))


# Specify this function before interpreting
def ConnectToDB():
    server = SEVER_NAME
    database = DATABASE_NAME
    username = 'sa' 
    password = 'svcntt' 
    cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)
    cursor = cnxn.cursor()
    return cursor

def handle_client(conn, addr):

     
    while True:

        option = conn.recv(1024).decode(FORMAT)


        if option == LOGIN:
            Ad.append(str(addr))
            clientLogIn(conn)
        
        elif option == SIGNUP:
            clientSignUp(conn, addr)


        elif option == LIST:
            clientListMatches(conn)
        
        elif option == SEARCH:
            clientSearch(conn)

        elif option == LOGOUT:
            Remove_LiveAccount(conn,addr)

        elif option ==INSERT_NEW_MATCH:
            Insert_New_Match(conn)
        
        elif option == UPDATE_SCORE:
            Update_Score(conn)
        
        elif option == UPDATE_DATETIME:
            Update_Date_Time(conn)

        elif option == INSERT_DETAIL:
            Insert_Detail(conn)
            
        elif option == DELETE_MATCH:
            Delete_Match(conn)


    Remove_LiveAccount(conn,addr)
    conn.close()
    print("end-thread")


def runServer():
    try:
        print(HOST)
        print("Waiting for Client")

        while True:
            print("enter while loop")
            conn, addr = s.accept()


            clientThread = threading.Thread(target=handle_client, args=(conn,addr))
            clientThread.daemon = True 
            clientThread.start()
        
            
            #handle_client(conn, addr)
            print("end main-loop")

        
    except KeyboardInterrupt:
        print("error")
        s.close()
    finally:
        s.close()
        print("end")
 

# defind GUI-app class
class SoccerNews_Admin(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        #self.iconbitmap('soccer-ball.ico')
        self.title("Soccer Sever")
        self.geometry("500x200")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.resizable(width=False, height=False)

        container = tk.Frame(self)
        container.pack(side="top", fill = "both", expand = True)
        
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (StartPage,HomePage):
            frame = F(container, self)

            self.frames[F] = frame 

            frame.grid(row=0, column=0, sticky="nsew")

        self.showFrame(StartPage)


    def showFrame(self, container):
        
        frame = self.frames[container]
        if container==HomePage:
            self.geometry("500x350")
        else:
            self.geometry("500x200")
        frame.tkraise()

    # close-programe function
    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.destroy()

    def logIn(self,curFrame):

        user = curFrame.entry_user.get()
        pswd = curFrame.entry_pswd.get()

        if pswd == "":
            curFrame.label_notice["text"] = "password cannot be empty"
            return 

        if user == "admin" and pswd == "server":
            self.showFrame(HomePage)
            curFrame.label_notice["text"] = ""
        else:
            curFrame.label_notice["text"] = "invalid username or password"

class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.configure(bg="bisque2")
        
        
        label_title = tk.Label(self, text="\nLOG IN FOR SEVER\n", font=LARGE_FONT,fg='#20639b',bg="bisque2").grid(row=0,column=1)

        label_user = tk.Label(self, text="\tUSERNAME ",fg='#20639b',bg="bisque2",font='verdana 10 bold').grid(row=1,column=0)
        label_pswd = tk.Label(self, text="\tPASSWORD ",fg='#20639b',bg="bisque2",font='verdana 10 bold').grid(row=2,column=0)

        self.label_notice = tk.Label(self,text="",bg="bisque2",fg='red')
        self.entry_user = tk.Entry(self,width=30,bg='light yellow')
        self.entry_pswd = tk.Entry(self,width=30,bg='light yellow')

        button_log = tk.Button(self,text="LOG IN",bg="#20639b",fg='floral white',command=lambda: controller.logIn(self))

        button_log.grid(row=4,column=1)
        button_log.configure(width=10)
        self.label_notice.grid(row=3,column=1)
        self.entry_pswd.grid(row=2,column=1)
        self.entry_user.grid(row=1,column=1)

class HomePage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent) 
        self.configure(bg="bisque2")
        label_title = tk.Label(self, text="\n ACTIVE ACCOUNT ON SEVER\n", font=LARGE_FONT,fg='#20639b',bg="bisque2").pack()
        
        self.conent =tk.Frame(self)
        self.data = tk.Listbox(self.conent, height = 10, 
                  width = 40, 
                  bg='floral white',
                  activestyle = 'dotbox', 
                  font = "Helvetica",
                  fg='#20639b')
        
        button_log = tk.Button(self,text="REFRESH",bg="#20639b",fg='floral white',command=self.Update_Client)
        button_back = tk.Button(self, text="LOG OUT",bg="#20639b",fg='floral white' ,command=lambda: controller.showFrame(StartPage))
        button_log.pack(side= BOTTOM)
        button_log.configure(width=10)
        button_back.pack(side=BOTTOM)
        button_back.configure(width=10)
        
        self.conent.pack_configure()
        self.scroll= tk.Scrollbar(self.conent)
        self.scroll.pack(side = RIGHT, fill= BOTH)
        self.data.config(yscrollcommand = self.scroll.set)
        
        self.scroll.config(command = self.data.yview)
        self.data.pack()
        
    def Update_Client(self):
        self.data.delete(0,len(Live_Account))
        for i in range(len(Live_Account)):
            self.data.insert(i,Live_Account[i])
    


sThread = threading.Thread(target=runServer)
sThread.daemon = True 
sThread.start()

        
app = SoccerNews_Admin()
app.mainloop()