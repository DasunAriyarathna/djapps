
from django.conf import settings

def send_mail(to_addr,
              from_addr         = "",
              subject           = "No Subject",
              body              = "",
              email_host        = "localhost",
              email_port        = 25,
              email_username    = "",
              email_password    = ""):
    if settings.USING_APPENGINE:
        from google.appengine.api import mail
        mail.send_mail(sender = from_addr, to = to_addr, subjet = subject, body = body)
    else:
        from django.core.mail import send_mail
        import smtplib
        server = smtplib.SMTP(email_host, email_port)
        if email_username:
            server.login(email_username, email_password)
        server.sendmail(from_addr,
                        new_user.email,
                        "Subject: " + email_subject + "\r\n" + body)
        server.sendmail(from_addr,
                        "admin@threefeeds.com",
                        "Subject: New user registered - " + new_user.email + "\r\n" +
                        ("Name: %s %s" % (new_user.first_name, new_user.last_name)))
        server.quit()
