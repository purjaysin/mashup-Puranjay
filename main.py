import streamlit as st
from email import encoders
st.set_page_config(page_title="Puranjay's Mashup", layout="wide", initial_sidebar_state="expanded")  
st.title("MASHUP your favourite artist's songs!")

name = st.text_input("Enter name of the singer:")
num_videos =  st.text_input("Enter the no. of videos:")
cut_duration = st.text_input("Enter cut duration(in seconds):")
email_id = st.text_input("Enter your email address:")
submit_button = st.button("Submit")

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
                if email_id is "":
                    st.error("Please enter the email ID")
                else:
                    if "@" not in email_id:
                        st.error("Please enter a valid email ID")
                    else:
                        st.balloons()
                        st.success("Output audio file has been zipped and mailed to your email ID.")

if submit_button:
    import urllib.request
    import re
    from pytube import YouTube
    import os
    from moviepy.editor import *
    import zipfile
    import email, smtplib, ssl
    from email.mime.base import MIMEBase
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText

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
            print("Cannot download video: " + video)

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
            print(file)
            video = VideoFileClip(path+file).subclip(0, int(cut_duration))
            video.audio.write_audiofile(SAVE_PATH + '/audios/' + str(idx) + ".mp3")
            video.close()
            os.remove(path+file)
            idx += 1

    def mergeAudios():
        SAVE_PATH = os.getcwd() + '/'
        final_wav_path = SAVE_PATH + "audios/" + "final_output.mp3"
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
        print("The audio files have been merged after editing and is located in:  " + final_wav_path)

    def zipAudio():
        SAVE_PATH = os.getcwd() + '/'
        final_wav_path = "audios/" + "final_output.mp3"
        zip_file = "audios/" + "final_output" + ".zip"
        with zipfile.ZipFile(zip_file, 'w') as myzip:
            myzip.write(final_wav_path)

    def sendEmail(email_id, result_file) : 
        port = 465  # For SSL
        smtp_server = "smtp.gmail.com"
        sender_email = "psingh12_be20@thapar.edu" 
        PASSWORD = "lxreijnqjiaghtti"
        receiver_email = email_id
        print(email_id)
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = receiver_email
        message["Subject"] = "MASHUP output .mp3 file from Puranjay Singh"
        message.attach(MIMEText("You used the app for creating a MASHUP of your favourite artist. Please find the result output in the attached .mp3 file.", "plain"))
        
        final_wav_path = "audios/" + "final_output"
        zip_file = final_wav_path + ".zip"
        print(zip_file)
        with open(zip_file, "rb") as attachment:
            # Add file as application/octet-stream
            # Email client can usually download this automatically as attachment
            part = MIMEBase("application", "octet-stream")
            part.set_payload((attachment).read())

        # Encode file in ASCII characters to send by email    
        encoders.encode_base64(part)
        result_file_2 = "final_output" + ".zip"
        part.add_header(
        "Content-Disposition",
        f"attachment; filename={result_file_2}",
        )

        # Add attachment to message and convert message to string
        message.attach(part)
        text = message.as_string()

        # Log in to server using secure context and send email
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
            server.login(sender_email, PASSWORD)
            server.sendmail(sender_email, receiver_email, text)

if submit_button:
        singer = name.replace(' ', '+')
        num_of_videos = int(num_videos)
        videos = get_videos(singer)
        for video in videos:
            download_video(video)
        convert_vid_to_audio()
        mergeAudios()
        zipAudio()
        sendEmail(email_id, "final_output.mp3")