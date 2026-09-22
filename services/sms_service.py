from twilio.rest import Client
import logging

class SMSService:
    def __init__(self, twilio_sid, twilio_token, twilio_phone, contact_number):
        self.client = Client(twilio_sid, twilio_token)
        self.twilio_phone = twilio_phone
        self.contact_number = contact_number

    def send_sms(self, message_body, filename):
        try:
            sms = self.client.messages.create(
                body=message_body,
                from_=self.twilio_phone,
                to=self.contact_number
            )
            logging.info(f"SMS alert sent for {filename}, SID: {sms.sid}")
            return True, sms.sid
        except Exception as e:
            logging.error(f"Error sending SMS for {filename}: {str(e)}")
            return False, str(e)