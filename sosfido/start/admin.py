""" Admin for start app """
from django.contrib import admin
from start.models import Place, Person, AdoptionProposal, AnimalReport, \
    ReportImage, PersonImage, AdoptionImage, PersonDevice, AdoptionRequest

admin.site.register(Place)
admin.site.register(Person)
admin.site.register(AdoptionProposal)
admin.site.register(AnimalReport)
admin.site.register(ReportImage)
admin.site.register(PersonImage)
admin.site.register(AdoptionImage)
admin.site.register(PersonDevice)
admin.site.register(AdoptionRequest)
