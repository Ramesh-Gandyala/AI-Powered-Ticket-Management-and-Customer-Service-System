
from rest_framework import serializers

from .models import Query, Ticket, TicketProgress


class QuerySerializer(serializers.ModelSerializer):

    class Meta:
        model = Query

        fields = [
            "id",
            "submitted_by",
            "query",
            "category",
            "status",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "submitted_by",
            "status",
            "created_at",
            "updated_at",
        ]

    def validate_query(self, value):
        if not value.strip():
            raise serializers.ValidationError(
                "Query cannot be empty."
            )

        return value.strip()

class TicketCreateSerializer(serializers.Serializer):

    query_id = serializers.IntegerField()

    assigned_agent = serializers.IntegerField(
        required=False,
        allow_null=True
    )

    def validate_query_id(self, value):

        try:
            query = Query.objects.get(id=value)
        except Query.DoesNotExist:
            raise serializers.ValidationError(
                "Query does not exist."
            )

        if query.status == Query.QueryStatus.TICKET_CREATED:
            raise serializers.ValidationError(
                "A ticket has already been created for this query."
            )

        return value

    def validate_assigned_agent(self, value):

        if value is None:
            return value

        from django.contrib.auth import get_user_model

        User = get_user_model()

        try:
            agent = User.objects.get(
                id=value,
                role="AGENT",
                is_active=True
            )
        except User.DoesNotExist:
            raise serializers.ValidationError(
                "Selected Agent does not exist or is inactive."
            )

        return value

class TicketListSerializer(serializers.ModelSerializer):

    category = serializers.CharField(
        source="query.category",
        read_only=True
    )

    customer_name = serializers.CharField(
        source="customer.username",
        read_only=True,
        allow_null=True
    )

    assigned_agent_name = serializers.CharField(
        source="assigned_agent.username",
        read_only=True,
        allow_null=True
    )

    created_by_name = serializers.CharField(
        source="created_by.username",
        read_only=True
    )

    class Meta:
        model = Ticket
        fields = [
            "id",
            "ticket_id",
            "query",
            "category",
            "customer",
            "customer_name",
            "assigned_agent",
            "assigned_agent_name",
            "created_by",
            "created_by_name",
            "status",
            "created_at",
            "updated_at",
        ]

class TicketStatusUpdateSerializer(serializers.Serializer):

    status = serializers.ChoiceField(
        choices=Ticket.TicketStatus.choices
    )

    remarks = serializers.CharField(
        required=False,
        allow_blank=True
    )


class TicketProgressSerializer(serializers.ModelSerializer):

    updated_by_name = serializers.CharField(
        source="updated_by.username",
        read_only=True
    )

    class Meta:
        model = TicketProgress
        fields = [
            "id",
            "previous_status",
            "new_status",
            "updated_by",
            "updated_by_name",
            "remarks",
            "created_at",
        ]


class TicketAssignmentSerializer(serializers.Serializer):

    assigned_agent = serializers.IntegerField()

    def validate_assigned_agent(self, value):

        from django.contrib.auth import get_user_model

        User = get_user_model()

        try:
            agent = User.objects.get(
                id=value,
                role="AGENT",
                is_active=True
            )

        except User.DoesNotExist:
            raise serializers.ValidationError(
                "Selected Agent does not exist or is inactive."
            )

        return value
