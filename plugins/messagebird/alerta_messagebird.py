import json
import logging
import os
import re
import string
from alerta.models.group import GroupUsers
import messagebird
from alerta.plugins import PluginBase

try:
  from alerta.plugins import app  # alerta >= 5.0
except ImportError:
  from alerta.app import app  # alerta < 5.0

LOG = logging.getLogger('alerta.plugins.messagebird')

MB_APIKEY = app.config['MESSAGEBIRD_APIKEY'] # !!! Do not delete !!!
FROM_NUMBER = app.config['MESSAGEBIRD_FROM_NUMBER'] # !!! Do not delete !!!
ID_GROUP = app.config['ID_FOR_FIREMASTER'] # !!! Do not delete !!!


class MessageBird(PluginBase):

  def _getNumbers(self):
    NUMBER_LIST = []
    RE_phone = re.compile(r"^\+351\d{9}")
    
    try:
      GROUP_FM = GroupUsers.find_by_id(ID_GROUP)
      LOG.debug('MessageBird: Group Firemaster: {}'.format(GROUP_FM)) # TESTING
            
      for USER in GROUP_FM:
        USER_NAME = USER.name
        LOG.debug('MessageBird: The User %s', USER_NAME) # TESTING
        
        L_USER = USER_NAME.split('|')
        
        PHONE_NUMBER = L_USER[1].strip(' ')
        LOG.debug('MessageBird: The phone number is: %s', PHONE_NUMBER) # TESTING
        
        if RE_phone.match(PHONE_NUMBER):
          NUMBER_LIST.append(PHONE_NUMBER)
        else:
          LOG.error('MessageBird: Number isn\'t valid %s for user %s', PHONE_NUMBER, L_USER[0])
          
    except Exception as e:
      LOG.error('MessageBird: Get Users failed: %s', e)
    
    return NUMBER_LIST

  def _getVoiceMessage(self, host, severity, resource):

    # Body of a Voice Message
    # <break> & <prosody> is for controlling speed of speech
    # https://developers.messagebird.com/api/voice-messaging#the-voice-body
    resource = resource.replace(".",",")
    resource = resource.replace("_"," ")

    # For Voice Message body
    message = "<break time=\"1s\"/>server <prosody rate=\"-5%\">{0}</prosody>, severity <prosody rate=\"-5%\">{1}</prosody>, alert on <prosody rate=\"-10%\">{2}</prosody>".format(host, severity, resource)

    # For callflow body
    #message = "<break time=\\\"1s\\\"/>server <prosody rate=\\\"-10%\\\">{0}</prosody>, severity <prosody rate=\\\"-10%\\\">{1}</prosody>, alert on <prosody rate=\\\"-10%\\\">{2}</prosody>".format(host, severity, resource)
    
    return message

  def _getSMSMessage(self, host, severity, resource):
    
    # Body of a SMS
    # https://developers.messagebird.com/api/sms-messaging#send-outbound-sms
    sms = str("Server {0}, changed to severity {1}, for alert {2}").format(host.upper(), severity.upper(), resource)

    return sms

  def _makeCallPayload(self, message, TO_NUMBER): # Not used for now
    
    # Makes a Call body
    # Instead we use Voice Message
    # https://developers.messagebird.com/api/voice-calling#calls
    callMessage = {}
      
    callMessage["source"] = FROM_NUMBER
    
    callMessage["destination"] = TO_NUMBER
    
    callMessage["callFlow"] = '{{"title": "Alerta", "steps": [{{"action": "say", "options": {{"language": "en-US", "voice": "male", "payload": "{}"}}}},{{"action": "hangup"}}]}}'.format(message)
          
    callMessage["callFlow"] = callMessage["callFlow"].strip("'''")
    
    callMessage["callFlow"] = json.loads(str(callMessage["callFlow"]))
    
    callMessage["webhook"] = {}
    
    LOG.debug('Messagebird: CallMessage format {!s}'.format(callMessage)) # For TESTING

    return callMessage

  def _makeCall(self, message, TO_NUMBER): # Not used for now
    
    # Makes a Voice Call 
    # Instead we use Voice Message
    # https://developers.messagebird.com/api/voice-calling#calls
    callMessage = self._makeCallPayload(message, TO_NUMBER)
    
    try:
      client = messagebird.Client(MB_APIKEY)

      call = client.call_create(**callMessage)
      
      LOG.debug('Messagebird: Information was returned as a {!r} object '.format(call)) # For TESTING
      
      # DEBUGGING
      """
      info = "id: {id!r} | status: {status!r} | source: {source!r} | destination: {destination!r}"
      LOG.debug(info.format(id = call.data.id, status = call.data.status, source = call.data.source, destination = call.data.destination)) # For TESTING
      """

    except messagebird.client.ErrorException as e:
      LOG.error('An error occurred while creating a call:')
      
      for error in e.errors:
        
        LOG.error(
          '\tcode\t: {!s}\n\tdescription :\t{!s}'.format(error.code, error.description)
          )

  def _makeVoiceMessagePayload(self, message, TO_NUMBER):
    
    # Makes a Voice Message body
    # https://developers.messagebird.com/api/voice-messaging#the-voice-body
    voiceMessage = {}

    params = {}
    
    voiceMessage["recipients"] = TO_NUMBER
          
    voiceMessage["body"] = message

    params = {
              'language': 'en-gb',
              'voice': 'male',
              'ifMachine': 'hangup',
              'originator': FROM_NUMBER
             }

    voiceMessage["params"] = params

    # DEBUGGING
    LOG.debug('Messagebird: voiceMessage format {!s}'.format(voiceMessage)) # For TESTING

    return voiceMessage

  def _makeVoiceMessage(self, message, TO_NUMBER):
    
    # Makes a Voice Message 
    # https://developers.messagebird.com/api/voice-messaging#send-a-voice-message

    # Prepare Args to send on a Voice Message
    voiceMessage = self._makeVoiceMessagePayload(message, TO_NUMBER)
    LOG.debug('Messagebird: Voice Message format {}'.format(voiceMessage))
    
    # Make a Voice Message
    try:
      client = messagebird.Client(MB_APIKEY)

      voice_message = client.voice_message_create(**voiceMessage)

      # DEBUGGING
      LOG.debug('Messagebird: Voice Call information {}'.format(voiceMessage)) # For TESTING

    except messagebird.client.ErrorException as e:
      LOG.error('An error occurred while creating a Voice_Call:')
      
      for error in e.errors:
        LOG.error(
          'code: {!s} | description:{!s}'.format(error.code, error.description)
          )

  def _makeSMSPayload(self, message, TO_NUMBER):
    
    # Makes a SMS body
    # https://developers.messagebird.com/api/sms-messaging#the-message-object
    
    SMS = {}
      
    SMS["originator"] = 'GOALERTA'
    
    SMS["recipients"] = TO_NUMBER
    
    SMS["body"] = message
  
    #LOG.debug('Messagebird: SMS format {!s}'.format(SMS)) # For TESTING

    return SMS

  def _makeSMS(self, message, TO_NUMBER):

    # Send a SMS
    # https://developers.messagebird.com/api/sms-messaging#send-outbound-sms
    smsMessage = self._makeSMSPayload(message, TO_NUMBER)
    
    try:
      client = messagebird.Client(MB_APIKEY)
      
      sms = client.message_create(**smsMessage)

      # DEBUGGING
      LOG.debug('Messagebird: SMS information {!r}'.format(smsMessage)) # For TESTING

    except messagebird.client.ErrorException as e:
      LOG.error('An error occurred while creating a sms:')
      for error in e.errors:
        LOG.error(
          '\tcode\t: {!s}\n\tdescription :\t{!s}'.format(error.code, error.description)
          )

  def pre_receive(self, alert):
    return alert

  def post_receive(self, alert):
    
    # Hostname from alert is:
    host = alert.origin.split('/')
    
    # Get Phone Numbers
    L_NUMBERS = self._getNumbers()
        
    if alert.repeat:
      return
      
    # If new or update Alert is Critical make a Call
    if alert.severity == 'critical':
      message = self._getVoiceMessage(host[1], alert.severity, alert.event)
      
      # DEBUGGING
      LOG.debug('Messagebird: Voice Message - {}'.format(message))
    
      self._makeVoiceMessage(message, L_NUMBERS)
    
    # When severity decrease send a SMS
    if alert.severity in ['warning', 'cleared'] and alert.status not in ['ack', 'closed']:
       sms = self._getSMSMessage(host[1], alert.severity, alert.event)

       # DEBUGGING
       LOG.debug('Messagebird: SMS - {}'.format(sms))
       
       self._makeSMS(sms, L_NUMBERS)

  def status_change(self, alert, status, text):
    return alert