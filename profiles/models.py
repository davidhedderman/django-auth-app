from decimal import Decimal

from allauth.account.signals import user_signed_up
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone
from pinax.eventlog.models import log as user_log


def update_previous_login(sender, user, **kwargs):
    """
    A signal receiver which updates the previous_login date for
    the user logging in, and the duplicated_last_login.
    The user of the duplicated_last_login is to ensure that the
    previous_login gets updated first.
    """
    user.previous_login = user.duplicated_last_login
    user.duplicated_last_login = timezone.now()
    user.save(update_fields=['previous_login', 'duplicated_last_login'])


def get_or_create_loggedin_user(sender, user, **kwargs):
    LoggedInUser.objects.get_or_create(user=user)


user_logged_in.connect(get_or_create_loggedin_user)
user_logged_in.connect(update_previous_login)


def delete_loggedin_user(sender, user, **kwargs):
    LoggedInUser.objects.filter(user=user).delete()


user_logged_out.connect(delete_loggedin_user)


def add_eventlog_signup(sender, user, **kwargs):
    """
    A signal receiver which adds an event log when a user signs up
    """
    user_log(user=user, action="NEW_USER_SIGNUP", extra={"user_email": "{0}".format(user.email),
                                                         "user_username": "{0}".format(user.username)})


user_signed_up.connect(add_eventlog_signup)


class ProfileUser(AbstractUser):
    previous_login = models.DateTimeField('Previous login', default=timezone.now)
    duplicated_last_login = models.DateTimeField('Duplicated last login', default=timezone.now)

    name = models.CharField(max_length=50, null=True, blank=True)
    address_first_line = models.CharField(max_length=50, null=True, blank=True)
    address_second_line = models.CharField(max_length=50, null=True, blank=True)
    address_third_line = models.CharField(max_length=50, null=True, blank=True)
    can_access_user_admin =  models.BooleanField(verbose_name="Access user admin", default=False,
                                            help_text="...")
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    credit = models.DecimalField(max_digits=16, decimal_places=2, default=0.00,
                                 validators=[MinValueValidator(Decimal('0.00'))],
                                 help_text="This is the amount of hits that the user currently has. Credit is reduced "
                                           "as the user matches and downloads files.")

    def __unicode__(self):
        return self.username


class LoggedInUser(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='logged_in_user', on_delete=models.CASCADE)
    session_key = models.CharField(max_length=32, null=True, blank=True)


    def __str__(self):
        return self.user.username
