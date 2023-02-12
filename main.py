import urllib.request
import re
from pytube import YouTube
import os
from moviepy.editor import *
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


def get_videos(singer):
    html = urllib.request.urlopen("https://www.youtube.com/results?search_query=" + singer)
    video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())
    temp_videos = ["https://www.youtube.com/watch?v=" + video_id for video_id in video_ids]
    temp_videos = list(set(temp_videos))
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
        print("Error! Could not download video.")

def convert_vid_to_audio():
    SAVE_PATH = os.getcwd() + '/'
    path = os.getcwd()+'/videos/'
    ds_store = path + ".DS_Store"
    if os.path.exists(ds_store):
        os.remove(ds_store)
    fileList = os.listdir(path)
    idx = 1
    if not os.path.exists(SAVE_PATH + 'audios/'):
        os.makedirs(SAVE_PATH + 'audios/')
    for file in fileList:
        try:
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
    print("Merging has been done at:" + final_wav_path)

def zipAudio():
    SAVE_PATH = os.getcwd() + '/'
    final_wav_path = "audios/" + output_file
    zip_file = final_wav_path + ".zip"
    with zipfile.ZipFile(zip_file, 'w') as myzip:
        myzip.write(final_wav_path)

def sendEmail(email, result_file) : 
    port = 465  
    smtp_server = "smtp.gmail.com"
    sender_email = "psingh12_be20@thapar.edu" 
    PASSWORD = "lxreijnqjiaghtti" 
    receiver_email = email  

    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = "Mashup Audio File"
    message.attach(MIMEText("Please find the attached zip file.", "plain"))

    zip_file = "audios/" + output_file + ".zip"
    
    part = MIMEBase('application', "octet-stream")
    part.set_payload( open(zip_file,"rb").read() )  
    encoders.encode_base64(part)
    output_file_2 = "output_file"
    part.add_header(
        "Content-Disposition",
        f"attachment; filename={output_file_2 +'.zip'}",
    )
    
    message.attach(part)
    text = message.as_string()
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_email, PASSWORD)
        server.sendmail(sender_email, receiver_email, text)

def clearFiles():
    path = os.getcwd()+'/audios/'
    if os.path.exists(path):
        fileList = os.listdir(path)
        for file in fileList:
            os.remove(path+file)

if submit_button:
    if name == '' or num_videos == '' or cut_duration == '' or output_file == '' or email == '':
        st.warning('Please fill all the fields.')
    else:
        st.success('Please wait while the request is being processed. This may take a few minutes depending on the number of videos you have entered.')
        if output_file.count('.') == 0:
            output_file += '.mp3'
        output_file.split('.')[-1] = 'mp3'
        singer = name.replace(' ', '+')
        num_of_videos = int(num_videos)
        clearFiles()
        videos = get_videos(singer)
        for video in videos:
            download_video(video)
        convert_vid_to_audio()
        mergeAudios()
        zipAudio()
        sendEmail(email, output_file)
        st.success("Your output .mp3 file has been zipped and sent to your email.")
        st.balloons()
