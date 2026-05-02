import streamlit as st

# Config the page
st.set_page_config(
    page_title = "Voice Assistant",
    layout = "wide"
)


# Libraries
import os
import time
import pyttsx3
import speech_recognition as sr
from groq import Groq
from dotenv import load_dotenv

# Load the API key from the local environment
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    st.error("You forget to initialize the API key in terminal")
    st.stop()

# initializing the LLM using API key
client =  Groq(api_key=GROQ_API_KEY)
MODEL = "llama-3.3-70b-versatile"

def get_ai_response(chat_messages):
    try:
        response = client.chat.completions.create(
            model = MODEL,
            messages = chat_messages,
            temperature=0.7
        )

        # LLM will provide many outputs
        result = response.choices[0].message.content
        return result.strip() if result else "Sorry I could not generate the response"
    except Exception as e:
        return f"I don't like your Question {e}"

# inititalize the speech to text recognizer
recognizer = sr.Recognizer()

# initialize Text to Speech Engine
def get_tts_engine():
    try:
        engine = pyttsx3.init()
        return engine
    except Exception as e:
        st.error(f"Failed to initialize TTS engine {e}")
        return None
    
def speak(text, voice_gender = "girl"):
    try:
        engine = get_tts_engine()
        if engine is None:
            return
        
        # choose the voice from the pyttsx3
        # engine supports many voice
        voices = engine.getProperty('voices')
        if voices:
            if voice_gender == 'boy':
                for voice in voices:
                    if "male" in voice.name.lower():
                        engine.setProperty('voice', voice.id)
                        break
            else:
                for voice in voices:
                    if "female" == voice.name.lower() or "zira" in voice.name.lower():
                        engine.setProperty('voice', voice.id)
                        break
        
        engine.setProperty('rate', 150)   # speed of speech
        engine.setProperty('volumn', 0.8) 
        engine.say(text)
        engine.runAndWait()
        engine.stop()
    except Exception as e:
        st.error(f"TTS ERROR {e}")


# Convert speech to text + capture audio via microphone
def listen_to_speech():
    try:
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration = 1)
            audio = recognizer.listen(source, phrase_time_limit = 10)

        text = recognizer.recognize_google(audio)
        return text.lower()
    except sr.UnknownValueError:
        return "Sorry, I didnot catch you"
    except sr.RequestError:
        return "Speech service is not available"
    except Exception as e:
        return f"Other Error {e}"



def main():
    st.title("Baby SIRI Voice Assistant")
    st.markdown("---")

    # initialize the chat history : use to share chatting with LLM
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
            {"role" : "system", "content" : "You are a useful voice assistant. Reply just one line"}
        ]

    # initialize messages : To display chatting message on screen
    if "messages" not in st.session_state:
        st.session_state.messages = []

    with st.sidebar:
        st.header("CONTROLS")

        tts_enable = st.checkbox("Enable for Voice Reply from LLM", value = True)

        voice_gender = st.selectbox(
            "Gontu Enchkondi",
            options = ["girl", "boy"],
            index = 0,
            help = "Voice Gender choice"
        )

        if st.button("Start the Conversation", type = "primary", use_container_width=True):
            with st.spinner("Listening...."):
                user_input = listen_to_speech()

                if user_input and user_input not in ["Sorry, I didnot catch you", "Speech service is not available"]:
                    st.session_state.messages.append({"role" : "user", "content" : user_input})
                    st.session_state.chat_history.append({"role" : "user", "content" : user_input})

                    # Task-2 : Getting reply from LLM
                    with st.spinner("Thniking...."):
                        ai_response = get_ai_response(st.session_state.chat_history)
                        st.session_state.messages.append({"role" : "assistant", "content" : ai_response})
                        st.session_state.chat_history.append({"role" : "assistant", "content" : ai_response})

                    if tts_enable:
                        speak(ai_response,voice_gender)


                    st.rerun()

        st.markdown("---")

        st.subheader("Text Input")
        user_text = st.text_input("Type your Message", key = "text_input")
        if st.button("SEND", use_container_width=True) and user_text:
            st.session_state.messages.append({"role" : "user", "content" : user_text})
            st.session_state.chat_history.append({"role" : "user", "content" : user_text})

            with st.spinner("Thinking...."):
                ai_response = get_ai_response(st.session_state.chat_history)
                st.session_state.messages.append({"role" : "assistant", "content" : ai_response})
                st.session_state.chat_history.append({"role" : "assistant", "content" : ai_response})
    
            if tts_enable:
                speak(ai_response,voice_gender)

            st.rerun()
        
        st.markdown("---")

        if st.button("Khali the Chat", use_container_width=True):
            st.session_state.messages = []
            st.session_state.chat_history = [
            {"role" : "system", "content" : "You are a useful voice assistant. Reply just one line"}
            ]
            st.rerun()
    
    st.subheader("CONVERSATION")

    for message in st.session_state.messages:
        if message["role"] == "user":
            with st.chat_message("user"):
                st.write(message["content"])
        else:
            with st.chat_message("assistant"):
                st.write(message["content"])


    # Starting Welcome message
    if not st.session_state.messages:
        st.info(" WELCOME TO BABY SIRI VOICE/CHAT ASSISTANT")


    # Copyright
    st.markdown("---")
    st.markdown(
        """
            <div style = 'text-align: center; color : #666;'>
                <p> Copyright @ Puneet Kansal </p>
            </div>
        """,
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()