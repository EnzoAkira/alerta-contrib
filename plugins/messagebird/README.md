Messagebird Plugin
===================

Send to Messagebird messages for Critical alerts.

Installation
------------

Clone the GitHub repo and run:

    $ python setup.py install

> #### Note: If Alerta is installed in a python virtual environment then plugins need to be installed into the same environment for Alerta to dynamically discover them. 

Enter on python virtual environment:

    $ source /opt/alerta/bin/activate
    $ cd /path/of/plugin/messagebird
    $ python setup.py install

To exit from python venv:

    $ deactivate

Configuration
-------------

Add `messagebird` to the list of enabled `PLUGINS` in `alertad.conf` server
configuration file and set plugin-specific variables either in the
server configuration file or as environment variables.
Create a specific group that will use the plugin.
Add the id of the group to `ID_OF_GROUP` var.

On Alerta Dashboard format user name as:
```
FirstName SecondName | +351Number	
```
> **This only will work on numbers from Portugal!**


```python
PLUGINS = ['messagebird']
MESSAGEBIRD_APIKEY = ''  # default="not set"
MESSAGEBIRD_FROM_NUMBER = ''  # default="not set"
ID_OF_GROUP = '' # default="not set"
```

**Example**

```python
PLUGINS = ['reject','messagebird']
MESSAGEBIRD_APIKEY = 'lkJASHd7698-POIHjh'  # default="not set"
MESSAGEBIRD_FROM_NUMBER = '+3512199999'  # default="not set"
ID_OF_GROUP = '720c3e2c-80fb-4d92-b4d6-a64c09e61bcc'
```

Troubleshooting
---------------

Restart Alerta API and confirm that the plugin has been loaded and enabled.

Set `DEBUG=True` in the `alertad.conf` configuration file and look for log
entries similar to below:

```
2020-02-14 14:41:49,893 - alerta.plugins[62723]: DEBUG - Server plug-in 'messagebird' found. [in /opt/alerta/lib64/python3.6/site-packages/alerta/utils/plugin.py:42]
2020-02-14 14:41:49,894 - alerta.plugins[62723]: INFO - Server plug-in 'messagebird' enabled. [in /opt/alerta/lib64/python3.6/site-packages/alerta/utils/plugin.py:42]
```
```
2020-02-14 18:12:54,916 - urllib3.connectionpool[19479]: DEBUG - Starting new HTTPS connection (1): voice.messagebird.com:443 [in /opt/alerta/lib64/python3.6/site-packages/urllib3/connectionpool.py:959]
2020-02-14 18:12:55,217 - urllib3.connectionpool[19479]: DEBUG - https://voice.messagebird.com:443 "POST /calls HTTP/1.1" 201 277 [in /opt/alerta/lib64/python3.6/site-packages/urllib3/connectionpool.py:437]
2020-02-14 18:12:55,220 - alerta.plugins.messagebird[19479]: DEBUG - Information was returned as a <class 'messagebird.call.Call'> object: 
[in /opt/alerta/lib64/python3.6/site-packages/alerta_messagebird-0.0.5-py3.6.egg/alerta_messagebird.py:59]
2020-02-14 18:12:55,221 - alerta.plugins.messagebird[19479]: DEBUG - id: '99cf7831-cccf-4f8a-9cc2-884404fc6ed6'
status: 'queued'
source: '3512199999'
destination: '35193542185' [in /opt/alerta/lib64/python3.6/site-packages/alerta_messagebird-0.0.5-py3.6.egg/alerta_messagebird.py:63]
```

References
----------

  * MessageBird API Reference:

    - [Voice Messaging](https://developers.messagebird.com/api/voice-messaging/)
    - [SMS](https://developers.messagebird.com/api/sms-messaging/)
