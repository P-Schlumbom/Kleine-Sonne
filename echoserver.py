from flask import Flask, request
import json
import requests
import numpy as np
import pyowm

app = Flask(__name__)

# This needs to be filled with the Page Access Token that will be provided
# by the Facebook App that will be created.
PAT = 'EAAFsUgXKDNgBAE4Ni76NlZBm1WKOWC8KRMZBsZCmkK6yCVRLUfjsw73qZBIb7rRHSAPibTDZBfPuY5GTcTYhZBI3wUYUDxTZCPZAG6QI5J114ezTPp7PCUygmZBh9rTmeHa0qIWIX56rKbRdiVIyzF7flfQltQrc5d7oJrtPhTkWITAZDZD'

#pyowm setup
owm = pyowm.OWM('b458d73d80151ce2be0d359eb826b549')  # pyowm api key
location = 'Auckland,nz'

@app.route('/', methods=['GET'])
def handle_verification():
  print("Handling Verification.")
  if request.args.get('hub.verify_token', '') == 'my_voice_is_my_password_verify_me':
    print("Verification successful!")
    return request.args.get('hub.challenge', '')
  else:
    print("Verification failed!")
    return 'Error, wrong validation token'

@app.route('/', methods=['POST'])
def handle_messages():
  print("Handling Messages")
  payload = request.get_data()
  print(payload)
  for sender, message in messaging_events(payload):
    print("Incoming from %s: %s" % (sender, message))
    send_message(PAT, sender, message)
  return "ok"

def messaging_events(payload):
  """Generate tuples of (sender_id, message_text) from the
  provided payload.
  """
  data = json.loads(payload)
  messaging_events = data["entry"][0]["messaging"]
  for event in messaging_events:
    if "message" in event and "text" in event["message"]:
        yield event["sender"]["id"], process_message(event["message"]["text"])
    else:
      yield event["sender"]["id"], "I can't echo this"


def send_message(token, recipient, text):
  """Send the message text to recipient with id recipient.
  """

  r = requests.post("https://graph.facebook.com/v2.6/me/messages",
    params={"access_token": token},
    data=json.dumps({
      "recipient": {"id": recipient},
      "message": {"text": text.decode('unicode_escape')}
    }),
    headers={'Content-type': 'application/json'})
  if r.status_code != requests.codes.ok:
    print(r.text)

def process_message(incoming):
  incoming = incoming.lower()
  greetings = ["hello", "hi ", "good morning", "good evening", "good day", "good afternoon"]
  tatas = ["goodbye", "bye", "see ya", "see you later", "writerlator", "good night"]
  if any(word in incoming for word in greetings):
    return "Hi!"
  elif any(word in incoming for word in tatas):
    return "See you later!"
  elif "every existing thing is born without reason" in incoming:
    return "and prolongs itself out of weakness"
  elif "jeder fuer sich" in incoming:
    return "und gott gegen alle"
  elif "version?" in incoming:
    return "test1: 0.2"
  elif "random?" in incoming:
    return str(np.random.rand())
  elif "weather?" in incoming:
    return get_weather()
  else:
     return incoming

def get_weather():
  weatherReport = ""
  observation = owm.weather_at_place(location)
  w = observation.get_weather()
  try:
    weatherReport = w.get_detailed_status()
  except:
    weatherReport = "Sorry, pyowm is being a little bitch and won't tell me nothin"
  return weatherReport
    
if __name__ == '__main__':
  app.run()
