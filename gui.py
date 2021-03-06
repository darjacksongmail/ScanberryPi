#!/usr/bin/python3.9
#-*- coding: utf-8 -*-
"""
////////////////////////////////////////////////////////////////////////////////////////////////////////

This file contains all the GUI build and logic surrounding button events and menus.
Threads are begun for longer operations such as scanning the drive or waiting for a user to insert a USB drive

Date:08/04/22
Author: Darren Jackson
file gui.py

////////////////////////////////////////////////////////////////////////////////////////////////////////


"""

#Import required libraries for use

from tkinter import *
from tkinter import ttk
from tkinter.messagebox import showerror, showwarning, showinfo
from tkinter import *
from PIL import ImageTk
from PIL import Image
import PIL
import tkinter.font as font
import time
import os
import USB
import threading



""" Create Threads for scan Processes"""
class myThread(threading.Thread):
      def __init__(self,threadID,drive,op):
          threading.Thread.__init__(self)
          self.threadID = threadID
          self.dev = drive
          self.op = op

      def run(self):
          print("Starting the Thread")
          print (self.dev)
          os.nice(-3)
          if self.op == "scan":
             self.dev.scan_usb("scan")
          elif self.op=="scanandremove":
              self.dev.scan_usb("scanremove")
          elif self.op == "insertusb":
              self.dev.insertusb()
          #progress_bar.stop()
          if self.op == "scan" or self.op == "scanandremove":
              showinfo('Scan Complete', 'USB Scan Complete')
          else:
              showinfo('Usb Inserted', 'USB Drive Inserted')
          print("Ending the Thread")

""" Check Thread is alive """
def check_thread(th,win1):
    if not th.is_alive():
        win1.destroy()
        results_win("summary")
        return
    if th.is_alive():
        win1.lift()
    win1.after(5, check_thread, th, win1)

""" Check Insert USB Thread is alive """
def check_thread_insert(th,win1):
    if not th.is_alive():
        win1.destroy()
        return
    if th.is_alive():
        win1.lift()
    win1.after(2, check_thread_insert, th, win1)


"""Function to shutdown the device"""
def shutdown():
    print("Shutting Down")
    time.sleep(5)
    os.system("sudo shutdown -h now")



""" Function to Return results files"""
def getResults(res_type):
    data = "No Data"
    if res_type=="summary":
       file = open("/opt/ScanberryPi/logs/scanReport.log")
       data = file.read()
       file.close()
    elif res_type=="history":
       file = open("/opt/ScanberryPi/logs/scanHistory.log")
       data = file.read()
       file.close()
    return data

