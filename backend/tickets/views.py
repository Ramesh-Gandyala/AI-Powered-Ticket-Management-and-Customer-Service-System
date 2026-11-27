from notifications.models import Notification
from notifications.services import (
    create_notification,
    send_notification_email,
)


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
    TicketAssignmentSerializer,
)

from .models import Query, Ticket, TicketProgress

from django.db import transaction
from django.shortcuts import get_object_or_404

from .services import generate_ticket_id

from django.contrib.auth import get_user_model

from ai_support.services import classify_customer_query

import logging

logger = logging.getLogger(__name__)





class QuerySubmissionAPIView(APIView):

    permission_classes = [
        IsAuthenticated,
        IsCustomerOrAdmin,
    ]

    def post(self, request):

        serializer = QuerySerializer(data=request.data)

        if serializer.is_valid():

            customer_message = serializer.validated_data["query"]

            # Step 1: Ask ULTRON to classify the query
            try:
                predicted_category = classify_customer_query(
                    customer_message
                )

            except Exception:
                logger.exception(
                    "ULTRON failed to classify the customer query."
                )

                predicted_category = Query.QueryCategory.GENERAL

            # Step 2: Save query and database notification together
            # If notification creation fails, query creation is rolled back.
            with transaction.atomic():

                query = serializer.save(
                    submitted_by=request.user,
                    category=predicted_category
                )

                create_notification(
                    recipient=request.user,
                    title="Query Submitted Successfully",
                    message=(
                        f"Your query #{query.id} has been submitted "
                        "successfully. ULTRON has classified your query "
                        f"under {query.category}."
                    ),
                    notification_type=Notification.NotificationType.QUERY_SUBMITTED
                )

            # Step 3: Send email after the database transaction commits
            try:
                send_notification_email(
                    recipient=request.user,
                    subject="Your Query Has Been Submitted",
                    message=(
                        f"Hello {request.user.username},\n\n"
                        f"Your query #{query.id} has been submitted "
                        "successfully.\n"
                        f"Category: {query.category}\n\n"
                        "Thank you for contacting our support team."
                    )
                )

            except Exception:
                logger.exception(
                    "Failed to send query submission email."
                )

            # Step 4: Return API response
            return Response(
                {
                    "success": True,
                    "message": "Query submitted successfully.",
                    "data": {
                        "id": query.id,
                        "status": query.status,
                        "category": query.category,
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

            # Step 12: Create customer notification
            if customer:

                create_notification(
                    recipient=customer,
                    title="Ticket Created Successfully",
                    message=(
                        f"Your ticket {ticket.ticket_id} has been created "
                        "successfully. Our support team will assist you."
                    ),
                    notification_type=Notification.NotificationType.TICKET_CREATED
                )

            # Step 13: Create assigned agent notification
            if assigned_agent:

                create_notification(
                    recipient=assigned_agent,
                    title="New Ticket Assigned",
                    message=(
                        f"Ticket {ticket.ticket_id} has been assigned to you. "
                        "Please review the ticket and assist the customer."
                    ),
                    notification_type=Notification.NotificationType.TICKET_ASSIGNED
                )

        # Step 14: Send ticket creation email to customer
        if customer:

            try:
                send_notification_email(
                    recipient=customer,
                    subject="Your Support Ticket Has Been Created",
                    message=(
                        f"Hello {customer.username},\n\n"
                        "Your support ticket has been created successfully.\n\n"
                        f"Ticket ID: {ticket.ticket_id}\n"
                        f"Category: {query.category}\n"
                        f"Status: {ticket.status}\n\n"
                        "Our support team will assist you shortly.\n\n"
                        "Thank you for contacting our support team."
                    )
                )

            except Exception:
                logger.exception(
                    "Failed to send ticket creation email."
                )

        # Step 15: Send ticket assignment email to agent
        if assigned_agent:

            try:
                send_notification_email(
                    recipient=assigned_agent,
                    subject="A New Support Ticket Has Been Assigned to You",
                    message=(
                        f"Hello {assigned_agent.username},\n\n"
                        "A new support ticket has been assigned to you.\n\n"
                        f"Ticket ID: {ticket.ticket_id}\n"
                        f"Category: {query.category}\n"
                        f"Customer: {customer.username if customer else 'Not available'}\n"
                        f"Status: {ticket.status}\n\n"
                        "Please review the ticket and assist the customer."
                    )
                )

            except Exception:
                logger.exception(
                    "Failed to send ticket assignment email."
                )

        # Step 16: Return successful response
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

            # Step 8: Create customer notification
            if ticket.customer:

                create_notification(
                    recipient=ticket.customer,
                    title="Ticket Status Updated",
                    message=(
                        f"Your ticket {ticket.ticket_id} status "
                        f"has changed from {previous_status} "
                        f"to {new_status}."
                    ),
                    notification_type=(
                        Notification.NotificationType.TICKET_STATUS_UPDATED
                    )
                )

        # Step 9: Send customer email after transaction commits
        if ticket.customer:

            try:
                send_notification_email(
                    recipient=ticket.customer,
                    subject=f"Ticket Status Updated: {ticket.ticket_id}",
                    message=(
                        f"Hello {ticket.customer.username},\n\n"
                        "The status of your support ticket has been updated.\n\n"
                        f"Ticket ID: {ticket.ticket_id}\n"
                        f"Previous Status: {previous_status}\n"
                        f"New Status: {new_status}\n"
                        f"Updated By: {request.user.username}\n"
                        f"Remarks: {remarks if remarks else 'No remarks provided.'}\n\n"
                        "Thank you for contacting our support team."
                    )
                )

            except Exception:
                logger.exception(
                    "Failed to send ticket status update email."
                )

        # Step 10: Return response
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



class TicketAssignmentAPIView(APIView):

    permission_classes = [
        IsAuthenticated,
        IsAgentOrAdmin,
    ]

    def patch(self, request, ticket_id):

        # Step 1: Validate request data
        serializer = TicketAssignmentSerializer(
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

        # Step 2: Get the selected agent ID
        assigned_agent_id = serializer.validated_data[
            "assigned_agent"
        ]

        # Step 3: Start database transaction
        with transaction.atomic():

            # Step 4: Retrieve and lock the ticket
            ticket = get_object_or_404(
                Ticket.objects.select_for_update(),
                ticket_id=ticket_id
            )

            # Step 5: Store the previous assigned agent
            previous_agent = ticket.assigned_agent

            # Step 6: Retrieve the new assigned agent
            User = get_user_model()

            new_agent = get_object_or_404(
                User,
                id=assigned_agent_id,
                role="AGENT",
                is_active=True
            )

            # Step 7: Prevent unnecessary reassignment
            if previous_agent == new_agent:
                return Response(
                    {
                        "success": False,
                        "message": "This agent is already assigned to the ticket.",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Step 8: Update ticket assignment
            ticket.assigned_agent = new_agent

            ticket.save(
                update_fields=["assigned_agent", "updated_at"]
            )

            # Step 9: Create notification for the new agent
            create_notification(
                recipient=new_agent,
                title="New Ticket Assigned",
                message=(
                    f"Ticket {ticket.ticket_id} has been assigned to you. "
                    "Please review the ticket and assist the customer."
                ),
                notification_type=(
                    Notification.NotificationType.TICKET_ASSIGNED
                )
            )

            # Step 10: Notify the previous agent
            if previous_agent:

                create_notification(
                    recipient=previous_agent,
                    title="Ticket Reassigned",
                    message=(
                        f"Ticket {ticket.ticket_id} has been reassigned "
                        f"from you to {new_agent.username}."
                    ),
                    notification_type=(
                        Notification.NotificationType.GENERAL
                    )
                )

        # Step 11: Send assignment email to the new agent
        try:

            send_notification_email(
                recipient=new_agent,
                subject="A New Support Ticket Has Been Assigned to You",
                message=(
                    f"Hello {new_agent.username},\n\n"
                    "A support ticket has been assigned to you.\n\n"
                    f"Ticket ID: {ticket.ticket_id}\n"
                    f"Category: {ticket.query.category}\n"
                    f"Customer: {ticket.customer.username if ticket.customer else 'Not available'}\n"
                    f"Status: {ticket.status}\n\n"
                    "Please review the ticket and assist the customer."
                )
            )

        except Exception:
            logger.exception(
                "Failed to send ticket assignment email to new agent."
            )

        # Step 12: Send reassignment email to the previous agent
        if previous_agent:

            try:

                send_notification_email(
                    recipient=previous_agent,
                    subject="Your Support Ticket Has Been Reassigned",
                    message=(
                        f"Hello {previous_agent.username},\n\n"
                        "A support ticket previously assigned to you "
                        "has been reassigned to another agent.\n\n"
                        f"Ticket ID: {ticket.ticket_id}\n"
                        f"New Assigned Agent: {new_agent.username}\n"
                        f"Category: {ticket.query.category}\n"
                        f"Status: {ticket.status}\n\n"
                        "You are no longer responsible for this ticket."
                    )
                )

            except Exception:
                logger.exception(
                    "Failed to send reassignment email to previous agent."
                )

        # Step 13: Return response
        return Response(
            {
                "success": True,
                "message": "Ticket assigned successfully.",
                "data": {
                    "ticket_id": ticket.ticket_id,
                    "previous_agent": (
                        previous_agent.username
                        if previous_agent else None
                    ),
                    "assigned_agent": new_agent.username,
                    "assigned_agent_id": new_agent.id,
                    "updated_by": request.user.username,
                    "updated_at": ticket.updated_at,
                },
            },
            status=status.HTTP_200_OK,
        )
