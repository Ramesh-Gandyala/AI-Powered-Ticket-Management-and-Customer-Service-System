
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .permissions import(
                        IsCustomerOrAdmin,
                        IsAgentOrAdmin,
                        IsCustomer,
) 


from .serializers import (
    QuerySerializer,
    TicketCreateSerializer,
    TicketListSerializer,
    TicketStatusUpdateSerializer,
    TicketProgressSerializer,
)

from .models import Query, Ticket, TicketProgress

from django.db import transaction
from django.shortcuts import get_object_or_404

from .services import generate_ticket_id

from django.contrib.auth import get_user_model


class QuerySubmissionAPIView(APIView):

    permission_classes = [
        IsAuthenticated,
        IsCustomerOrAdmin,
    ]

    def post(self, request):

        serializer = QuerySerializer(data=request.data)

        if serializer.is_valid():

            query = serializer.save(
                submitted_by=request.user
            )

            return Response(
                {
                    "success": True,
                    "message": "Query submitted successfully.",
                    "data": {
                        "id": query.id,
                        "status": query.status,
                    },
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(
            {
                "success": False,
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


class PendingQueriesAPIView(APIView):

    permission_classes = [
        IsAuthenticated,
        IsAgentOrAdmin,
    ]

    def get(self, request):

        pending_queries = Query.objects.filter(
            status=Query.QueryStatus.PENDING
        ).select_related("submitted_by").order_by("-created_at")

        serializer = QuerySerializer(
            pending_queries,
            many=True
        )

        return Response(
            {
                "success": True,
                "count": pending_queries.count(),
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

class AllQueriesAPIView(APIView):

    permission_classes = [
        IsAuthenticated,
        IsAgentOrAdmin,
    ]

    def get(self, request):

        all_queries = Query.objects.select_related(
            "submitted_by"
        ).order_by("-created_at")

        serializer = QuerySerializer(
            all_queries,
            many=True
        )

        return Response(
            {
                "success": True,
                "count": all_queries.count(),
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class MyQueriesAPIView(APIView):

    permission_classes = [
        IsAuthenticated,
        IsCustomer,
    ]

    def get(self, request):

        my_queries = Query.objects.filter(
            submitted_by=request.user
        ).order_by("-created_at")

        serializer = QuerySerializer(
            my_queries,
            many=True
        )

        return Response(
            {
                "success": True,
                "count": my_queries.count(),
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )



class TicketCreationAPIView(APIView):

    permission_classes = [
        IsAuthenticated,
        IsAgentOrAdmin,
    ]

    def post(self, request):

        # Step 1: Validate incoming data
        serializer = TicketCreateSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {
                    "success": False,
                    "errors": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Step 2: Get validated data
        query_id = serializer.validated_data["query_id"]

        assigned_agent_id = serializer.validated_data.get(
            "assigned_agent"
        )

        # Step 3: Start database transaction
        with transaction.atomic():

            # Step 4: Retrieve and lock the query
            query = get_object_or_404(
                Query.objects.select_for_update(),
                id=query_id
            )

            # Step 5: Check whether a ticket already exists
            if query.status == Query.QueryStatus.TICKET_CREATED:
                return Response(
                    {
                        "success": False,
                        "message": "A ticket already exists for this query.",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Step 6: Retrieve the assigned Agent, if provided
            assigned_agent = None

            if assigned_agent_id is not None:

                User = get_user_model()

                assigned_agent = get_object_or_404(
                    User,
                    id=assigned_agent_id,
                    role="AGENT",
                    is_active=True,
                )

            # Step 7: Identify the customer
            if query.submitted_by.role == "CUSTOMER":
                customer = query.submitted_by
            else:
                customer = None

            # Step 8: Generate category-based ticket ID
            ticket_id = generate_ticket_id(query.category)

            # Step 9: Create the ticket
            ticket = Ticket.objects.create(
                ticket_id=ticket_id,
                query=query,
                customer=customer,
                assigned_agent=assigned_agent,
                created_by=request.user,
                status=Ticket.TicketStatus.OPEN,
            )

            # Step 10: Update query status
            query.status = Query.QueryStatus.TICKET_CREATED
            query.save(update_fields=["status", "updated_at"])

            # Step 11: Create initial progress history
            TicketProgress.objects.create(
                ticket=ticket,
                previous_status=None,
                new_status=Ticket.TicketStatus.OPEN,
                updated_by=request.user,
                remarks="Ticket created successfully.",
            )

        # Step 12: Return successful response
        return Response(
            {
                "success": True,
                "message": "Ticket created successfully.",
                "data": {
                    "ticket_id": ticket.ticket_id,
                    "query_id": query.id,
                    "customer_id": customer.id if customer else None,
                    "assigned_agent_id": (
                        assigned_agent.id if assigned_agent else None
                    ),
                    "created_by": request.user.id,
                    "status": ticket.status,
                    "created_at": ticket.created_at,
                },
            },
            status=status.HTTP_201_CREATED,
        )


class AllTicketsAPIView(APIView):

    permission_classes = [
        IsAuthenticated,
        IsAgentOrAdmin,
    ]

    def get(self, request):

        tickets = Ticket.objects.select_related(
            "query",
            "customer",
            "assigned_agent",
            "created_by",
        ).order_by("-created_at")

        serializer = TicketListSerializer(
            tickets,
            many=True
        )

        return Response(
            {
                "success": True,
                "count": tickets.count(),
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )



class MyTicketsAPIView(APIView):

    permission_classes = [
        IsAuthenticated,
        IsCustomer,
    ]

    def get(self, request):

        my_tickets = Ticket.objects.filter(
            customer=request.user
        ).select_related(
            "query",
            "customer",
            "assigned_agent",
            "created_by",
        ).order_by("-created_at")

        serializer = TicketListSerializer(
            my_tickets,
            many=True
        )

        return Response(
            {
                "success": True,
                "count": my_tickets.count(),
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class TicketStatusUpdateAPIView(APIView):

    permission_classes = [
        IsAuthenticated,
        IsAgentOrAdmin,
    ]

    def patch(self, request, ticket_id):

        # Step 1: Validate request data
        serializer = TicketStatusUpdateSerializer(
            data=request.data
        )

        if not serializer.is_valid():
            return Response(
                {
                    "success": False,
                    "errors": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Step 2: Start database transaction
        with transaction.atomic():

            # Step 3: Retrieve and lock ticket
            ticket = get_object_or_404(
                Ticket.objects.select_for_update(),
                ticket_id=ticket_id
            )

            # Step 4: Store previous status
            previous_status = ticket.status

            # Step 5: Get new status and remarks
            new_status = serializer.validated_data["status"]

            remarks = serializer.validated_data.get(
                "remarks",
                ""
            )

            # Step 6: Update ticket status
            ticket.status = new_status

            ticket.save(
                update_fields=["status", "updated_at"]
            )

            # Step 7: Create progress history
            progress = TicketProgress.objects.create(
                ticket=ticket,
                previous_status=previous_status,
                new_status=new_status,
                updated_by=request.user,
                remarks=remarks,
            )

        # Step 8: Return response
        return Response(
            {
                "success": True,
                "message": "Ticket status updated successfully.",
                "data": {
                    "ticket_id": ticket.ticket_id,
                    "previous_status": progress.previous_status,
                    "new_status": progress.new_status,
                    "updated_by": request.user.username,
                    "remarks": progress.remarks,
                    "updated_at": progress.created_at,
                },
            },
            status=status.HTTP_200_OK,
        )



class MyTicketProgressAPIView(APIView):

    permission_classes = [
        IsAuthenticated,
        IsCustomer,
    ]

    def get(self, request, ticket_id):

        # Retrieve only the logged-in customer's ticket
        ticket = get_object_or_404(
            Ticket,
            ticket_id=ticket_id,
            customer=request.user,
        )

        # Retrieve ticket progress history
        progress_history = ticket.progress_history.order_by(
            "created_at"
        )

        serializer = TicketProgressSerializer(
            progress_history,
            many=True
        )

        return Response(
            {
                "success": True,
                "ticket_id": ticket.ticket_id,
                "current_status": ticket.status,
                "count": progress_history.count(),
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )
