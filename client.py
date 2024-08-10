import socket
import tkinter as tk 
from tkinter import messagebox
from tkinter import ttk 
import threading
from datetime import datetime

HOST = "127.0.0.1"
PORT = 65432
HEADER = 64
FORMAT = "utf8"
DISCONNECT = "x"

LARGE_FONT = ("verdana", 13,"bold")

#option
SIGNUP = "signup"
LOGIN = "login"
LOGOUT = "logout"
SEARCH = "search"
LIST = "listall"

ADMIN_USERNAME = 'admin'
ADMIN_PSWD = 'database'

INSERT_NEW_MATCH='insert_a_match'
UPDATE_SCORE = "upd_score"
UPDATE_DATETIME = "upd_date_time"
INSERT_DETAIL = "insert_detail"
DELETE_MATCH = "delete_match"


#GUI intialize
class SoccerNews_App(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        
        self.geometry("500x200")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.resizable(width=False, height=False)

        container = tk.Frame(self)
        container.pack(side="top", fill = "both", expand = True)
        
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (StartPage, HomePage,AdminPage):
            frame = F(container, self)

            self.frames[F] = frame 

            frame.grid(row=0, column=0, sticky="nsew")

        self.showFrame(StartPage)
    
    def showFrame(self, container):
        frame = self.frames[container]
        if container==HomePage:
            self.geometry("700x500")
        elif container == AdminPage:
            self.geometry("450x500")
        else:
            self.geometry("500x200")
        frame.tkraise()

    # close-programe function
    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.destroy()
            try:
                option = LOGOUT
                client.sendall(option.encode(FORMAT))
            except:
                pass

    def logIn(self,curFrame,sck):
        try:
            user = curFrame.entry_user.get()
            pswd = curFrame.entry_pswd.get()

            if user == "" or pswd == "":
                curFrame.label_notice["text"] = "Fields cannot be empty"
                return 
       
            #notice server for starting log in
            option = LOGIN
            sck.sendall(option.encode(FORMAT))

            #send username and password to server
            sck.sendall(user.encode(FORMAT))
            print("input:", user)

            sck.recv(1024)
            print("s responded")

            
            sck.sendall(pswd.encode(FORMAT))
            print("input:", pswd)


            # see if login is accepted
            accepted = sck.recv(1024).decode(FORMAT)
            print("accepted: "+ accepted)

            if accepted == "1":
                if user =="admin":
                    self.showFrame(AdminPage)
                else:
                    self.showFrame(HomePage)
                
                curFrame.label_notice["text"] = ""
            elif accepted == "2":
                curFrame.label_notice["text"] = "invalid username or password"
            elif  accepted == "0":
                curFrame.label_notice["text"] = "user already logged in"

        except:
            curFrame.label_notice["text"] = "Error: Server is not responding"
            print("Error: Server is not responding")

    def signUp(self,curFrame, sck):
        
        try:
        
            user = curFrame.entry_user.get()
            pswd = curFrame.entry_pswd.get()

            if pswd == "":
                curFrame.label_notice["text"] = "password cannot be empty"
                return 

            #notice server for starting log in
            option = SIGNUP
            sck.sendall(option.encode(FORMAT))
            
            
            #send username and password to server
            sck.sendall(user.encode(FORMAT))
            print("input:", user)

            sck.recv(1024)
            print("s responded")

            sck.sendall(pswd.encode(FORMAT))
            print("input:", pswd)


            # see if login is accepted
            accepted = sck.recv(1024).decode(FORMAT)
            print("accepted: "+ accepted)

            if accepted == "True":
                self.showFrame(HomePage)
                curFrame.label_notice["text"] = ""
            else:
                curFrame.label_notice["text"] = "username already exists"

        except:
            curFrame.label_notice["text"] = "Error 404: Server is not responding"
            print("404")

    def logout(self,curFrame, sck):
        try:
            option = LOGOUT
            sck.sendall(option.encode(FORMAT))
            accepted = sck.recv(1024).decode(FORMAT)
            if accepted == "True":
                self.showFrame(StartPage)
        except:
            curFrame.label_notice["text"] = "Error: Server is not responding"





class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.configure(bg="bisque2")

        label_title = tk.Label(self, text="LOG IN", font=LARGE_FONT,fg='#20639b',bg="bisque2")
        label_user = tk.Label(self, text="username ",fg='#20639b',bg="bisque2",font='verdana 10 ')
        label_pswd = tk.Label(self, text="password ",fg='#20639b',bg="bisque2",font='verdana 10 ')

        self.label_notice = tk.Label(self,text="",bg="bisque2")
        self.entry_user = tk.Entry(self,width=20,bg='light yellow')
        self.entry_pswd = tk.Entry(self,width=20,bg='light yellow')

        button_log = tk.Button(self,text="LOG IN", bg="#20639b",fg='floral white',command=lambda: controller.logIn(self, client)) 
        button_log.configure(width=10)
        button_sign = tk.Button(self,text="SIGN UP",bg="#20639b",fg='floral white', command=lambda: controller.signUp(self, client)) 
        button_sign.configure(width=10)
        
        label_title.pack()
        label_user.pack()
        self.entry_user.pack()
        label_pswd.pack()
        self.entry_pswd.pack()
        self.label_notice.pack()

        button_log.pack()
        button_sign.pack()

# match : [ID, TeamA, TeamB, Score, Date, Time]

def checkTime(stringDate, stringTime):
    date_time = datetime.now()

    d = stringDate.split('-') 
    for i in range(3):
        d[i] = int(d[i])

    t = stringTime.split(':') 
    for i in range(3):
        t[i] = int(t[i])

    date_match = datetime(d[0], d[1], d[2], t[0], t[1], t[2])
    
    if date_match.date() < date_time.date():
        msg = "FULL TIME"
        return msg
    if date_match.date() > date_time.date():
        msg = "NOT YET"
        return msg
    
    # if dates are the same 
    if date_match.date() == date_time.date():
        if date_match.time() > date_time.time():
            msg = "NOT YET"
            return msg

        if date_match.time() < date_time.time():
            delta = date_time - date_match
            print(delta)
            # calculate the number of MINUTES that have lasted
            time_diff = delta.seconds / 60 
            print(time_diff)
            
            if time_diff <= 15:
                msg = "START TIME"
                return msg
            
            if 15 < time_diff <= 45:
                msg = "HALF TIME"
                return msg

            if 45 < time_diff <= 60:
                msg = "BREAK TIME"
                return msg

            if 60 < time_diff <= 105:
                msg = "LAST TIME"
                return msg
            
            if 105 < time_diff:
                msg = "FULL TIME"
                return msg

def checkEvent(strEven):
    msg = "---"
    if strEven == "1":
        msg = "GOAL"
        return msg

    if strEven == "2":
        msg = "YELLOW CARD"
        return msg

    if strEven == "3":
        msg = "RED CARD"
        return msg

    return msg 


class HomePage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.configure(bg="bisque2")
        
        label_title = tk.Label(self, text="HOME PAGE", font=LARGE_FONT,fg='#20639b',bg="bisque2")
        button_back = tk.Button(self, text="Go back",bg="#20639b",fg='#f5ea54', command=lambda: controller.logout(self,client))
        button_list = tk.Button(self, text="List all", bg="#20639b",fg='#f5ea54',command=self.listAll)

        self.entry_search = tk.Entry(self)
        button_search = tk.Button(self, text="Search for ID",bg="#20639b",fg='#f5ea54', command=self.searchID)

        label_title.pack(pady=10)

        button_search.configure(width=10)
        button_list.configure(width=10)
        button_back.configure(width=10)

        self.entry_search.pack()

        self.label_notice = tk.Label(self, text="", bg="bisque2" )
        self.label_notice.pack(pady=4)

        button_search.pack(pady=2)
        button_list.pack(pady=2) 
        button_back.pack(pady=2)

        self.frame_detail = tk.Frame(self, bg="steelblue1")
        
        self.label_score = tk.Label(self.frame_detail,bg="steelblue1", text="", font=LARGE_FONT)
        self.label_time = tk.Label(self.frame_detail,bg="steelblue1", text="", font=LARGE_FONT)
        self.label_status = tk.Label(self.frame_detail,bg="steelblue1", text="", font=LARGE_FONT)

        self.tree_detail = ttk.Treeview(self.frame_detail)
        self.tree_detail["column"] = ("Time", "Player", "Team", "Event")
        
        self.tree_detail.column("#0", width=0, stretch=tk.NO)
        self.tree_detail.column("Time", anchor='c', width=50)
        self.tree_detail.column("Player", anchor='c', width=200)
        self.tree_detail.column("Team", anchor='c', width=200)
        self.tree_detail.column("Event", anchor='c', width=180)

        self.tree_detail.heading("0", text="", anchor='c')
        self.tree_detail.heading("Time", text="Time", anchor='c')
        self.tree_detail.heading("Player", text="Player", anchor='c')
        self.tree_detail.heading("Team", text="Team", anchor='c')
        self.tree_detail.heading("Event", text="Event", anchor='c')


        self.label_score.pack(pady=5)
        self.label_time.pack(pady=5)
        self.label_status.pack(pady=5)
        self.tree_detail.pack()
        


        self.frame_list = tk.Frame(self, bg="tomato")
        
        self.tree = ttk.Treeview(self.frame_list)

        
        self.tree["column"] = ("ID", "TeamA", "Score", "TeamB", "Status")
        
        
        self.tree.column("#0", width=0, stretch=tk.NO)
        self.tree.column("ID", anchor='c', width=30)
        self.tree.column("TeamA", anchor='e', width=140)
        self.tree.column("Score", anchor='c', width=40)
        self.tree.column("TeamB", anchor='w', width=140)
        self.tree.column("Status", anchor='c', width=80)

        self.tree.heading("0", text="", anchor='c')
        self.tree.heading("ID", text="ID", anchor='c')
        self.tree.heading("TeamA", text="TeamA", anchor='e')
        self.tree.heading("Score", text="Score", anchor='c')
        self.tree.heading("TeamB", text="TeamB", anchor='w')
        self.tree.heading("Status", text="Status", anchor='c')
        
        self.tree.pack(pady=20)
        
    
    def recieveMatches(self):
        match = []
    
        matches = []
        data = ''
        while True:
            data = client.recv(1024).decode(FORMAT)
            client.sendall(data.encode(FORMAT))
            if data == "end":
                break
            
            # match : [ID, TeamA, TeamB, Score, Date, Time]

            for i in range(6):
                data = client.recv(1024).decode(FORMAT)
                client.sendall(data.encode(FORMAT))
                match.append(data) 

            
            matches.append(match)
            match = []

        return matches

    def listAll(self):
        try:
            self.frame_detail.pack_forget()

            option = LIST
            client.sendall(option.encode(FORMAT))
            
            matches = self.recieveMatches()
            
            x = self.tree.get_children()
            for item in x:
                self.tree.delete(item)

            i = 0
            for m in matches:
                self.tree.insert(parent="", index="end", iid=i, values=( m[0], m[1], m[3], m[2], checkTime(m[4], m[5]) ) )
                
                i += 1

            self.frame_list.pack(pady=10)
        except:
            self.label_notice["text"] = "Error"
            


    def receive1Match(self):
              
        data = ""
        match = []

        for i in range(6):
            data = client.recv(1024).decode(FORMAT)
            client.sendall(data.encode(FORMAT))
            match.append(data) 

        return match

    

    def receiveDetails(self):
        option = "details"
        client.sendall(option.encode(FORMAT))

        row = []
        details = []
        data = ""

        while True:
            data = client.recv(1024).decode(FORMAT)
            if (data == "end"):
                break
            
            for i in range(5):
                data = client.recv(1024).decode(FORMAT)
                client.sendall(data.encode(FORMAT)) 
                row.append(data)

            details.append(row)
            row = []
        
        return details


    def searchID(self):
        try:
            self.label_notice["text"] = ""
            id = self.entry_search.get()    
            
            if (id == ""):
                self.label_notice["text"] = "Field cannot be empty"
                return

            option = SEARCH
            client.sendall(option.encode(FORMAT))

            

            self.frame_list.pack_forget()
            
            # detail = [ID, team, event, player, time]
            # match : [ID, TeamA, TeamB, Score, Date, Time]
            

            client.sendall(id.encode(FORMAT))
            msg = client.recv(1024).decode(FORMAT)

            if (msg == "noid"):
                print("no id")
                self.label_notice["text"] = "This ID doesn't exist"
                return

            x = self.tree_detail.get_children()
            for item in x:
                self.tree_detail.delete(item)

            m = self.receive1Match()

            d = self.receiveDetails()

            self.label_score["text"] = m[0]+" "+m[1]+" "+m[3]+" "+m[2] 
            self.label_time["text"] = m[4]+" "+m[5]
            self.label_status["text"] = checkTime(m[4], m[5])
            
            i = 0
            for row in d:
                self.tree_detail.insert(parent="", index="end", iid=i, values=(row[4],row[3],row[1],checkEvent( row[2] )) )
                i += 1

            self.frame_detail.pack()
        except:
            self.label_notice["text"] = "Error"



class AdminPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.configure(bg="bisque2")
     
        self.insert_a_match_frame=tk.Frame(self,bg="bisque2")
        self.detail_frame=tk.Frame(self,bg="bisque2")
        self.date_time_frame=tk.Frame(self,bg="bisque2")
        self.update_score_frame=tk.Frame(self,bg="bisque2")
        self.delete_match_frame=tk.Frame(self,bg="bisque2")
        

        label_title = tk.Label(self, text="\n      ADMINISTRATOR \n", font='verdana 22 bold',fg='#20639b',bg="bisque2").grid(row=0,column=0,columnspan=2,)
        button_back = tk.Button(self, text="LOG OUT",bg="#20639b",fg='#f5ea54' ,command=lambda: controller.logout(self,client))
        self.button_list = tk.Button(self, text="ENTER",bg="#20639b",fg='#f5ea54',command= self.Insert_New_Match)
       
        self.label_option=tk.Label(self,text='OPTION\t',fg='#20639b',bg="bisque2",font='verdana 15 bold').grid(row=1,column=0)
        self.label_notice = tk.Label(self, text="", bg="bisque2" )
        self.label_notice.grid(row=2,column=1)
        
        # combobox
        self.n=tk.StringVar()
        self.option=ttk.Combobox(self,width=25,textvariable=self.n,font = "Helvetica 13 ")
        self.option['values']=('Insert a match','Update Score','Update Date&time','Insert detail','Delete a match')
        self.option['state'] = 'readonly'
        self.option.bind('<<ComboboxSelected>>',self.Choose_Function)
        self.option.current(0)
        self.option.grid(row=1,column=1)


        # insert a match frame setup
        self.ID_entry1=tk.Entry(self.insert_a_match_frame,font = "Helvetica 13 bold")
        self.teamA_entry=tk.Entry(self.insert_a_match_frame,font = "Helvetica 13 bold")
        self.teamB_entry=tk.Entry(self.insert_a_match_frame,font = "Helvetica 13 bold")
        self.score_entry1=tk.Entry(self.insert_a_match_frame,font = "Helvetica 13 bold")
        self.date_entry1=tk.Entry(self.insert_a_match_frame,font = "Helvetica 13 bold")
        self.time_entry1=tk.Entry(self.insert_a_match_frame,font = "Helvetica 13 bold")

        self.label_ID1=tk.Label(self.insert_a_match_frame, text ='ID:\t',bg="bisque2",fg='#20639b',font='verdana 15 bold')
        self.label_teamA=tk.Label(self.insert_a_match_frame, text='TeamA:\t',bg="bisque2",fg='#20639b',font='verdana 15 bold')
        self.label_teamB=tk.Label(self.insert_a_match_frame,text='TeamB:\t',bg="bisque2",fg='#20639b',font='verdana 15 bold')
        self.label_score1=tk.Label(self.insert_a_match_frame,text='Score:\t',bg="bisque2",fg='#20639b',font='verdana 15 bold')
        self.label_date1=tk.Label(self.insert_a_match_frame,text="Date:\t",bg="bisque2",fg='#20639b',font='verdana 15 bold')
        self.label_time1=tk.Label(self.insert_a_match_frame,text="Time:\t",bg="bisque2",fg='#20639b',font='verdana  15 bold')
 
        
        # update score frame setup
        self.ID_entry2=tk.Entry(self.update_score_frame,font = "Helvetica 13 bold")
        self.score_entry2=tk.Entry(self.update_score_frame,font = "Helvetica 13 bold")

        self.label_ID2=tk.Label(self.update_score_frame, text ='ID:\t',bg="bisque2",fg='#20639b',font='verdana 15 bold')
        self.label_score2=tk.Label(self.update_score_frame,text='Score:\t',bg="bisque2",fg='#20639b',font='verdana 15 bold')
  
        
        # date_time frame setup
        self.ID_entry3=tk.Entry(self.date_time_frame,font = "Helvetica 13 bold")
        self.date_entry3=tk.Entry(self.date_time_frame,font = "Helvetica 13 bold")
        self.time_entry3=tk.Entry(self.date_time_frame,font = "Helvetica 13 bold")

        self.label_ID3=tk.Label(self.date_time_frame, text ='ID:\t',bg="bisque2",fg='#20639b',font='verdana 15 bold')
        self.label_date3=tk.Label(self.date_time_frame,text="Date:\t",bg="bisque2",fg='#20639b',font='verdana 15 bold')
        self.label_time3=tk.Label(self.date_time_frame,text="Time:\t",bg="bisque2",fg='#20639b',font='verdana  15 bold')
 
        
        # detail frame setup
        self.Did_entry=tk.Entry(self.detail_frame,font = "Helvetica 13 bold")
        self.Dteam_entry=tk.Entry(self.detail_frame,font = "Helvetica 13 bold")
        self.player_entry=tk.Entry(self.detail_frame,font = "Helvetica 13 bold")
        self.Event_entry=tk.Entry(self.detail_frame,font = "Helvetica 13 bold")
        self.Dtime_entry=tk.Entry(self.detail_frame,font = "Helvetica 13 bold")
       
        self.label_Did=tk.Label(self.detail_frame,text='ID:\t',bg="bisque2",fg='#20639b',font='verdana 15 bold')
        self.label_Dteam=tk.Label(self.detail_frame, text='Team:\t',bg="bisque2",fg='#20639b',font='verdana 15 bold')
        self.label_player=tk.Label(self.detail_frame,text='Player:\t',bg="bisque2",fg='#20639b',font='verdana 15 bold')
        self.label_Event=tk.Label(self.detail_frame,text='Event:\t',bg="bisque2",fg='#20639b',font='verdana 15 bold')
        self.label_Dtime=tk.Label(self.detail_frame,text="Time:\t",bg="bisque2",fg='#20639b',font='verdana  15 bold')


        # delete match frame setup
        self.ID_entry4=tk.Entry(self.delete_match_frame,font = "Helvetica 13 bold")

        self.label_ID4=tk.Label(self.delete_match_frame,text ='ID:\t',bg="bisque2",fg='#20639b',font='verdana 15 bold')

        
        # button setup
        self.button_list.grid(row=12,column=1, ipady=7,ipadx=20)
        self.button_list.configure(width=10)
        button_back.grid(row=13,column=1, ipady=7,ipadx=20)
        button_back.configure(width=10)
 
    
    def Grid_insert_a_match(self):
        # insert a match frame
        self.label_ID1.grid(row=3,column=0)
        self.label_teamA.grid(row=4,column=0)
        self.label_teamB.grid(row=5,column=0)
        self.label_score1.grid(row=6,column=0)
        self.label_date1.grid(row=7,column=0)
        self.label_time1.grid(row=8,column=0)     

        self.ID_entry1.grid(row=3,column=1, ipady=7,ipadx=20)
        self.teamA_entry.grid(row=4,column=1, ipady=7,ipadx=20)
        self.teamB_entry.grid(row=5,column=1, ipady=7,ipadx=20)
        self.score_entry1.grid(row=6,column=1, ipady=7,ipadx=20)
        self.date_entry1.grid(row=7,column=1, ipady=7,ipadx=20)
        self.time_entry1.grid(row=8,column=1, ipady=7,ipadx=20)
        
        
    def Grid_date_time(self):
        # date_time frame
        self.label_ID3.grid(row=3,column=0)
        self.label_date3.grid(row=4,column=0)
        self.label_time3.grid(row=5,column=0)

        self.ID_entry3.grid(row=3,column=1, ipady=7,ipadx=20)
        self.date_entry3.grid(row=4,column=1, ipady=7,ipadx=20)
        self.time_entry3.grid(row=5,column=1, ipady=7,ipadx=20)
        

    def Grid_update_score(self):
        # update score frame
        self.label_ID2.grid(row=3,column=0)
        self.label_score2.grid(row=4,column=0)

        self.ID_entry2.grid(row=3,column=1, ipady=7,ipadx=20)
        self.score_entry2.grid(row=4,column=1, ipady=7,ipadx=20)
        

    def Grid_delete_match(self):
        # delete match frame
        self.label_ID4.grid(row=3,column=0)

        self.ID_entry4.grid(row=3,column=1, ipady=7,ipadx=20)
        
        
    def Grid_detail(self):
        # detail frame
        self.label_Did.grid(row=3,column=0)
        self.label_Dteam.grid(row=4,column=0)
        self.label_player.grid(row=5,column=0)
        self.label_Event.grid(row=6,column=0)
        self.label_Dtime.grid(row=7,column=0)

        self.Did_entry.grid(row=3,column=1, ipady=7,ipadx=20)
        self.Dteam_entry.grid(row=4,column=1, ipady=7,ipadx=20)
        self.player_entry.grid(row=5,column=1, ipady=7,ipadx=20)
        self.Event_entry.grid(row=6,column=1, ipady=7,ipadx=20)
        self.Dtime_entry.grid(row=7,column=1, ipady=7,ipadx=20)


    def Delete_Entry(self):
        self.ID_entry1.delete(0,'end')
        self.teamA_entry.delete(0,'end')
        self.teamB_entry.delete(0,'end')
        self.score_entry1.delete(0,'end')
        self.date_entry1.delete(0,'end')
        self.time_entry1.delete(0,'end')
        
        self.ID_entry2.delete(0,'end')
        self.score_entry2.delete(0,'end')
        
        self.ID_entry3.delete(0,'end')
        self.date_entry3.delete(0,'end')
        self.time_entry3.delete(0,'end')
        
        self.player_entry.delete(0,'end')
        self.Event_entry.delete(0,'end')
        self.Did_entry.delete(0,'end')
        self.Dteam_entry.delete(0,'end')
        self.Dtime_entry.delete(0,'end')
        
        self.ID_entry4.delete(0,'end')        

   
    def Choose_Function(self,event):
        msg= self.option.get()
        self.insert_a_match_frame.grid_forget()
        self.detail_frame.grid_forget()
        self.date_time_frame.grid_forget()
        self.update_score_frame.grid_forget()
        self.delete_match_frame.grid_forget()
        
        self.label_notice["text"] = ""
        
        if msg=='Insert a match':
            self.insert_a_match_frame.grid(row=3,column=0,columnspan=2)
            self.Grid_insert_a_match()
            self.button_list.configure(command=self.Insert_New_Match)
        
        if msg=='Update Score':
            self.update_score_frame.grid(row=3,column=0,columnspan=2)           
            self.Grid_update_score()
            self.button_list.configure(command=self.Update_Score)
                 
        if msg=='Insert detail':
            self.detail_frame.grid(row=3,column=0,columnspan=2)
            self.Grid_detail()
            self.button_list.configure(command=self.Insert_Detail)
        
        if msg=="Update Date&time":
            self.date_time_frame.grid(row=3,column=0,columnspan=2)
            self.Grid_date_time()
            self.button_list.configure(command=self.Update_Date_Time)
            
        if msg=="Delete a match":
            self.delete_match_frame.grid(row=3,column=0,columnspan=2)
            self.Grid_delete_match()
            self.button_list.configure(command=self.Delete_Match)
              
        self.Delete_Entry()
    # 0= own goal
    # 1= goal
    # 2= yellow card
    # 3= red card
    

    def Insert_New_Match(self):
        try:
            match=[]
            ID=self.ID_entry1.get()
            match.append(ID)
            teamA=self.teamA_entry.get()
            match.append(teamA)
            teamB=self.teamB_entry.get()
            match.append(teamB)
            score=self.score_entry1.get()
            match.append(score)
            date=self.date_entry1.get()
            match.append(date)
            time=self.time_entry1.get()
            match.append(time)
            
            if ID == '' or teamA=="" or teamB=="" or score=="" or date=="" or time=="":
                self.label_notice["text"] = "Field cannot be empty"
                return

            option=INSERT_NEW_MATCH
            client.sendall(option.encode(FORMAT))

            for data in match:
                data=str(data)
                print(data,end=' ')
                client.sendall(data.encode(FORMAT))
                client.recv(1024)
            
            self.Delete_Entry()
            status = client.recv(1024).decode(FORMAT)
            if status == "success":
                self.label_notice["text"] = "success"
                return True
            elif status =="failed":
                self.label_notice["text"] = "failed"
                return False
        except:
            self.label_notice["text"] = "Error"

            

    def Update_Score(self):
        try:
            match=[]
            
            ID=self.ID_entry2.get()
            match.append(ID)
            score=self.score_entry2.get()
            match.append(score)
            if ID == "" or score =="":
                self.label_notice["text"] = "Field cannot be empty"
                return
            
            option=UPDATE_SCORE
            client.sendall(option.encode(FORMAT))
            for data in match:
                data=str(data)
                client.sendall(data.encode(FORMAT))
                client.recv(1024)
            
            self.Delete_Entry()
            status = client.recv(1024).decode(FORMAT)
            if status == "success":
                self.label_notice["text"] = "success"
                return True
            elif status =="failed":
                self.label_notice["text"] = "failed"
                return False
        except:
            self.label_notice["text"] = "Error"

    def Update_Date_Time(self):
        try:
            match= []
            ID=self.ID_entry3.get()
            match.append(ID)
            date=self.date_entry3.get()
            match.append(date)
            time= self.time_entry3.get()
            match.append(time)

            if ID == "" or date == "" or time == "":
                self.label_notice["text"] = "Field cannot be empty"
                return
            
            option = UPDATE_DATETIME
            client.sendall(option.encode(FORMAT))

            for data in match:
                data =str(data)
                client.sendall(data.encode(FORMAT))
                client.recv(1024)
            
            self.Delete_Entry()
            status = client.recv(1024).decode(FORMAT)
            if status == "success":
                self.label_notice["text"] = "success"
                return True
            elif status =="failed":
                self.label_notice["text"] = "failed"
                return False
        except:
            self.label_notice["text"] = "Error"
         

    def Insert_Detail(self):
        try:
            match = []

            ID=self.Did_entry.get()
            match.append(ID)

            Team=self.Dteam_entry.get()
            match.append(Team)

            Event=self.Event_entry.get()
            match.append(Event)

            Player=self.player_entry.get()
            match.append(Player)

            Min=self.Dtime_entry.get()
            match.append(Min)

            for data in match:
                if data  == "":
                    self.label_notice["text"] = "Field cannot be empty"
                    return False
                
            
            option = INSERT_DETAIL
            client.sendall(option.encode(FORMAT))

            for data in match:
                data =str(data)
                client.sendall(data.encode(FORMAT))
                client.recv(1024)
            
            self.Delete_Entry()
            status = client.recv(1024).decode(FORMAT)
            if status == "success":
                self.label_notice["text"] = "success"
                return True
            elif status == "failed":
                self.label_notice["text"] = "failed"
                return False
        except:
             self.label_notice["text"] = "Error"
             

    def Delete_Match(self):
        try:

            ID = self.ID_entry4.get()

            if ID == "":
                self.label_notice["text"] = "Field cannot be empty"
                return False
            
            option = DELETE_MATCH
            client.sendall(option.encode(FORMAT))

            data = str(ID)
            client.sendall(data.encode(FORMAT))
            client.recv(1024)
            
            self.Delete_Entry()
            status = client.recv(1024).decode(FORMAT)
            if status == "success":
                self.label_notice["text"] = "success"
                return True
            elif status == "failed":
                self.label_notice["text"] = "failed"
                return False
        except:
             self.label_notice["text"] = "Error"


#GLOBAL socket initialize
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = (HOST, PORT)

client.connect(server_address)


app = SoccerNews_App()



#main
try:
    app.mainloop()
except:
    print("Error: server is not responding")
    client.close()

finally:
    client.close()