""" Results Window takesd in a parameter to open the window for summary or history"""
def results_win(ex):
    pop_win = Toplevel()
    malwareCount = 0

    myFont = font.Font(family='Calibri',size=10)
    myFonth = font.Font(family='Calibri',size=13)
    pop_win["bg"]="black"

    pop_win.columnconfigure(1,weight=2)
    pop_win.columnconfigure(2,weight=2)
    pop_win.columnconfigure(3,weight=2)
    pop_win.columnconfigure(4,weight=2)
    pop_win.rowconfigure(7,weight=1)


    pop_win.title("Finshed Scanning USB : Results")
    pop_win.geometry('800x400+0+0')
    Label(pop_win, text="Finshed Scanning USB Drive: Results", bg='black', fg='white', font=myFonth).grid(row=0,column=1,columnspan=6)

    sb = Scrollbar(pop_win,orient=VERTICAL)
    sb.grid(row=1,column=3,columnspan=3,sticky='ns')

    """ Text area to output scan results and manipulate the results to highlight malware found"""
    textarea = Text(pop_win, height = 18 , width = 85, wrap="none",font=myFont)
    textarea.configure(bg='black',fg='#7FFF00')
    if ex == "summary":
       with open("/opt/ScanberryPi/logs/scanReport.log","r") as file:
          for line in file:
             if "Malware Found" in line:
                malwareCount += 1
                textarea.tag_config('warning', background="#E4D00A", foreground="black")
                textarea.insert(END,line,'warning')
             else:
                textarea.insert(END,line)
    elif ex == "history":
       with open("/opt/ScanberryPi/logs/scanHistory.log","r") as file1:
          for line in file1:
             if "Malware Found" in line:
                malwareCount += 1
                textarea.tag_config('warning', background="#E4D00A", foreground="black")
                textarea.insert(END,line,'warning')
             else:
                textarea.insert(END,line)
    elif ex == "clear":
       os.system("sudo truncate -s 0 /opt/ScanberryPi/logs/scanHistory.log")
       print("History File Cleared")
       textarea.insert(END,"NO RESULTS TO SHOW")
    else:
       textarea.insert(END,"NO RESULTS TO SHOW")

    print("#Malware Found: "+ str(malwareCount))
    textarea.config(state=DISABLED)
    textarea.config(yscrollcommand=sb.set)
    sb.config(command=textarea.yview)
    textarea.grid(row=1,column=2)

    Label(pop_win, text="Total Malware Found in "+ex+" "+str(malwareCount), bg='black', fg='white', font=myFonth).grid(row=2,column=2,columnspan=2)


    w1_exit = Button(pop_win, text="  Close  \n", command=pop_win.destroy ,bg='#B22222', fg='#ffffff',activebackground="yellow")
    w1_exit['font'] = myFont
    w1_exit.grid(row=2,column=3,columnspan=2,padx=20,pady=20)

    pop_win.after(150)
    pop_win.attributes('-topmost',True)


""" Function to get button event and object and processes the button event based on parameters passed to function"""
def button_event(button,device):
    if button == "VFAT":
       butev = device.format_usb("VFAT")
       print("Button Event: "+butev)
       if butev == "VFAT":
          showinfo('USB Formatted', 'USB now has a file system type of: '+butev)
       else:
           showerror('USB not Formatted', 'USB Was unable to format drive to: '+butev)
    elif button == "FAT32":
       butev = device.format_usb("FAT32")
       if butev == "FAT32":
          showinfo('USB Formatted', 'USB now has a file system type of: '+butev)
       else:
          showerror('USB not Formatted', 'USB Was unable to format drive to: '+butev)

    elif button == "EXFAT":
       butev = device.format_usb("EXFAT")
       if butev == "EXFAT":
          showinfo('USB Formatted', 'USB now has a file system type of: '+butev)
       else:
          showerror('USB not Formatted', 'USB Was unable to format drive to: '+butev)

    elif button == "NTFS":
       butev = device.format_usb("NTFS")
       if butev == "NTFS":
          showinfo('USB Formatted', 'USB now has a file system type of: '+butev)
       else:
          showerror('USB not Formatted', 'USB Was unable to format drive to: '+butev)

    elif button == "INSERT":
       butev = device.mountUSB()
       if butev == "INSERT":
          showinfo('USB Inserted', 'USB was inserted: '+butev)
       else:
          showerror('USB Inserted', 'USB Was unable to mount drive: '+butev)

    elif button == "EJECT":
       butev = device.ejectUSB() 
       if butev == "EJECTED":
          showinfo('USB Ejected', 'USB has been ejected: '+butev)
       else:
          showerror('USB Ejected', 'USB Was unable to Eject: '+butev)
    else:
       showerror('Error', 'Error Please try again: '+butev)


