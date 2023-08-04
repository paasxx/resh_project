from rest_framework.serializers import ( CharField, EmailField, ModelSerializer)
from rest_framework.validators import UniqueValidator
from django.contrib.auth.models import User




class UserSerializer(ModelSerializer):

    email = EmailField(required=True, validators=[UniqueValidator(queryset=User.objects.all())])
    username = CharField(required=True, max_length = 32, validators=[UniqueValidator(queryset=User.objects.all())])
    password = CharField( required=True, min_length = 8, write_only=False)

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance
    
    
    class Meta:
        model = User
        fields = ( 'username', 'password', 'email', 'id')

