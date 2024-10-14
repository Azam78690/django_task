from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .serializer import client_serializer, project_serializer, user_serializer
from .models import Client_model, Project_model
from django.contrib.auth.models import User


@api_view(['GET', 'POST'])
def client_get_post(request):
    if request.method == 'GET':
        clients = Client_model.objects.all()
        serializer = client_serializer(clients, many=True)
        if serializer.data:
            response_data_list = []
            for item in serializer.data:
                response_data = {
                    'id': item['id'],
                    'client_name': item['client_name'],
                    'created_at': item['created_at'],
                    'created_by': item['created_by_username']
                }
                response_data_list.append(response_data)
            return Response(response_data_list)
        else:
            return Response({'No clients found'})

    if request.method == 'POST':
        serializer = client_serializer(data=request.data)
        response_data = {}
        if serializer.is_valid():
            serializer.save(created_by=request.user)
            if serializer.data:
                response_data = {
                    'id': serializer.data['id'],
                    'client_name': serializer.data['client_name'],
                    'created_at': serializer.data['created_at'],
                    'created_by': request.user.username
                    }
        return Response(response_data)


@api_view(['GET', 'PUT', 'DELETE'])
def client_get_put_delete(request, id):
    client_detail = get_object_or_404(Client_model, pk=id)
    projects = client_detail.projects.all()
    if request.method == 'GET':
        client_serialized = client_serializer(client_detail)
        project_serialized = project_serializer(projects, many=True)
        project_response = []
        if project_serialized.data:
            for project in project_serialized.data:
                project_response.append({
                    'id': project['id'],
                    'name': project['project_name']
                })
        response_data = {
            'id': client_serialized.data['id'],
            'client_name': client_serialized.data['client_name'],
            'projects': project_response,
            'created_at': client_serialized.data['created_at'],
            'created_by': client_serialized.data['created_by_username'],
        }
        return Response(response_data, status=200)

    elif request.method == 'PUT':
        serializer = client_serializer(client_detail, data=request.data)
        if serializer.is_valid():
            serializer.save()
            response_data = {
                'id': serializer.data['id'],
                'client_name': serializer.data['client_name'],
                'created_at': serializer.data['created_at'],
                'created_by': client_detail.created_by.username,
                'updated_at': client_detail.updated_at
            }
            return Response(response_data)

    elif request.method == 'DELETE':
        client_detail.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
def create_project(request, id):
    client = get_object_or_404(Client_model, pk=id)
    request_data = {
        'project_name': request.data.get('project_name'),
        'client': client.id,
        'created_by': request.user.id,
        'users': request.data.get('users', []),
    }
    project_detail = project_serializer(data=request_data)
    if project_detail.is_valid():
        project = project_detail.save()
        response_data = {
            'id': project.id,
            'project_name': project.project_name,
            'client': project.client.client_name,
            'users': [{'id': user.id, 'name': user.username} for user in project.users.all()],
            'created_at': project.created_at,
            'created_by': project.created_by.username
        }
        return Response(response_data, status=status.HTTP_201_CREATED)
    return Response(project_detail.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def projects(request):
    project_detail = Project_model.objects.filter(users=request.user)
    if not project_detail.exists():
        return Response({"detail": "No projects found for this user."}, status=404)
    serializer = project_serializer(project_detail, many=True)
    response_data_list = []
    for i in range(len(serializer.data)):
        response_data = {
            'id': serializer.data[i]['id'],
            'project_name': serializer.data[i]['project_name'],
            'created_at': serializer.data[i]['created_at'],
            'created_by':  User.objects.get(id=serializer.data[i]['created_by']).username,
        }
        response_data_list.append(response_data)
    return Response(response_data_list)
    #return Response(serializer.data, status=200)