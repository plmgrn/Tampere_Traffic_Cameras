"""
Otto Palmgren
GUI interface for Tampere traffic cams
Created using Tampere traffic cam API


Very simple gui, created for fun
Data storaging isn't optimized as the name
and the camera picture should be tied together
to avoid any problems with misaligning.
(which might be possible at the moment)
"""

#TODO Optimize code for speed
#
#TODO Optimize import statements for speed
#
#TODO create loading sequence to avoid exe not answering
#
#TODO certifications


import json
import requests
from requests import Timeout
import datetime
from tkinter import *
import PIL
from PIL import ImageTk, Image
from io import BytesIO

root = Tk()
root.geometry('630x450')
root.title(f"Tampere {datetime.datetime.now()}")
root.iconbitmap("camera_icon.ico")
root.configure(bg='#555959')
root.resizable(False, False)
print("initialized root")


picindex = 0

def main(picindex):
    [namelist, urlist] = fetch()
    print("fetched")
    list = data(urlist)
    print("data parsed")

    pic = ImageTk.PhotoImage(Image.open(BytesIO(list[0])))
    pLabel = Label(root, image=pic)
    pLabel.place(x=0, y=0)
    print('created pic label')

    lastbutton = Button(root, text='Prev', command=lambda: loadprev(pLabel, list, namelabel, namelist), bd=3,
                        bg='LightGray')
    lastbutton.place(rely=0.9, relx=0.15, anchor='center')

    namelabel = Label(root, text='', font=('Helvetica 15 bold'), bg='white', bd=2)
    namelabel.place(rely=0.9, relx=0.5, anchor='center')
    print("created name label")

    loadpic(pLabel, list, namelabel, namelist)
    loadname(namelabel, namelist)
    print('loaded all label contents')

    nextbutton = Button(root, text='Next', command=lambda: loadpic(pLabel, list, namelabel, namelist), bd=3,
                        bg='LightGray')
    nextbutton.place(rely=0.9, relx=0.85, anchor='center')
    print('ALL DONE')

    mainloop()


def loadname(namelabel, namelist):
    global picindex
    name = namelist[picindex]
    namelabel.configure(text=name.upper())
    namelabel.name = name


def loadprev(pLabel, list, namelabel, namelist):
    global picindex
    try:
        picindex -= 1
        pic = ImageTk.PhotoImage(Image.open(BytesIO(list[picindex])))
        pLabel.configure(image=pic)
        pLabel.image = pic
        loadname(namelabel, namelist)
    except PIL.UnidentifiedImageError:
        loadprev(pLabel, list, namelabel, namelist)
    except IndexError:
        picindex += 1
        return


def loadpic(pLabel, list, namelabel, namelist):
    global picindex
    try:
        picindex += 1
        pic = ImageTk.PhotoImage(Image.open(BytesIO(list[picindex])))
        pLabel.configure(image=pic)
        pLabel.image = pic
        loadname(namelabel, namelist)
    except PIL.UnidentifiedImageError:
        loadpic(pLabel, list, namelabel, namelist)
    except IndexError:
        picindex -= 1
        return


# the function that requests the data from the
# TAMPERE API (traffic cameras)
# return value is list of camera location names AND list of camera image urls
def fetch():
    # time = datetime.datetime.now()

    # try to connect to the API
    try:
        response = requests.get(f'https://traffic-cameras.tampere.fi/api/v1/cameras', timeout=20)
    except Timeout:
        print('timeout')
        return 0

    if response:
        print('success')
    else:
        print('fetch 404')
        print((response.status_code))
        return 0

    # this parses the requested data JSON [str] into a maneuverable data listish format
    responsedata = json.loads(response.text)

    # Fetching the dates of the cameras to filter out ones that don't work
    datelist = []
    i = 0
    while i < len(responsedata["results"]):
        date = responsedata["results"][i]['cameraPresets'][0]['latestPictureTimestamp']
        d1 = datetime.datetime.strptime(date, "%Y-%m-%dT%H:%M:%S%z")
        #check the dates of the pictures
        #print(d1.date())
        datelist.append(d1.date())
        i += 1

    datelist.sort()
    datelist.reverse()


    #print('----------------------------DATELIST REVERSE------------------------------')
    #for i in datelist:
        #print(i)
    #print(datelist[0])


    # the latest date in the list of dates
    CorrectDateTime = datelist[0]

    # The list making iteration
    # collects the url:s of the lists in urlist
    # and the names of the cameralocations in namelist
    urlist = []
    namelist = []
    j = 0

    print('\n\n************************\n** BROKEN CAMERA INFO **\n************************')
    while j < len(responsedata["results"]):
        picdate = responsedata["results"][j]['cameraPresets'][0]['latestPictureTimestamp']
        picdate = datetime.datetime.strptime(picdate, "%Y-%m-%dT%H:%M:%S%z")
        picdate = picdate.date()
        if picdate != CorrectDateTime:
            print(f'kamera {responsedata["results"][j]["cameraPresets"][0]["presetId"]} näyttää aikaa {picdate}')
        else:
            namelist.append(responsedata["results"][j]["cameraPresets"][0]["presetId"])
            urlist.append(responsedata["results"][j]['cameraPresets'][0]['imageUrl'])
        j += 1

    print('\n\n')

    return namelist, urlist


# Input is the list of picture url:s
# data() parses the url into
# Output is usable data from url:s
def data(urlist):
    returnlist = []
    for i in urlist:
        r = requests.get(i)
        imagedata = r.content
        returnlist.append(imagedata)
    return returnlist


if __name__ == '__main__':
    main(picindex)
