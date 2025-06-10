from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from api.serializers import NouveauCasSerializer


class NouveauCasView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = NouveauCasSerializer(data=request.data)
        if serializer.is_valid():
            echantillon = serializer.save()
            return Response({"message": "Nouveau cas enregistré avec succès!", "code_echantillon": echantillon.code_echantillon}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)