import urllib.request
import re
from pytube import YouTube
import os
import imageio
from moviepy.editor import *
import sys
import streamlit as st
import zipfile
import smtplib, ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

st.set_page_config(page_title="Puranjay's Mashup", layout="wide", initial_sidebar_state="expanded")  
st.title("MASHUP your favourite artist's songs!")
st.markdown("Puranjay Singh, 102003384")

name = st.text_input("Enter name of the singer:")
num_videos =  st.text_input("Enter the no. of videos:")
cut_duration = st.text_input("Enter cut duration(in seconds):")
email = st.text_input("Enter your email address:")
submit_button = st.button("Submit")
output_file = "output.mp3"

if submit_button:
    if name is "":
        st.error("Please enter the artist name.")
    else:
        if num_videos is "":
            st.error("Please enter the number of videos.")
        else:
            if cut_duration is "":
                st.error("Please enter the cut duration.")
            else:
                if email is "":
                    st.error("Please enter the email ID")
                else:
                    if "@" not in email:
                        st.error("Please enter a valid email ID")
                    else:
                        st.balloons()


def get_videos(singer):
    html = urllib.request.urlopen("https://www.youtube.com/results?search_query=" + singer)
    video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())
    temp_videos = ["https://www.youtube.com/watch?v=" + video_id for video_id in video_ids]
    print(len(temp_videos))
    #make list values unique
    temp_videos = list(set(temp_videos))
    print(len(temp_videos))
    videos = []
    idx = 1
    for video in temp_videos:
        if idx > num_of_videos:
            break
        yt = YouTube(video)
        if yt.length/60 < 5.00:
            videos.append(video)
            idx += 1
    return videos


def download_video(video):
   
    downloadPath = 'videos/'
    if not os.path.exists(downloadPath):
        os.makedirs(downloadPath)
    
    yt = YouTube(video)
    try :
        yt.streams.first().download(downloadPath)
    except :
        print("Error in downloading video")

def convert_vid_to_audio():
    SAVE_PATH = os.getcwd() + '/'
    #get paths of videos stored in videos folder using os module
    path = os.getcwd()+'/videos/'
    print(path)
    ds_store = path + ".DS_Store"
    if os.path.exists(ds_store):
        os.remove(ds_store)
    fileList = os.listdir(path)
    print(fileList)
    idx = 1
    if not os.path.exists(SAVE_PATH + 'audios/'):
        os.makedirs(SAVE_PATH + 'audios/')
    for file in fileList:
        try:
            print(file)
            video = VideoFileClip(path+file).subclip(0, int(cut_duration))
            video.audio.write_audiofile(SAVE_PATH + '/audios/' + str(idx) + ".mp3")
            video.close()
            os.remove(path+file)
            idx += 1
        except:
            continue

def mergeAudios():
    SAVE_PATH = os.getcwd() + '/'
    final_wav_path = SAVE_PATH + "audios/" + output_file
    ds_store = SAVE_PATH + "/audios/.DS_Store"
    if os.path.exists(ds_store):
        os.remove(ds_store)
    if os.path.exists(final_wav_path):
        os.remove(final_wav_path)
    for file in os.listdir(SAVE_PATH + "/audios/"):
        if file.endswith(".zip"):
            os.remove(SAVE_PATH + "/audios/" + file)
    wavs = os.listdir(SAVE_PATH + "/audios/")
    
    final_clip = concatenate_audioclips([AudioFileClip(SAVE_PATH + "/audios/"+wav) for wav in wavs])
    final_clip.write_audiofile(final_wav_path)
    final_clip.close()
    print("Done merging wavs to " + final_wav_path)

def zipAudio():
    SAVE_PATH = os.getcwd() + '/'
    final_wav_path = "audios/" + output_file
    zip_file = final_wav_path + ".zip"
    with zipfile.ZipFile(zip_file, 'w') as myzip:
        myzip.write(final_wav_path)

def sendEmail(email, result_file) : 
    port = 465  # For SSL
    smtp_server = "smtp.gmail.com"
    sender_email = "psingh12_be20@thapar.edu" 
    PASSWORD = "lxreijnqjiaghtti"  # Enter your address
    receiver_email = email  # Enter receiver address

        # Create a multipart message and set headers
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = "Mashup Audio File"

        # Add body to email
    message.attach(MIMEText("Please find the attached zip file.", "plain"))

        # Open PDF file in bynary
    zip_file = "audios/" + output_file + ".zip"
    
    part = MIMEBase('application', "octet-stream")
    part.set_payload( open(zip_file,"rb").read() )
        # Encode file in ASCII characters to send by email    
    encoders.encode_base64(part)
    
        # Add header with pdf name
    part.add_header(
        "Content-Disposition",
        f"attachment; filename={output_file+'.zip'}",
    )
    
        

        # Add attachment to message and convert message to string
    message.attach(part)
    text = message.as_string()

        # Log in to server using secure context and send email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_email, PASSWORD)
        server.sendmail(sender_email, receiver_email, text)
def clearFiles():
    path = os.getcwd()+'/audios/'
    # path2 = os.getcwd()+'/videos/'
    if os.path.exists(path):
        fileList = os.listdir(path)
        for file in fileList:
            os.remove(path+file)
        # fileList = os.listdir(path2)
        # for file in fileList:
        #     os.remove(path2+file)
if submit_button:
    if name == '' or num_videos == '' or cut_duration == '' or output_file == '' or email == '':
        st.warning('Please enter all the fields')
    else:
        st.success('Please wait while we process your request')
        if output_file.count('.') == 0:
            output_file += '.mp3'
        output_file.split('.')[-1] = 'mp3'
        singer = name.replace(' ', '+')
        num_of_videos = int(num_videos)
        clearFiles()
        videos = get_videos(singer)
        for video in videos:
            # st.write(video)
            download_video(video)
        convert_vid_to_audio()
        mergeAudios()
        zipAudio()
        sendEmail(email, output_file)
        st.success("Output audio file has been zipped and mailed to your email ID.")
        
