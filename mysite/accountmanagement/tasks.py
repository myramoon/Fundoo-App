import logging,os
from celery import shared_task
from django.core.mail import EmailMessage
import threading
from notes.models import Note
from accountmanagement.models import Account
from mysite.settings import SECONDS_IN_DAY,MINUTE_CONVERSION_CONSTANT,MINUTES_IN_HOUR
import datetime
import pytz

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s  %(name)s  %(levelname)s: %(message)s')

file_handler = logging.FileHandler(os.path.abspath('loggers/log_tasks.log'),mode='w')
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)


class EmailThread(threading.Thread):
    """[creates thread for sending email]
    """
    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        self.email.send()

@shared_task
def send_email(data):
    """[sends email on the basis of set email parameters in registration view, reset password view and check_remider method]
    """
    email = EmailMessage(
        subject=data['email_subject'], body=data['email_body'], to=[data['to_email']])
    EmailThread(email).start()




@shared_task
def check_reminder():
    """[checks notes periodically if any note's reminder is set within the current hour.If yes sends an email informing the same.]
    """

    current_time = datetime.datetime.now()
    utc = pytz.UTC
    current_time = utc.localize(current_time)
    logger.debug(current_time)

    for note in Note.objects.exclude(reminder=None).filter(reminder__gt = current_time):
        difference = note.reminder-current_time
        minutes_remaining = (divmod(difference.days * SECONDS_IN_DAY + difference.seconds, MINUTE_CONVERSION_CONSTANT))

        if(minutes_remaining[0] < MINUTES_IN_HOUR):
            user_email = Account.objects.get(email=note.user).email
            data = {'email_body': 'Hi!Reminder for ' + note.title + ' is scheduled within this hour.',
                    'to_email': user_email,
                    'email_subject': 'Reminder for your note'}
            send_email.delay(data)
            logger.debug('sent reminder for '+note.title)















