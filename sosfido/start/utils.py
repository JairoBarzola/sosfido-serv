""" Utils for start app """
from datetime import timezone, datetime, timedelta
from sosfido import settings
from django.contrib.auth.models import User
from oauth2_provider.models import Application, AccessToken
from oauthlib.common import generate_token

from start.models import Person, Place
from start.serializers import TokenSerializer


def create_username(first_name, last_name):
    """ Create username account
        parameters
        ----------
        first_name: String
            first name of user account
        last_name: String
            last name of user account
    """
    first_name = first_name.split(" ")[0].replace(".", "")
    last_name = last_name.split(" ")[0].replace(".", "")
    username = (first_name + "." + last_name).lower()
    usernames = User.objects.filter(username__contains=username).order_by('id')
    if usernames:
        for user_name in usernames:
            repeated_username = user_name.username
            first_part = repeated_username.split('.')[0]
            second_part = repeated_username.split('.')[1]
            if (username.split('.')[0] == first_part and
                    username.split('.')[1] == second_part):
                split_repeated_username = repeated_username.split('.')
                if len(split_repeated_username) == 2:
                    username = username + '.1'
                else:
                    count = int(repeated_username.split('.')[2])
                    count += 1
                    if len(split_repeated_username) == 3:
                        split_repeated_username[2] = str(count)
                        username = '.'.join(split_repeated_username)
                    else:
                        username = username + '.' + str(count)
    return username


def get_access_token(user):
    """ Method to obtain access to a new token """
    access_token = None
    if AccessToken.objects.filter(user=user,
                                  expires__gt=timezone.now()).exists():
        access_token = (AccessToken.objects
                        .filter(user=user, expires__gt=timezone.now()).last())
    if not access_token:
        expire_seconds = settings.OAUTH2_PROVIDER['ACCESS_TOKEN_EXPIRE_SECONDS']
        scopes = settings.OAUTH2_PROVIDER['SCOPES']
        application = Application.objects.get(name="SOSFIDO")
        expires = datetime.now() + timedelta(seconds=expire_seconds)
        access_token = AccessToken.objects.create(user=user,
                                                  application=application,
                                                  token = generate_token(),
                                                  expires=expires,
                                                  scope=scopes)
    serializer = TokenSerializer(access_token, many=False)
    return serializer


def create_user(dict_post):
    """ Function to create an user and person """
    exists_user = User.objects.filter(email=dict_post['email']).exists()
    if not exists_user:
        dict_post['first_name'] = (dict_post['first_name']).title()
        dict_post['last_name'] = (dict_post['last_name']).title()
        username = create_username(dict_post['first_name'],
                                   dict_post['last_name'])
        user = User.objects.create(username=username,
                                   email=dict_post['email'],
                                   password="",
                                   first_name=dict_post['first_name'],
                                   last_name=dict_post['last_name'])
        user.set_password(dict_post['password'])
        user.save()
        place = Place.objects.create(location=dict_post['location'],
                                     latitude=dict_post['latitude'],
                                     longitude=dict_post['longitude'])
        place.save()
        person = Person.objects.create(user=user,
                                       address=place,
                                       born_date=dict_post['born_date'],
                                       phone_number=dict_post['phone_number'])
        person.save()
        return user
    else:
        return None
