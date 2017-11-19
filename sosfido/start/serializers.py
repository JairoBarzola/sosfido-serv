""" Serializers for start app """
from sosfido import settings
from django.contrib.auth.models import User
from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import ModelSerializer, DateTimeField
from oauth2_provider.models import Application, AccessToken
from drf_extra_fields.fields import Base64ImageField
from start.models import Person, Place, PersonImage, ReportImage, AnimalReport,\
    PersonDevice, AdoptionImage, AdoptionProposal, AdoptionRequest
from start.utils import find_devices, send_notification_mobile


class UserSerializer(ModelSerializer):
    """ Serializer for User model """

    class Meta:
        """ Meta class for User serializer """
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']
        extra_kwargs = {'id': {'read_only': True, 'required': False},
                        'username': {'read_only': True, 'required': False}}


class PlaceSerializer(ModelSerializer):
    """ Serializer for Location model """
    class Meta:
        """ Meta class for Location serializer """
        model = Place
        fields = ['location', 'latitude', 'longitude']


class PersonSerializer(ModelSerializer):
    """ Serializer for Person model """
    person_image = SerializerMethodField()

    def to_representation(self, obj):
        ret = super(PersonSerializer, self).to_representation(obj)
        if 'all_reports' in self.context['request'].GET:
            ret.pop('user')
            ret.pop('born_date')
            ret.pop('phone_number')
            ret.pop('address')
            ret.pop('person_image')
        return ret

    class Meta:
        """ Meta class for Person serializer """
        model = Person
        fields = ['id', 'user', 'born_date', 'phone_number', 'address',
                  'person_image']
        extra_kwargs = {'id': {'read_only': True, 'required': False}}

    def __init__(self, *args, **kwargs):
        super(PersonSerializer, self).__init__(*args, **kwargs)
        if self.context['request'].method == 'GET':
            self.fields['user'] = UserSerializer(read_only=True,
                                                 context=kwargs['context'])
            self.fields['address'] = PlaceSerializer(read_only=True,
                                                     context=kwargs['context'])
        if self.context['request'].method == 'PATCH':
            self.fields['user'] = UserSerializer(context=kwargs['context'])
            self.fields['address'] = PlaceSerializer(context=kwargs['context'])

    def update(self, instance, validated_data):
        """ Function to update user information """
        if 'user' in validated_data:
            user_data = validated_data.pop('user')
            user = instance.user
            if 'first_name' in user_data:
                user.first_name = user_data['first_name']
            if 'last_name' in user_data:
                user.first_name = user_data['last_name']
            if 'email' in user_data:
                user.first_name = user_data['email']
            user.save()
        if 'phone_number' in validated_data:
            instance.phone_number = validated_data['phone_number']
        if 'born_date' in validated_data:
            instance.born_date = validated_data['born_date']
        if 'address' in validated_data:
            address_data = validated_data.pop('address')
            place = instance.address
            if 'location' in address_data:
                place.location = address_data['location']
            if 'latitude' in address_data:
                place.latitude = address_data['latitude']
            if 'longitude' in address_data:
                place.longitude = address_data['longitude']
            place.save()
        instance.save()
        return instance

    def get_person_image(self, obj):
        """ This method obtain the profile image of a person """
        person_image = 'Sin imagen'
        if PersonImage.objects.filter(person=obj).exists():
            person_image = (PersonImage.objects.filter(person=obj)
                            .order_by('-upload_date').first())
            person_image = (settings.IMAGE_HOST + person_image.image.url)
        return person_image


class PersonImageSerializer(ModelSerializer):
    """ Serializer for Image of user profiles """
    image = Base64ImageField()
    url_image = SerializerMethodField()
    upload_date = DateTimeField(read_only=True, format="%Y-%m-%d %H:%M:%S")
    extra_kwargs = {'id': {'read_only': True, 'required': False}}

    def to_representation(self, obj):
        ret = super(PersonImageSerializer, self).to_representation(obj)
        if self.context['request'].method == 'POST':
            ret.pop('id')
            ret.pop('person')
            ret.pop('image')
            ret.pop('upload_date')
        return ret

    class Meta:
        """ Meta class for ImageDetail serializer """
        model = PersonImage
        fields = '__all__'

    def update(self, instance, validated_data):
        """ Function to update user information """
        instance.image.delete(save=False)
        instance.image = validated_data.get('image', instance.image)
        instance.save()
        return instance

    def get_url_image(self, obj):
        """ Function to obtain the url for an image """
        return settings.IMAGE_HOST + obj.image.url


