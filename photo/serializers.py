from rest_framework import serializers


class SnippetSerializer(serializers.Serializer):
    img_path = serializers.ImageField()
    f = serializers.FloatField()
    k1 = serializers.FloatField()
    k2 = serializers.FloatField()
