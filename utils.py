from twilio.rest import Client

class TwilioTexter():
    def __init__(self):
        self.client = self.get_twilio_client()
    

    def get_twilio_client(self):
        aid = 'ACbcf8d51a96ed0013d121e1e47330f0c6'
        a_token = 'e3b933ce7a5553e2775bf3e5113f908c'
        client = Client(aid, a_token)
        return client

    def send_text(self, to_number, body, from_number="+18554216531"):
        message = self.client.messages.create(
            to=to_number,
            from_=from_number,
            body=body
        )
        return True