class ReportImageSerializer(ModelSerializer):
    """ Serializer for Image of reports of animals """
    image = Base64ImageField()
    url_image = SerializerMethodField()
    upload_date = DateTimeField(read_only=True, format="%Y-%m-%d %H:%M:%S")
    extra_kwargs = {'id': {'read_only': True, 'required': False}}

    def to_representation(self, obj):
        ret = super(ReportImageSerializer, self).to_representation(obj)
        if self.context['request'].method == 'POST':
            ret.pop('id')
            ret.pop('report')
            ret.pop('image')
            ret.pop('upload_date')
        return ret

    class Meta:
        """ Meta class for ImageDetail serializer """
        model = ReportImage
        fields = '__all__'

    def create(self, validated_data):
        report_image = ReportImage.objects.create(**validated_data)
        report_image.save()
        person_devices = list(PersonDevice.objects
                              .exclude(person__id=report_image.report
                                       .person.id)
                              .values_list('id_device', flat=True))
        title = 'SOSFIDO'
        message = ('Se creo un reporte de un animal en ' +
                   report_image.report.place.location)
        data_notification = {'report_id': report_image.report.id}
        image_notification = 'https://s3.amazonaws.com/uploads.hipchat.com/' +\
                             '529035/4489842/wDKOTjEIqyr1pPX/logo_sosfido1.png'
        send_notification_mobile(person_devices, title, message,
                                 data_notification, image_notification)
        return report_image

    def update(self, instance, validated_data):
        """ Function to update user information """
        instance.image.delete(save=False)
        instance.image = validated_data.get('image', instance.image)
        instance.save()
        return instance

    def get_url_image(self, obj):
        """ Function to obtain the url for an image """
        return settings.IMAGE_HOST + obj.image.url


class AnimalReportSerializer(ModelSerializer):
    """ Serializer for AnimalReport model """
    report_image = SerializerMethodField()
    date = DateTimeField(read_only=True, format="%Y-%m-%d %H:%M:%S")

    def to_representation(self, obj):
        ret = super(AnimalReportSerializer, self).to_representation(obj)
        if self.context['request'].method == 'POST':
            ret.pop('person')
            ret.pop('place')
            ret.pop('pet_name')
            ret.pop('description')
            ret.pop('date')
            ret.pop('report_image')
        if self.context['request'].method == 'PATCH':
            ret.pop('person')
            ret.pop('place')
            ret.pop('pet_name')
            ret.pop('description')
            ret.pop('date')
            ret.pop('report_image')
        elif self.context['request'].method == 'GET':
            if 'person_id' in self.context['request'].GET:
                ret.pop('person')
            if 'abandoned_pet' in self.context['request'].GET:
                ret.pop('pet_name')
        return ret

    class Meta:
        """ Meta class for AnimalReport serializer """
        model = AnimalReport
        fields = ['id', 'person', 'pet_name', 'place', 'description', 'date',
                  'report_image']
        extra_kwargs = {'id': {'read_only': True, 'required': False}}

    def __init__(self, *args, **kwargs):
        super(AnimalReportSerializer, self).__init__(*args, **kwargs)
        if self.context['request'].method == 'GET':
            self.fields['person'] = PersonSerializer(read_only=True,
                                                     context=kwargs['context'])
            self.fields['place'] = PlaceSerializer(read_only=True,
                                                   context=kwargs['context'])
        if self.context['request'].method == 'POST':
            self.fields['place'] = PlaceSerializer(context=kwargs['context'])
        if self.context['request'].method == 'PATCH':
            self.fields['place'] = PlaceSerializer(context=kwargs['context'])

    def create(self, validated_data):
        """ Method create for the serializer """
        place_data = validated_data.pop('place')
        place = Place.objects.create(**place_data)
        place.save()
        animal_report = AnimalReport.objects.create(place=place,
                                                    **validated_data)
        animal_report.save()
        return animal_report

    def update(self, instance, validated_data):
        """ Method update for the serializer """
        if 'place' in validated_data:
            place_data = validated_data.pop('place')
            place = instance.place
            if 'location' in place_data:
                place.location = place_data['location']
            if 'latitude' in place_data:
                place.latitude = place_data['latitude']
            if 'longitude' in place_data:
                place.longitude = place_data['longitude']
            place.save()
        if 'description' in validated_data:
            instance.description = validated_data['description']
        instance.save()
        return instance

    def get_report_image(self, obj):
        """ This method obtain the image of a report """
        report_image = 'Sin imagen'
        if ReportImage.objects.filter(report=obj).exists():
            report_image = (ReportImage.objects.filter(report=obj)
                            .order_by('-upload_date').first())
            report_image = (settings.IMAGE_HOST + report_image.image.url)
        return report_image


