from flask import Flask, request
import json
import requests
import numpy as np
import pyowm
from wit import Wit

app = Flask(__name__)

# This needs to be filled with the Page Access Token that will be provided
# by the Facebook App that will be created.
PAT = 'EAAFsUgXKDNgBAE4Ni76NlZBm1WKOWC8KRMZBsZCmkK6yCVRLUfjsw73qZBIb7rRHSAPibTDZBfPuY5GTcTYhZBI3wUYUDxTZCPZAG6QI5J114ezTPp7PCUygmZBh9rTmeHa0qIWIX56rKbRdiVIyzF7flfQltQrc5d7oJrtPhTkWITAZDZD'

#pyowm setup
owm = pyowm.OWM('b458d73d80151ce2be0d359eb826b549')  # pyowm api key
location = 'Auckland,nz'

witAccessToken = '3KNHMXJ5LNQPUCRSKH3JJDIZTTQW4QEX'   # use this to access wit

witResponse = ""
feedbackReport = "No Report"

@app.route('/', methods=['GET'])
def handle_verification():
  if request.args.get('hub.verify_token', '') == 'my_voice_is_my_password_verify_me':
    return request.args.get('hub.challenge', '')
  else:
    return 'Error, wrong validation token'

@app.route('/', methods=['POST'])
def handle_messages():
  payload = request.get_data()
  for sender, message in messaging_events(payload):
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
    return "wit-integration: 0.2.11"
  elif "random?" in incoming:
    return str(np.random.rand())
  elif "weather?" in incoming:
    return get_weather()
  else:
    try:
      #wit_run(incoming)
      client.run_actions('us-1', message=incoming)
      #return witResponse
      return witResponse + ", " + feedbackReport
    except:
      return "My dynos are spent. My line has ended. Heroku has deserted us. Wit.ai's betrayed me. Abandon your posts! Flee, flee for your lives!"

def get_weather():
  """
  simply tries to retrieve the current weather status in Auckland, returns a warning instead if this isn't possible
  """
  weatherReport = ""
  observation = owm.weather_at_place(location)
  w = observation.get_weather()
  
  try:
    weatherReport = w.get_detailed_status()
  except:
    weatherReport = "Sorry, pyowm is being a little bitch and won't tell me nothin"
  return weatherReport

#-----------the following functions concern wit integration--------------------#

def first_entity_value(entities, entity):
  if entity not in entities:
    return None
  val = entities[entity][0]['value']
  if not val:
    return None
  return val['value'] if isinstance(val, dict) else val

def send(request, response):
  global witResponse
  witResponse = str(response['text'])
  return response['text']

def get_forecast(request):
  context = request['context']
  entities = request['entities']
  
  global feedbackReport
  feedbackReport = "well, something's working at least... context is: " + str(context)
  
  loc = first_entity_value(entities, 'location')
  if loc:
    #feedbackReport += "loc is true, "
    feedbackReport = feedbackReport + " loc is true, "
    context['forecast'] = 'sunny'
    if context.get('missingLocation') is not None:
      #feedbackReport += "missingLocation is not None."
      feedbackReport = feedbackReport + "missingLocation is not None."
      del context['missingLocation']
  else:
    #feedbackReport += "missingLocation is None.
    feedbackReport = feedbackReport + "missingLocation is None."
    context['missingLocation'] = True
    if context.get('forecast') is not None:
      #feedbackReport += " forecast is not None."
      feedbackReport = feedbackReport + " forecast is not None, it is " + str(context['forecast'])
      del context['forecast']
  feedbackReport = feedbackReport + " Outgoing context..." + str(context)
  return context

actions = {'send': send, 'getForecast': get_forecast,}

'''def wit_run(mess):
  """
  tries to get a response from wit, and returns it.
  """
  witReport = ""
  client = Wit(access_token=witAccessToken, actions=actions)   #  This was outside the function, but get_weather() didn't like that for some reason?
  #resp = client.converse('us-1', message='hello there')
  resp = client.run_actions('us-1', message=mess)
  
  try:
    witReport = resp['msg']
  except:
    witReport = "Wit didn't like that, here's what we got: " + str(resp)
  
  return witReport'''

client = Wit(access_token=witAccessToken, actions=actions)

if __name__ == '__main__':
  app.run()
