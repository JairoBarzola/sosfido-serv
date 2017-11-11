""" Views for start app """
import requests
from datetime import datetime, timedelta
from sosfido import settings
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.http.response import JsonResponse
from django.shortcuts import render, redirect
from django.views import generic, View
from django.utils import timezone
from oauth2_provider.models import Application, AccessToken
from oauth2_provider.ext.rest_framework.\
    authentication import OAuth2Authentication
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication,\
    BasicAuthentication
from start.models import Person, Place, PersonImage, ReportImage, AnimalReport, \
    AdoptionImage, PersonDevice, AdoptionProposal
from start.serializers import PersonSerializer, PlaceSerializer, \
    ApplicationSerializer, PersonImageSerializer, ReportImageSerializer, \
    AnimalReportSerializer, AdoptionImageSerializer, AdoptionProposalSerializer, \
    PersonDeviceSerializer
from start.utils import create_user


class CsrfExemptSessionAuthentication(SessionAuthentication):
    """ Class View used to exempt csrf for a request"""

    def enforce_csrf(self, request):
        """ Overwriting method enforce_csrf """
        return  # To not perform the csrf check previously happening


class Index(View):
    """ Class View to show the home page of the website """

    def get(self, request):
        """ GET method to return a render response """
        return render(request, 'start/Index.html', {})


class PersonAPI(ModelViewSet):
    """ API class to manage Person serializer """
    authentication_classes = [OAuth2Authentication]
    permission_classes = [IsAuthenticated]
    queryset = Person.objects.all()
    serializer_class = PersonSerializer
    lookup_field = 'id'

    def get_queryset(self):
        """ Method to redefine the queryset """
        if 'email' in self.request.GET:
            if (Person.objects.filter(user__email=self.request.GET['email'])
                    .exists()):
                queryset = (Person.objects
                            .filter(user__email=self.request.GET['email']))
            else:
                queryset = []
        else:
            queryset = Person.objects.all()
        return queryset


class FindUserAPI(APIView):
    """ API view to find a user with its email """
    authentication_classes = [CsrfExemptSessionAuthentication,
                              BasicAuthentication]
    permission_classes = [AllowAny]

    def post(self, request):
        """ Post method for the Api view """
        if 'email' in self.request.POST:
            if (Person.objects.filter(user__email=self.request.POST['email'])
                    .exists()):
                user = (Person.objects
                        .filter(user__email=self.request.POST['email'])
                        .last().user)
                return Response({'status': True, 'user_id': user.id})
        return Response({'status': False, 'user_id': 0})


class UpdatePasswordAPI(APIView):
    """ API class to update the password of an user """
    authentication_classes = [CsrfExemptSessionAuthentication,
                              BasicAuthentication]
    permission_classes = [AllowAny]

    def post(self, request):
        """ Post method for the Api view """
        if 'password' in self.request.POST and 'user_id' in self.request.POST:
            if User.objects.filter(id=self.request.POST['user_id']).exists():
                user = User.objects.get(id=self.request.POST['user_id'])
                user.set_password(self.request.POST['password'])
                user.save()
                return Response({'status': True})
        return Response({'status': False})


class LocationAPI(ModelViewSet):
    """ API class to manage Location serializer """
    authentication_classes = [OAuth2Authentication]
    permission_classes = [IsAuthenticated]
    queryset = Place.objects.all()
    serializer_class = PlaceSerializer


class ValidateLoginAjax(generic.View):
    """ Validate login for the admin in the web """
    def get(self, request):
        if 'email' in request.GET and 'password' in request.GET:
            email = request.GET['email']
            password = request.GET['password']
            email_active = False
            if User.objects.filter(email=email, is_active=True).exists():
                email_active = True
                found_user = User.objects.filter(email=email,
                                                 is_active=True).last()
                user = authenticate(username=found_user.username,
                                    password=password)
                if user:
                    return JsonResponse({
                        'status': True, 'full_name': user.get_full_name(),
                        'short_name': user.first_name
                    })
                else:
                    return JsonResponse({'status': False})
            else:
                return JsonResponse({'status': False})
        if 'username' in request.GET and 'password' in request.GET:
            username = request.GET['username']
            password = request.GET['password']
            if User.objects.filter(username=username, is_active=True).exists():
                user = authenticate(username=username,
                                    password=password)
                if user:
                    return JsonResponse({
                        'status': True, 'full_name': user.get_full_name(),
                        'short_name': user.first_name, 'id_user': user.id
                    })
                else:
                    return JsonResponse({'status': False})
            else:
                return JsonResponse({'status': False})