"""Function to Create new windows within the main loop"""
def new_win(win, msg, title, device):
    " new window"
    try:
        if win1.state() == "normal": win1.focus()
    except NameError as e:
        print(e)
        win1 = Toplevel(win)
        myFont = font.Font(family='Calibri',size=20)
        myFonth = font.Font(family='Calibri',size=28)
        win1["bg"] = "black"

        s = ttk.Style()
        s.theme_use('clam')
        s.configure("red.Horizontal.TProgressbar", troughcolor ='blue', background='red')


        if msg == "ScanUsb":
            if device.isDeviceConnected():

               print("Scan Usb")
               win1.title(msg)

               win1.columnconfigure(1,weight=2)
               win1.columnconfigure(2,weight=2)
               win1.columnconfigure(3,weight=2)
               win1.columnconfigure(4,weight=2)
               win1.rowconfigure(10,weight=2)


               lb = Label(win1, text="Scan USB Drive",bg='black',fg='white', font=myFonth)
               lb.grid(row=0,column=1,columnspan=6)

               w1_scan_button = Button(win1, text="Scan\n & Detect", command= lambda:new_win(win1,"scanning","scanning",device),bg='#009900', fg='#ffffff',activebackground="yellow")
               w1_scan_button['font'] = myFont
               w1_scan_button.grid(row=1,column=2)
               w1_scan_button.config(padx=30,pady=30)

               w1_scan_button_remove = Button(win1, text=" Remove \n Malware", command= lambda:new_win(win1,"scanningandremove","scanningandremove",device),bg='#009900', fg='#ffffff',activebackground="yellow")
               w1_scan_button_remove['font'] = myFont
               w1_scan_button_remove.grid(row=1,column=3)
               w1_scan_button_remove.config(padx=30,pady=30)

               lb1 = Label(win1, text="",bg='black',fg='white', font=myFonth)
               lb1.grid(row=2,column=0,columnspan=6)

               res_button = Button(win1, text="Get Last Scan\n Results", command= lambda:results_win("summary"),bg='#0052cc', fg='#ffffff',activebackground="yellow")
               res_button['font'] = myFont
               res_button.grid(row=3,column=2)
               res_button.config(padx=20,pady=20)

               res1_button = Button(win1, text="Get Last Scans\n History", command= lambda:results_win("history"),bg='#0052cc', fg='#ffffff',activebackground="yellow")
               res1_button['font'] = myFont
               res1_button.grid(row=3,column=3)
               res1_button.config(padx=20,pady=20)

               res2_button = Button(win1, text="Clear \n History", command= lambda:results_win("clear"),bg='#0052cc', fg='#ffffff',activebackground="yellow")
               res2_button['font'] = myFont
               res2_button.grid(row=3,column=4)
               res2_button.config(padx=20,pady=20)

               lb1 = Label(win1, text="",bg='black',fg='white', font=myFonth)
               lb1.grid(row=4,column=0,columnspan=6)

               e_button = Button(win1, text="Exit\n", command=win1.destroy,bg='#B22222', fg='#ffffff',activebackground="yellow")
               e_button['font'] = myFont
               e_button.grid(row=5,column=3)
               e_button.config(padx=20,pady=20)


               win1.attributes('-fullscreen', True)
            else:
               showerror('NO USB Detected', 'No USB Drive Detected please insert a USB to access this option\n and try again using the insert method')


        elif msg == "scanning":
             print("Scanning USB")
             win1.title("Scanning USB")
             win1.geometry('400x250+100+100')
             Label(win1, text="Scanning USB Drive",bg='black',fg='white', font=myFonth).grid(row=0,column=3)

             #start progress bar
             progress_bar = ttk.Progressbar(win1, style="red.Horizontal.TProgressbar", orient="horizontal",
             mode="indeterminate", takefocus=True, length=320)
             progress_bar.place(x=40, y=80)
             progress_bar.start()


             thread1 = myThread(1,device,"scan")
             thread1.start()
             win1.after(5, check_thread, thread1, win1)
             win1.after(0, lambda: win1.attributes("-topmost", False))

        elif msg == "Insert USB":
             print("Please Insert USB")
             #win1.iconbitmap('media/USB.ico')
             win1.title("Insert USB")
             win1.geometry('400x250+100+100')

             Label(win1, text="Insert USB Drive",bg='black',fg='white', font=myFonth).grid(row=0,column=3)

             #start progress bar
             progress_bar = ttk.Progressbar(win1, style="red.Horizontal.TProgressbar", orient="horizontal",
             mode="indeterminate", takefocus=True, length=320)
             progress_bar.place(x=40, y=80)
             progress_bar.start()


             thread1 = myThread(1,device,"insertusb")
             thread1.start()
             win1.after(5, check_thread_insert, thread1, win1)
             win1.after(0, lambda: win1.attributes("-topmost", False))

        elif msg == "results":
             win1.title("Finshed Scanning USB : Results")
             win1.geometry('500x350+100+100')

             Label(win1, text="Finshed Scanning USB Drive: Results", font=myFonth).grid(row=0,column=3)
             Text(win, height = 30 , width = 53).grid(row=1,column=0)
             results = getResults()
             Text.insert(results)

             w1_exit = Button(win1, text="Stop", command= lambda:win1.destroy ,bg='#B22222', fg='#ffffff',activebackground="yellow")
             w1_exit['font'] = myFont
             w1_exit.grid(row=3,column=2)

             win1.attributes('-topmost',True)

        elif msg == "scanningandremove":
             print("Scanning USB \n and removing")
             #win1.iconbitmap('media/USB.ico')
             win1.title("Scanning USB")
             win1.geometry('400x250+100+100')

             Label(win1, text="Scanning USB Drive \n and Removing", font=myFonth, bg="black", fg="white").grid(row=0,column=3)

             #start progress bar
             progress_bar = ttk.Progressbar(win1,style="red.Horizontal.TProgressbar", orient="horizontal",
             mode="indeterminate", takefocus=True, length=320)
             progress_bar.place(x=40, y=100)
             progress_bar.start()

             thread1 = myThread(1,device,"scanandremove")
             thread1.start()
             win1.after(5, check_thread, thread1, win1)
             win1.after(0, lambda: win1.attributes("-topmost", False))
             win1.attributes('-topmost',True)



        elif msg == "InsertUsb":
             print("Scan Usb")
             win1.title(msg)
             #win1.geometry("300x300+500+200")
             print("Insert Usb")

             win1.columnconfigure(1,weight=2)
             win1.columnconfigure(2,weight=2)
             win1.columnconfigure(3,weight=2)
             win1.columnconfigure(4,weight=2)
             win1.rowconfigure(10,weight=2)

             win1.title("Insert USB")
             lb = Label(win1, text="Please Insert USB")
             lb.pack()

             image = Image.open("media/RaspberryPi_logo.png")
             resize = image.resize((200,200),Image.ANTIALIAS)
             r_image = ImageTk.PhotoImage(resize)
             insusb_label = Label()
             insusb_label.config(image=r_image, bg='#000000',pady=250)
             insusb_label.pack()

             lb = Label(win1, text=msg)
             lb.pack()

             win1.focus_set()
             win1.grab_Set()
             win1.attributes('-fullscreen', True)



        elif msg == "FormatUsb":
             if device.isDeviceConnected():  
                print("FormatUSB")
                win1.title(msg)

                win1.columnconfigure(1,weight=2)
                win1.columnconfigure(2,weight=2)
                win1.columnconfigure(3,weight=2)
                win1.columnconfigure(4,weight=2)
                win1.rowconfigure(10,weight=2)

                #win1.geometry("300x300+500+200")
                lb = Label(win1,font=myFonth,text="Format USB Drive",bg='black',fg='white')
                lb.grid(row=0,column=1,columnspan=6)


                format = device.check_format()
                Format_button = Button(win1, text="Check Format", command= lambda: showinfo('USB Format', 'USB has a file system type of: '+ str(format)),bg='#009900', fg='#ffffff',activebackground="yellow")
                Format_button['font'] = myFont
                Format_button.grid(row=1,column=1,columnspan=6)

                lb1 = Label(win1, text="",bg='black',fg='white', font=myFonth)
                lb1.grid(row=2,column=0,columnspan=6)

                vfat_button = Button(win1, text="VFAT \n Format", command= lambda: button_event("VFAT",device),bg='#0052cc', fg='#ffffff',activebackground="yellow")
                vfat_button['font'] = myFont
                vfat_button.grid(row=3,column=1,padx=20,pady=20)

                fat32_button = Button(win1, text="FAT32 \n  Format", command= lambda: button_event("FAT32",device),bg='#0052cc', fg='#ffffff',activebackground="yellow")
                fat32_button['font'] = myFont
                fat32_button.grid(row=3,column=2,padx=20,pady=20)

                exfat_button = Button(win1, text="exFAT \n Format", command= lambda: button_event("EXFAT",device),bg='#0052cc', fg='#ffffff',activebackground="yellow")
                exfat_button['font'] = myFont
                exfat_button.grid(row=3,column=3,padx=20,pady=20)

                ntfs_button = Button(win1, text="NTFS \n Format", command= lambda: button_event("NTFS",device),bg='#0052cc', fg='#ffffff',activebackground="yellow")
                ntfs_button['font'] = myFont
                ntfs_button.grid(row=3,column=4,padx=10,pady=10)

                lb1 = Label(win1, text="",bg='black',fg='white', font=myFonth)
                lb1.grid(row=4,column=0,columnspan=6)

                #exit button and its attributes
                e_button = Button(win1, text="Exit\n", command=win1.destroy,bg='#B22222', fg='#ffffff',activebackground="yellow")
                e_button['font'] = myFont
                e_button.grid(row=4,column=1,columnspan=6,padx=10,pady=10)
                win1.attributes('-fullscreen', True)
             else:
               showerror('No USB Detected', 'Please insert a USB driver to access this option,\n Using the insert USB method')

        elif msg == "Eject/InsertUsb":
            print("Eject/Insert USB")
            win1.title(msg)
            #win1.geometry("300x300+500+200")
            win1.columnconfigure(1,weight=2)
            win1.columnconfigure(2,weight=2)
            win1.columnconfigure(3,weight=2)
            win1.columnconfigure(4,weight=2)
            win1.rowconfigure(10,weight=2)

            lb = Label(win1, text=msg, font=myFonth,bg='black',fg='white')
            lb.grid(row=0,column=1,columnspan=6)

            lb1 = Label(win1, text="",bg='black',fg='white', font=myFonth)
            lb1.grid(row=1,column=0,columnspan=6)

            #insert_button = Button(win1, text="Insert USB", command= lambda: button_event("INSERT",device),bg='#0052cc', fg='#ffffff',activebackground="yellow")
            insert_button = Button(win1, text="Insert \n  USB", command=  lambda:new_win(win1,"Insert USB","Insert USB",device),bg='#0052cc', fg='#ffffff',activebackground="yellow")
            insert_button['font'] = myFont
            insert_button.grid(row=2,column=3)

            eject_button = Button(win1, text="Eject \n  USB", command= lambda: button_event("EJECT",device) ,bg='#0052cc', fg='#ffffff',activebackground="yellow")
            #eject_button = Button(win1, text="Eject USB", command= lambda:new_win(win1,"INSERT","insertusb",device) ,bg='#0052cc', fg='#ffffff',activebackground="yellow") 
            eject_button['font'] = myFont
            eject_button.grid(row=2,column=2)

            lb1 = Label(win1, text="",bg='black',fg='white', font=myFonth)
            lb1.grid(row=3,column=0,columnspan=6)


            e_button = Button(win1, text="\n Exit \n", command=win1.destroy,bg='#B22222', fg='#ffffff',activebackground="yellow")
            e_button['font'] = myFont
            e_button.grid(row=4,column=0,columnspan=6)
            win1.attributes('-fullscreen', True)
        else:
            win1.title(msg)
            #win1.geometry("300x300+500+200")
            lb = Label(win1, text=msg)
            lb.pack()
            #exit button and its attributes
            e_button = Button(win1, text="Exit", command=win1.destroy,bg='#B22222', fg='#ffffff',activebackground="yellow")
            e_button['font'] = myFont
            e_button.pack()
            win1.attributes('-fullscreen', True)

        win.bind('<Escape>', lambda e: win.destroy())
        win.focus()
        win.update()



