try:
    from rest_framework import serializers
except Exception:
    serializers = None

if serializers:
    from .models import EmissionRecord


    class EmissionRecordSerializer(serializers.ModelSerializer):
        class Meta:
            model = EmissionRecord
            fields = "__all__"