class AdoptionImageSerializer(ModelSerializer):
    """ Serializer for Image of adoption of animals """
    image = Base64ImageField()
    url_image = SerializerMethodField()
    upload_date = DateTimeField(read_only=True, format="%Y-%m-%d %H:%M:%S")
    extra_kwargs = {'id': {'read_only': True, 'required': False}}

    def to_representation(self, obj):
        ret = super(AdoptionImageSerializer, self).to_representation(obj)
        if self.context['request'].method == 'POST':
            ret.pop('id')
            ret.pop('adoption_proposal')
            ret.pop('image')
            ret.pop('upload_date')
        return ret

    class Meta:
        """ Meta class for ImageDetail serializer """
        model = AdoptionImage
        fields = '__all__'

    def update(self, instance, validated_data):
        """ Function to update user information """
        instance.image.delete(save=False)
        instance.image = validated_data.get('image', instance.image)
        instance.save()
        return instance

    def get_url_image(self, obj):
        """ Function to obtain the url for an image """
        return settings.IMAGE_HOST + obj.image.url


class AdoptionProposalSerializer(ModelSerializer):
    """ Serializer for AnimalReport model """
    adoption_image = SerializerMethodField()
    date = DateTimeField(read_only=True, format="%Y-%m-%d %H:%M:%S")

    def to_representation(self, obj):
        ret = super(AdoptionProposalSerializer, self).to_representation(obj)
        if self.context['request'].method == 'POST':
            ret.pop('owner')
            ret.pop('pet_name')
            ret.pop('description')
            ret.pop('date')
            ret.pop('status')
            ret.pop('adoption_image')
            ret.pop('was_deleted')
        if self.context['request'].method == 'PATCH':
            ret.pop('owner')
            ret.pop('pet_name')
            ret.pop('description')
            ret.pop('date')
            ret.pop('status')
            ret.pop('adoption_image')
            ret.pop('was_deleted')
        elif self.context['request'].method == 'GET':
            if 'owner_id' in self.context['request'].GET:
                ret.pop('owner')
            ret.pop('was_deleted')
        return ret

    class Meta:
        """ Meta class for AnimalReport serializer """
        model = AdoptionProposal
        fields = ['id', 'owner', 'pet_name', 'status', 'description', 'date',
                  'adoption_image', 'was_deleted']
        extra_kwargs = {'id': {'read_only': True, 'required': False}}

    def __init__(self, *args, **kwargs):
        super(AdoptionProposalSerializer, self).__init__(*args, **kwargs)
        if self.context['request'].method == 'GET':
            self.fields['owner'] = PersonSerializer(read_only=True,
                                                    context=kwargs['context'])
            self.fields['adopter'] = PersonSerializer(read_only=True,
                                                      context=kwargs['context'])

    def update(self, instance, validated_data):
        """ Method update for the serializer """
        if 'status' in validated_data:
            instance.status = validated_data['status']
        if 'description' in validated_data:
            instance.description = validated_data['description']
        if 'was_deleted' in validated_data:
            instance.was_deleted = validated_data['was_deleted']
        instance.save()
        return instance

    def get_adoption_image(self, obj):
        """ This method obtain the image of a report """
        adoption_image = 'Sin imagen'
        if AdoptionImage.objects.filter(adoption_proposal=obj).exists():
            adoption_image = (AdoptionImage.objects
                              .filter(adoption_proposal=obj)
                              .order_by('-upload_date').first())
            adoption_image = (settings.IMAGE_HOST + adoption_image.image.url)
        return adoption_image