""" Main menu loop"""

def main_menu(device):
    
    count = 0
    window = Tk()
    window.geometry("720x270")

    if device.isDeviceConnected():
    	connected = "True"
    else:
        connected = "False"

    #Initialise Main Window of Program
    window.title("USB Scanberry Pi")
    window.config(padx=10,pady=10)
    window.configure(background="black")
    #window.iconbitmap('media/USB.ico')

    #Grid layout configuration
    window.columnconfigure(1,weight=2)
    window.columnconfigure(2,weight=2)
    window.columnconfigure(3,weight=2)
    window.columnconfigure(4,weight=2)
    window.rowconfigure(7,weight=4)

    #Program Title and image
    myFont = font.Font(family='Calibri',size=20)
    myFonth = font.Font(family='Calibri',size=28)
    program_label = Label()
    program_label.config(text="Welcome to Scanberry Pi",pady=20,padx=20,font=myFonth,fg='#ffffff',bg='#000000')
    program_label.grid(row=0,column=0,columnspan=6)

    image = Image.open("media/RaspberryPi_logo.png")

    resize = image.resize((200,200),Image.ANTIALIAS)

    r_image = ImageTk.PhotoImage(resize)
    logo_label = Label()
    logo_label.config(image=r_image, bg='#000000',pady=250)
    logo_label.grid(row=1,column=0,columnspan=6)


    #Scan Buttons and its attributes
    #scan_button = ttk.Button(window, text="Scan\n USB", command= new_win('ScanUSB','Scan USB Drive'))
    scan_button = Button(text="Scan\n USB",command =lambda: new_win(window, 'ScanUsb','Scan USB drive',device), bg='#009900', fg='#ffffff',activebackground="yellow")
    scan_button['font'] = myFont
    scan_button.grid(column=2,row=4)
    scan_button.config(padx=30,pady=30)


    #Format button and its attributes
    format_button = Button(text="Format\n USB",command =lambda: new_win(window, 'FormatUsb','Format USB drive',device), bg='#0052cc', fg='#ffffff',activebackground="yellow")
    format_button['font'] = myFont
    format_button.grid(column=3,row=4)
    format_button.config(padx=30,pady=30)

    #mount button and its attributes
    mount_button = Button(text="Eject/\nInsert USB",command =lambda: new_win(window, 'Eject/InsertUsb','Eject/Insert USB drive',device), bg='#0052cc', fg='#ffffff',activebackground="yellow")
    mount_button['font'] = myFont
    mount_button.grid(column=4,row=4)
    mount_button.config(padx=30,pady=30)


    #exit button and its attributes
    #exit_button = Button(window, text="Exit", command=lambda: window.destroy(),bg='#B22222', fg='#ffffff',activebackground="yellow")
    exit_button = Button(window, text="Exit", command = lambda: shutdown(),bg='#B22222', fg='#ffffff',activebackground="yellow")
    exit_button['font'] = myFont
    exit_button.grid(column=5,row=7,rowspan=3)
    exit_button.config(padx=10,pady=10)


    #exit button and its attributes
    maint_button = Button(window, text="M", command=lambda: window.destroy(),bg='#000000', fg='#ffffff',activebackground="orange")
    maint_button['font'] = myFont
    maint_button.grid(column=5,row=0)
    maint_button.config(padx=0,pady=0)

    # Open in Full Screen
    window.bind('<Escape>', lambda e: window.destroy())
    window.attributes('-fullscreen', True)

    # Main Program Loop
    window.mainloop()

