from rest_framework import serializers

from .models import Account

class AccountDetailSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Account
        fields = ('id','username', 'email' , 'password','date_joined','last_login')