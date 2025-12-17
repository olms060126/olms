from django.conf import settings
from phonepe.sdk.pg.payments.v2.standard_checkout_client import StandardCheckoutClient
from phonepe.sdk.pg.payments.v2.models.request.standard_checkout_pay_request import StandardCheckoutPayRequest
from phonepe.sdk.pg.common.models.request.meta_info import MetaInfo
from phonepe.sdk.pg.env import Env


_client=None

def get_phonepe_client():
    global _client
    if _client is None:
        env = Env.SANDBOX if settings.PHONEPE_ENV == "SANDBOX" else Env.PRODUCTION
        
        _client = StandardCheckoutClient.get_instance(
            client_id=settings.CLIENT_ID,
            client_secret=settings.CLIENT_SECRET,
            client_version=settings.CLIENT_VERSION,
            env=env,
            should_publish_events=False,
        )   
    return _client

def meta_info_generation():
    meta_info = MetaInfo(
    udf1="test-user-123",
    udf2="demo-order",
    udf3="any-extra-info",)
    return meta_info

def buil_request(client,unique_order_id,amount_paise,redirect_url,meta_info):
    standard_pay_request = StandardCheckoutPayRequest.build_request(
    merchant_order_id=unique_order_id,
    amount=amount_paise,
    redirect_url=redirect_url,
    meta_info=meta_info,
    
)
    return standard_pay_request    


def send_mail(reseiver,subject,body):
    sender = settings.EMAIL_NAME
    password = settings.EMAIL_PASSWORD
    message = MIMEMultipart()
    message["From"] = sender
    message["To"] = reseiver
    message["Subject"] = subject

    message.attach(MIMEText(body, "plain"))

    # Connect to Gmail SMTP
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()  # Secure the connection
        server.login(sender, password)
        server.sendmail(sender, reseiver, message.as_string())

    print("Email sent successfully!")