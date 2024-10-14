from rest_framework import serializers
from .models import Client_model,Project_model
from django.contrib.auth.models import User

class client_serializer(serializers.ModelSerializer):
        created_by_username = serializers.CharField(source='created_by.username', read_only=True)

        class Meta:
                model = Client_model
                fields = ['id', 'client_name', 'created_at', 'created_by_username']


class user_serializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']


class project_serializer(serializers.ModelSerializer):
    users = serializers.ListField(child=serializers.DictField(child=serializers.CharField()), write_only=True)  # Expect a list of dicts with id and name

    class Meta:
        model = Project_model
        fields = ['id', 'project_name', 'client', 'users', 'created_by', 'created_at']

    def create(self, validated_data):
        users_data = validated_data.pop('users')  # Extract users from validated_data
        project = Project_model.objects.create(**validated_data)  # Create the project

        # Associate users with the project
        user_ids = [user['id'] for user in users_data]  # Extract user IDs
        project.users.set(user_ids)  # Associate users
        project.save()

        return project