class AdoptionRequestSerializer(ModelSerializer):
    """ Serializer for adoption request model """
    date = DateTimeField(read_only=True, format="%Y-%m-%d %H:%M:%S")

    def to_representation(self, obj):
        ret = super(AdoptionRequestSerializer, self).to_representation(obj)
        if self.context['request'].method == 'POST':
            ret.pop('requester')
            ret.pop('adoption_proposal')
            ret.pop('description')
            ret.pop('date')
            ret.pop('status')
            ret.pop('was_deleted')
        if self.context['request'].method == 'PATCH':
            ret.pop('requester')
            ret.pop('adoption_proposal')
            ret.pop('description')
            ret.pop('date')
            ret.pop('status')
            ret.pop('was_deleted')
        elif self.context['request'].method == 'GET':
            if 'requester_id' in self.context['request'].GET:
                ret.pop('requester')
            elif 'proposal_id' in self.context['request'].GET:
                ret.pop('adoption_proposal')
            ret.pop('was_deleted')
        return ret

    class Meta:
        """ Meta class for AdoptionRequest serializer """
        model = AdoptionRequest
        fields = ['id', 'adoption_proposal', 'requester', 'status',
                  'description', 'date', 'was_deleted']
        extra_kwargs = {'id': {'read_only': True, 'required': False}}

    def __init__(self, *args, **kwargs):
        super(AdoptionRequestSerializer, self).__init__(*args, **kwargs)
        if self.context['request'].method == 'GET':
            self.fields['requester'] =\
                PersonSerializer(read_only=True, context=kwargs['context'])
            self.fields['adoption_proposal'] =\
                AdoptionProposalSerializer(read_only=True,
                                           context=kwargs['context'])

    def create(self, validated_data):
        """ Method create for the serializer """
        if (AdoptionRequest.objects
            .filter(adoption_proposal=validated_data['adoption_proposal'])
                .exists()):
            return (AdoptionRequest.objects
                    .get(adoption_proposal=validated_data['adoption_proposal']))
        else:
            adoption_request = AdoptionRequest.objects.create(**validated_data)
            person_devices = find_devices(adoption_request.adoption_proposal
                                          .owner.id)
            title = 'SOSFIDO'
            message = ('Se ha enviado una petición a tu propuesta de ' +
                       'adopción de tu mascota ' +
                       adoption_request.adoption_proposal.pet_name)
            data_notification = {'proposal_id': adoption_request
                                 .adoption_proposal.id}
            image_notification = 'https://s3.amazonaws.com/uploads.hipchat.' + \
                                 'com/529035/4489842/wDKOTjEIqyr1pPX/' + \
                                 'logo_sosfido1.png'
            send_notification_mobile(person_devices, title, message,
                                     data_notification, image_notification)
            return adoption_request

    def update(self, instance, validated_data):
        """ Method update for the serializer """
        if 'status' in validated_data:
            instance.status = validated_data['status']
        if 'description' in validated_data:
            instance.description = validated_data['description']
        if 'was_deleted' in validated_data:
            instance.was_deleted = validated_data['was_deleted']
        instance.save()
        return instance


class TokenSerializer(ModelSerializer):
    """ Serializer for the token of an user """
    user = UserSerializer()
    status = SerializerMethodField('bool')

    class Meta:
        """ Meta class for the token serializer """
        model = AccessToken
        fields = ('token', 'user', 'status',)

    @staticmethod
    def setup_eager_loading(queryset):
        """ Perform necessary eager loading of data """
        queryset = queryset.select_related('user')
        return queryset

    def bool(self, obj):
        """ This method only return a boolean variable """
        return True


class ApplicationSerializer(ModelSerializer):
    """ Serializer for the client token """
    status = SerializerMethodField('bool')

    class Meta:
        """ Meta class for Application serializer """
        model = Application
        fields = ('client_id', 'client_secret', 'status',)

    def bool(self, obj):
        """ This method only return a boolean variable """
        return True


class PersonDeviceSerializer(ModelSerializer):
    """ Serializer for PersonDevice model """
    def to_representation(self, obj):
        ret = super(PersonDeviceSerializer, self).to_representation(obj)
        if self.context['request'].method == 'POST':
            ret.pop('person')
        elif self.context['request'].method == 'GET':
            if 'person_id' in self.context['request'].GET:
                ret.pop('person')
        return ret

    class Meta:
        """ Meta class for PersonDevice serializer """
        model = PersonDevice
        fields = ['id', 'person', 'id_device', 'is_active']
        extra_kwargs = {'id': {'read_only': True, 'required': False}}

    def __init__(self, *args, **kwargs):
        super(PersonDeviceSerializer, self).__init__(*args, **kwargs)
        if self.context['request'].method == 'GET':
            self.fields['person'] =\
                PersonSerializer(read_only=True, context=kwargs['context'])
