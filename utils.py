import os
from twilio.rest import Client
from dotenv import load_dotenv

class TwilioTexter():
    def __init__(self):
        # self.client = self.get_twilio_client()
        print("TwilioTexter initialized")
    
    def get_twilio_client(self):

        load_dotenv()

        aid = os.getenv('TWILIO_AID')
        a_token = os.getenv('TWILIO_TOKEN')
        client = Client(aid, a_token)

        return client

    def send_text(self, to_number, body, from_number="+18554216531"):
        message = self.client.messages.create(
            to=to_number,
            from_=from_number,
            body=body
        )
        return True