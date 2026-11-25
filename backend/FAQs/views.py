from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from django.shortcuts import get_object_or_404

from .models import FAQ
from .serializers import FAQSerializer
from .permissions import IsAdminOrReadOnly

from django.db.models import Q


class FAQListCreateAPIView(APIView):

    permission_classes = [
        IsAuthenticated,
        IsAdminOrReadOnly,
    ]

    def get(self, request):

        if request.user.role == "ADMIN":
            faqs = FAQ.objects.all()
        else:
            faqs = FAQ.objects.filter(is_published=True)

        # Search by question or answer
        search_query = request.query_params.get("search")

        if search_query:
            faqs = faqs.filter(
                Q(question__icontains=search_query) |
                Q(answer__icontains=search_query)
            )

        # Filter by category
        category = request.query_params.get("category")

        if category:
            faqs = faqs.filter(category=category.upper())

        faqs = faqs.order_by("-created_at")

        serializer = FAQSerializer(faqs, many=True)

        return Response({
            "success": True,
            "count": faqs.count(),
            "data": serializer.data,
        }, 
        status=status.HTTP_200_OK)

    def post(self, request):

        serializer = FAQSerializer(data=request.data)

        if serializer.is_valid():

            faq = serializer.save()

            return Response({
                "success": True,
                "message": "FAQ created successfully.",
                "data": FAQSerializer(faq).data,
            }, status=status.HTTP_201_CREATED)

        return Response({
            "success": False,
            "errors": serializer.errors,
        }, status=status.HTTP_400_BAD_REQUEST)


class FAQDetailAPIView(APIView):

    permission_classes = [
        IsAuthenticated,
        IsAdminOrReadOnly,
    ]

    def get_object(self, request, faq_id):

        if request.user.role == "ADMIN":
            queryset = FAQ.objects.all()
        else:
            queryset = FAQ.objects.filter(is_published=True)

        return get_object_or_404(queryset, id=faq_id)

    def get(self, request, faq_id):

        faq = self.get_object(request, faq_id)

        serializer = FAQSerializer(faq)

        return Response({
            "success": True,
            "data": serializer.data,
        }, status=status.HTTP_200_OK)

    def patch(self, request, faq_id):

        faq = self.get_object(request, faq_id)

        serializer = FAQSerializer(
            faq,
            data=request.data,
            partial=True,
        )

        if serializer.is_valid():

            serializer.save()

            return Response({
                "success": True,
                "message": "FAQ updated successfully.",
                "data": serializer.data,
            }, status=status.HTTP_200_OK)

        return Response({
            "success": False,
            "errors": serializer.errors,
        }, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, faq_id):

        faq = self.get_object(request, faq_id)

        faq.delete()

        return Response({
            "success": True,
            "message": "FAQ deleted successfully.",
        }, status=status.HTTP_200_OK)