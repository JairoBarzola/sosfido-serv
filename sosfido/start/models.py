""" Models for start app """
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User


class Place(models.Model):
    """ Information of an specific place """
    location = models.CharField(max_length=180, default='')
    latitude = models.CharField(max_length=50, default='')
    longitude = models.CharField(max_length=50, default='')

    def __str__(self):
        return self.location


class Person(models.Model):
    """ Additional information for a User """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    address = models.OneToOneField(Place, on_delete=models.CASCADE, blank=True,
                                   null=True)
    born_date = models.DateField()
    phone_number = models.CharField(max_length=18)

    def __str__(self):
        return self.user.get_full_name()


class PersonImage(models.Model):
    """ Images in general for the project """
    person = models.ForeignKey(Person)
    image = models.ImageField(upload_to='photos/users/profile',
                              blank=True)
    upload_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.person.user.get_full_name() + ': ' + self.image.url


class AdoptionProposal(models.Model):
    """ Proposal of adoption made by one person """
    STATUSES = (
        (0, 'CANCELADA'),
        (1, 'ACEPTADA'),
        (2, 'EN ESPERA')
    )
    owner = models.ForeignKey(Person, related_name="owner",
                              on_delete=models.CASCADE, blank=True, null=True)
    pet_name = models.CharField(max_length=50, blank=True, null=True,
                                default="Sin nombre")
    description = models.TextField(blank=True, null=True)
    status = models.IntegerField(choices=STATUSES, default=2)
    was_deleted = models.BooleanField(default=False)
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        description = 'Sin descripción'
        if self.description:
            description = self.description
        return self.owner.user.get_full_name() + ' - ' + description


class AdoptionRequest(models.Model):
    """ Request to adopt associated to a proposal """
    STATUSES = (
        (0, 'CANCELADA'),
        (1, 'ACEPTADA'),
        (2, 'EN ESPERA')
    )
    adoption_proposal = models.ForeignKey(AdoptionProposal,
                                          on_delete=models.CASCADE)
    requester = models.ForeignKey(Person, on_delete=models.CASCADE)
    description = models.TextField(blank=True, null=True, default='')
    status = models.IntegerField(choices=STATUSES, default=2)
    was_deleted = models.BooleanField(default=False)
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        description = 'Sin descripción'
        if self.description:
            description = self.description
        return self.requester.user.get_full_name() + ' - ' + description


class AdoptionImage(models.Model):
    """ Model for images of adoption proposals """
    adoption_proposal = models.ForeignKey(AdoptionProposal,
                                          on_delete=models.CASCADE)
    image = models.ImageField(upload_to='photos/adoptions/pets',
                              blank=True)
    upload_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.adoption_proposal.__str__()


class AnimalReport(models.Model):
    """ Report made for a stry/lost animal """
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    place = models.OneToOneField(Place, on_delete=models.CASCADE)
    pet_name = models.CharField(max_length=50, blank=True, null=True,
                                default='Sin nombre')
    description = models.TextField(blank=True, null=True)
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        description = 'Sin descripción'
        if self.description:
            description = self.description
        return self.person.user.get_full_name() + ' - ' + description


class ReportImage(models.Model):
    """ Model for images of reports """
    report = models.ForeignKey(AnimalReport, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='photos/reports/pets',
                              blank=True)
    upload_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.report.__str__()


class PersonDevice(models.Model):
    """ Devices of a person """
    person = models.ForeignKey(Person)
    id_device = models.CharField(max_length=40)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.person.user.get_full_name() + ' - ' + self.id_device