'''
#--------------------------------------------------------------------------------------------------------------------------------#
app = Flask(__name__)

WIT_TOKEN = '3KNHMXJ5LNQPUCRSKH3JJDIZTTQW4QEX'
# Messenger API parameters
FB_PAGE_TOKEN = 'EAAFsUgXKDNgBAE4Ni76NlZBm1WKOWC8KRMZBsZCmkK6yCVRLUfjsw73qZBIb7rRHSAPibTDZBfPuY5GTcTYhZBI3wUYUDxTZCPZAG6QI5J114ezTPp7PCUygmZBh9rTmeHa0qIWIX56rKbRdiVIyzF7flfQltQrc5d7oJrtPhTkWITAZDZD'
# A user secret to verify webhook get request.
FB_VERIFY_TOKEN = 'my_voice_is_my_password_verify_me'

#pyowm setup
owm = pyowm.OWM('b458d73d80151ce2be0d359eb826b549')  # pyowm api key
location = 'Auckland,nz'


# Facebook Messenger GET Webhook
@app.get('/webhook')
def messenger_webhook():
    """
    A webhook to return a challenge
    """
    verify_token = request.query.get('hub.verify_token')
    # check whether the verify tokens match
    if verify_token == FB_VERIFY_TOKEN:
        # respond with the challenge to confirm
        challenge = request.query.get('hub.challenge')
        return challenge
    else:
        return 'Invalid Request or Verification Token'


# Facebook Messenger POST Webhook
@app.post('/webhook')
def messenger_post():
    """
    Handler for webhook (currently for postback and messages)
    """
    data = request.json
    if data['object'] == 'page':
        for entry in data['entry']:
            # get all the messages
            messages = entry['messaging']
            if messages[0]:
                # Get the first message
                message = messages[0]
                # Yay! We got a new message!
                # We retrieve the Facebook user ID of the sender
                fb_id = message['sender']['id']
                # We retrieve the message content
                text = message['message']['text']
                # Let's forward the message to the Wit.ai Bot Engine
                # We handle the response in the function send()
                fb_message(fb_id, text)
                #client.run_actions(session_id=fb_id, message=text)
    else:
        # Returned another event
        return 'Received Different Event'
    return None


def fb_message(sender_id, text):
    """
    Function for returning response to messenger
    """
    data = {
        'recipient': {'id': sender_id},
        'message': {'text': text}
    }
    # Setup the query string with your PAGE TOKEN
    qs = 'access_token=' + FB_PAGE_TOKEN
    # Send POST request to messenger
    resp = requests.post('https://graph.facebook.com/me/messages?' + qs,
                         json=data)
    return resp.content


def first_entity_value(entities, entity):
    """
    Returns first entity value
    """
    if entity not in entities:
        return None
    val = entities[entity][0]['value']
    if not val:
        return None
    return val['value'] if isinstance(val, dict) else val


def send(request, response):
    """
    Sender function
    """
    # We use the fb_id as equal to session_id
    fb_id = request['session_id']
    text = response['text']
    # send message
    fb_message(fb_id, text)


def get_forecast(request):
    context = request['context']
    entities = request['entities']
    loc = first_entity_value(entities, 'location')
    if loc:
        # This is where we could use a weather service api to get the weather.
        context['forecast'] = 'sunny'
        if context.get('missingLocation') is not None:
            del context['missingLocation']
    else:
        context['missingLocation'] = True
        if context.get('forecast') is not None:
            del context['forecast']
    return context

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
    return "master: 0.2"
  elif "random?" in incoming:
    return str(np.random.rand())
  elif "weather?" in incoming:
    return get_weather()
  elif "wit?" in incoming:
    return wit_run()
  else:
     return incoming

def get_weather():
  """
  simply tries to retrieve the current weather status in Auckland, returns a warning instead if this isn't possible
  """
  weatherReport = ""
  observation = owm.weather_at_place(location)
  w = observation.get_weather()
  try:
    weatherReport = w.get_detailed_status()
  except:
    weatherReport = "Sorry, pyowm is being a little bitch and won't tell me nothin"
  return weatherReport

def wit_run():
  """
  tries to get a response from wit, and returns it.
  """
  witReport = ""
  client = Wit(access_token=witAccessToken, actions=actions)
  resp = client.converse('us-1', message='hello there')
  
  try:
    witReport = resp['msg']
  except:
    witReport = "Wit didn't like that, here's what we got: " + str(resp)
  
  return witReport

# Setup Actions
actions = {
    'send': send,
    'getForecast': get_forecast,}

# Setup Wit Client
client = Wit(access_token=WIT_TOKEN, actions=actions)

if __name__ == '__main__':
  app.run()
'''
