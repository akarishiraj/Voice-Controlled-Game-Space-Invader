from ibm_watson import SpeechToTextV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator


def activate():
    # initialize speech to text service
    authenticator = IAMAuthenticator('yTSSJ5GSmGhgIA95KnVPDf61KSZinztq909UBMfoqh7l')
    speech_to_text = SpeechToTextV1(authenticator=authenticator)
    speech_to_text.set_service_url(
        "https://api.us-east.speech-to-text.watson.cloud.ibm.com/instances/77c94867-643f-431b-a593-0bc775c18bb7")
    return speech_to_text


def stop(stream, audio, audio_source):
    try:
        stream.stop_stream()
        stream.close()
        audio.terminate()
        audio_source.completed_recording()
    except Exception as e:
        print("ERROR")
        print(e)
