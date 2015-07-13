import logging

from django.contrib.auth import get_user_model
from django.conf import settings

import requests

PERSONA_VERIFY_URL = 'https://verifier.login.persona.org/verify'
User = get_user_model()
logger = logging.getLogger(__name__)

class PersonaAuthenticationBackend(object):

    def authenticate(self, assertion):
        resp = requests.post(PERSONA_VERIFY_URL, data={
            'assertion': assertion,
            'audience': settings.DOMAIN
        })

        if resp.ok and resp.json()['status'] == 'okay':
            email = resp.json()['email']
            try:
                return User.objects.get(email=email)
            except User.DoesNotExist:
                return User.objects.create(email=email)
        elif not resp.ok:
            logger.warning('Persona says no. resp.ok is False')
        else:
            logger.warning('Persona says no. Json was: {}'.format(
                resp.json()
            ))


    def get_user(self, email):
        try:
            return User.objects.get(email=email)
        except User.DoesNotExist:
            return None