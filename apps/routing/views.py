from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def protected_test(request):
    return Response({
        "message": "You are authenticated!",
        "user": str(request.user)
    })
def test_api(request):
    return JsonResponse({"message": "Routing app working"})