class AuthenticateUserAPI(APIView):
    """ Api to authenticate an user """
    authentication_classes = [CsrfExemptSessionAuthentication,
                              BasicAuthentication]
    permission_classes = [AllowAny]

    def get(self, request):
        """ GET method to return a render response """
        return redirect('start:home')

    def post(self, request):
        """ POST method for authentication """
        if 'email' in self.request.POST or 'password' in self.request.POST:
            email = request.POST['email']
            password = request.POST['password']
            user = None
            if User.objects.filter(email=email, is_active=True).exists():
                obj_user = User.objects.filter(email=email,
                                               is_active=True).last()
                user = authenticate(username=obj_user.username,
                                    password=password)
                if user:
                    login(request, user)
                else:
                    return Response({'status': False})
            if user:
                application = Application.objects.get(name="SOSFIDO")
                app = ApplicationSerializer(application)
                url = ("http://" + settings.SERVER_HOST + "/o/token/" +
                       "?grant_type=password&" +
                       "client_id=" + app['client_id'].value + "&" +
                       "client_secret=" + app['client_secret'].value + "&" +
                       "username=" + user.username + "&" +
                       "password=" + password + "&" +
                       "date=" + str(timezone.now()))
                request_content = requests.post(url)
                response_json = request_content.json()
                person_id = Person.objects.get(user=user).id
                return Response({'access_token': response_json['access_token'],
                                 'person_id': person_id, 'status': True},
                                status=status.HTTP_200_OK)
        return Response({'status': False})


class RegisterUserAPI(APIView):
    """ API used for registration of an user """
    authentication_classes = [CsrfExemptSessionAuthentication,
                              BasicAuthentication]
    permission_classes = [AllowAny]

    def get(self, request):
        """ GET method to return a render response """
        return redirect('start:home')

    def post(self, request):
        """ POST method to handle the registration """
        dictionary_post = {}
        dictionary_post['first_name'] = self.request.POST['first_name']
        dictionary_post['last_name'] = self.request.POST['last_name']
        dictionary_post['email'] = self.request.POST['email']
        dictionary_post['password'] = self.request.POST['password']
        dictionary_post['born_date'] = self.request.POST['born_date']
        dictionary_post['phone_number'] = self.request.POST['phone_number']
        dictionary_post['location'] = self.request.POST['location']
        dictionary_post['latitude'] = self.request.POST['latitude']
        dictionary_post['longitude'] = self.request.POST['longitude']
        new_user = create_user(dictionary_post)
        if new_user is not None:
            if new_user:
                new_user_auth = authenticate(username=new_user.username,
                                             password=dictionary_post['password'])
                if new_user_auth:
                    login(request, new_user_auth)
                else:
                    return Response({'status': False})
            application = Application.objects.get(name="SOSFIDO")
            app = ApplicationSerializer(application)
            url = ("http://" + settings.SERVER_HOST +
                   "/o/token/?grant_type=password&" +
                   "client_id=" + app['client_id'].value + "&" +
                   "client_secret=" + app['client_secret'].value + "&" +
                   "username=" + new_user.username + "&" +
                   "password=" + dictionary_post['password'] + "&" +
                   "date=" + str(timezone.now()))
            request_content = requests.post(url)
            response_json = request_content.json()
            person_id = Person.objects.get(user=new_user).id
            return Response({'access_token': response_json['access_token'],
                             'person_id': person_id, 'status': True},
                            status=status.HTTP_200_OK)
        return Response({'status': False})


