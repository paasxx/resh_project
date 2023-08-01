from django.contrib.auth import get_user_model
from rest_framework.serializers import ( CharField, EmailField, HyperlinkedIdentityField, ModelSerializer, SerializerMethodField, ValidationError,UniqueTogetherValidator)
from rest_framework.validators import UniqueValidator
from django.contrib.auth.models import User
from rest_framework_jwt.settings import api_settings

User = get_user_model()

class UserSerializer(ModelSerializer):

    token = SerializerMethodField()

    email = EmailField(required=True, validators=[UniqueValidator(queryset=User.objects.all())])

    username = CharField(required=True, max_length = 32, validators=[UniqueValidator(queryset=User.objects.all())])

    password = CharField( required=True, min_length = 8, write_only=True)

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance
    
    def get_token(self, obj):
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
        payload = jwt_payload_handler(obj)
        token = jwt_encode_handler(payload)
        return token
    
    class Meta:

        model = User

        fields = ('token', 'username', 'password', 'email', 'id')
