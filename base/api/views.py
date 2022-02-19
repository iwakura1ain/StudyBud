from rest_framework.decorators import api_view
from rest_framework.response import Response
from base.models import Room
from .serializers import RoomSerializer


@api_view(['GET'])
def GetRoutes(request):
    routes = [
        'GET /api',
        'GET /api/rooms',
        'GET /api/rooms/:id'
    ]

    return Response(routes)


@api_view(['GET'])
def GetRooms(request):
    serializers = RoomSerializer(Room.objects.all(), many=True)
    return Response(serializers.data)


@api_view(['GET'])
def GetRoom(request, key):
    serializers = RoomSerializer(Room.objects.get(id=key), many=False)
    return Response(serializers.data)