class LogoutAPI(APIView):
    """ API class used to handle logout """
    authentication_classes = [OAuth2Authentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """ GET method to return a render response """
        return redirect('start:home')

    def post(self, request):
        """ POST Method for logout """
        if 'person_id' in self.request.POST:
            user = User.objects.get(person__id=self.request.POST['person_id'])
            if AccessToken.objects.filter(user=user).exists():
                tokens = AccessToken.objects.filter(user=user)
                for token in tokens:
                    token.revoke()
                logout(request)
                return Response({'status': True})
        return Response({'status': False})


class PersonImageAPI(ModelViewSet):
    """ API view to manage images for person """
    authentication_classes = [OAuth2Authentication]
    permission_classes = [IsAuthenticated]
    serializer_class = PersonImageSerializer
    queryset = PersonImage.objects.all()
    lookup_field = 'person__id'


class ReportImageAPI(ModelViewSet):
    """ API view to manage images for reports """
    authentication_classes = [OAuth2Authentication]
    permission_classes = [IsAuthenticated]
    serializer_class = ReportImageSerializer
    queryset = ReportImage.objects.all()
    lookup_field = 'report__id'


class AnimalReportAPI(ModelViewSet):
    """ API view to manage reports """
    authentication_classes = [OAuth2Authentication]
    permission_classes = [IsAuthenticated]
    serializer_class = AnimalReportSerializer
    lookup_field = 'id'

    def get_queryset(self):
        """ Redefinition of queryset for the view """
        queryset = []
        if 'person_id' in self.request.GET:
            if 'abandoned_pet' in self.request.GET:
                queryset = (AnimalReport.objects
                            .filter(pet_name__exact='Sin nombre',
                                    person__id=self.request.GET['person_id']))
            elif 'missing_pet' in self.request.GET:
                queryset = (AnimalReport.objects
                            .filter(person__id=self.request.GET['person_id'])
                            .exclude(pet_name__exact='Sin nombre'))
        elif 'all_reports' in self.request.GET:
            if 'abandoned_pet' in self.request.GET:
                queryset = (AnimalReport.objects
                            .filter(pet_name__exact='Sin nombre',
                                    date__gt=datetime.now()-timedelta(hours=1)))
            elif 'missing_pet' in self.request.GET:
                queryset = (AnimalReport.objects
                            .filter(date__gt=datetime.now()-timedelta(hours=1))
                            .exclude(pet_name__exact='Sin nombre'))
        return queryset


class AdoptionImageAPI(ModelViewSet):
    """ API view to manage images for adoptions """
    authentication_classes = [OAuth2Authentication]
    permission_classes = [IsAuthenticated]
    serializer_class = AdoptionImageSerializer
    queryset = AdoptionImage.objects.all()
    lookup_field = 'adoption__id'


class AdoptionProposalAPI(ModelViewSet):
    """ API view to manage adoptions """
    authentication_classes = [OAuth2Authentication]
    permission_classes = [IsAuthenticated]
    serializer_class = AdoptionProposalSerializer
    lookup_field = 'id'

    def get_queryset(self):
        """ Redefinition of queryset for the view """
        queryset = []
        if 'owner_id' in self.request.GET:
            queryset = (AdoptionProposal.objects
                        .filter(owner__id=self.request.GET['owner_id']))
        elif 'all_adoptions' in self.request.GET:
            queryset = (AdoptionProposal.objects
                        .filter(date__gt=datetime.now()-timedelta(days=15)))
        return queryset


class PersonDeviceAPI(ModelViewSet):
    """ Api class to manage UserDevice model """
    authentication_classes = [OAuth2Authentication]
    permission_classes = [IsAuthenticated]
    serializer_class = PersonDeviceSerializer
    lookup_field = 'id'

    def get_queryset(self):
        """ Redefinition of queryset for the view """
        if 'person_id' in self.request.GET:
            queryset = (PersonDevice.objects
                        .filter(person__id=self.request.GET['person_id'],
                                is_active=True))
        else:
            queryset = PersonDevice.objects.all()
        return queryset
