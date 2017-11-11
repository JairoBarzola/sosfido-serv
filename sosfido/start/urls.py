""" URLs for start app"""
from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
from start.views import AuthenticateUserAPI, PersonAPI, LocationAPI, \
    ValidateLoginAjax, Index, RegisterUserAPI, LogoutAPI, PersonImageAPI, \
    AnimalReportAPI, ReportImageAPI, AdoptionImageAPI, AdoptionProposalAPI, \
    PersonDeviceAPI, UpdatePasswordAPI, FindUserAPI

app_name = 'start'

urlpatterns = [
    url(r'^$', Index.as_view(), name='home'),
    url(r'^login/$', ValidateLoginAjax.as_view()),
    url(r'^register-api/$', RegisterUserAPI.as_view()),
    url(r'^login-api/$', AuthenticateUserAPI.as_view()),
    url(r'^logout-api/$', LogoutAPI.as_view()),
    url(r'^update-password-api/$', UpdatePasswordAPI.as_view()),
    url(r'^find-user-api/$', FindUserAPI.as_view()),
    url(r'^person-api/$', PersonAPI.as_view({'get': 'list'})),
    url(r'^person-api/(?P<id>[0-9]+)/$',
        PersonAPI.as_view({'get': 'retrieve', 'patch': 'partial_update'})),
    url(r'^location-api/$', LocationAPI.as_view({'get': 'list'})),
    url(r'^person-image-api/$',
        PersonImageAPI.as_view({'post': 'create'})),
    url(r'^person-image-api/(?P<person__id>[0-9]+)/$',
        PersonImageAPI.as_view({'get': 'retrieve', 'patch': 'partial_update'})),
    url(r'^report-image-api/$',
        ReportImageAPI.as_view({'post': 'create'})),
    url(r'^report-image-api/(?P<report__id>[0-9]+)/$',
        ReportImageAPI.as_view({'get': 'retrieve', 'patch': 'partial_update'})),
    url(r'^animal-report-api/$',
        AnimalReportAPI.as_view({'get': 'list', 'post': 'create'})),
    url(r'^animal-report-api/(?P<id>[0-9]+)/$',
        AnimalReportAPI.as_view({'get': 'retrieve', 'patch': 'partial_update',
                                 'delete': 'destroy'})),
    url(r'^adoption-image-api/$',
        AdoptionImageAPI.as_view({'post': 'create'})),
    url(r'^adoption-image-api/(?P<adoption__id>[0-9]+)/$',
        AdoptionImageAPI.as_view({'get': 'retrieve', 'patch': 'partial_update'})),
    url(r'^adoption-proposal-api/$',
        AdoptionProposalAPI.as_view({'get': 'list', 'post': 'create'})),
    url(r'^adoption-proposal-api/(?P<id>[0-9]+)/$',
        AdoptionProposalAPI.as_view({'get': 'retrieve',
                                     'patch': 'partial_update',
                                     'delete': 'destroy'})),
    url(r'^person-device-api/$',
        PersonDeviceAPI.as_view({'get': 'list', 'post': 'create'})),
    url(r'^person-device-api/(?P<id>[0-9]+)/$',
        PersonDeviceAPI.as_view({'get': 'retrieve', 'patch': 'partial_update'})),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
