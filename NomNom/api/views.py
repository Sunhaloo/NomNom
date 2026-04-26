from django.db import transaction
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from rest_framework import permissions, status, viewsets, authentication
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from orders.models import Order
from delivery.models import Delivery
from payments.models import Payment
from review.models import Review
from common.stats import get_business_stats
from .serializers import DeliverySerializer, OrderSerializer, UserProfileSerializer
import logging

logger = logging.getLogger(__name__)


class OrderViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint to list or retrieve orders for the authenticated user.

    - GET /api/v1/orders/: list of the current user's orders
    - GET /api/v1/orders/<id>/: single order (only if it belongs to the user)
    """

    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [
        authentication.SessionAuthentication,
        authentication.TokenAuthentication,
    ]

    def get_queryset(self):
        user = self.request.user
        qs = Order.objects.filter(user=user)

        status_param = self.request.query_params.get("status")
        if status_param:
            normalized = status_param.strip().lower()
            status_map = {
                "pending": "Pending",
                "paid": "Paid",
                "cancelled": "Cancelled",
                "canceled": "Cancelled",
            }
            status_value = status_map.get(normalized, status_param.strip())
            qs = qs.filter(order_status__iexact=status_value)

        return qs.order_by("-order_date")


class DeliveryViewSet(viewsets.ReadOnlyModelViewSet):
    """Delivery endpoints for the authenticated user.

    - GET /api/v1/deliveries/:
        list of the user's deliveries; by default only Pending ones.
    - GET /api/v1/deliveries/<id>/:
        details for a single delivery (only if it belongs to the user).
    - POST /api/v1/deliveries/<id>/confirm/:
        mark a pending delivery as Done.
    - POST /api/v1/deliveries/<id>/cancel/:
        cancel a pending delivery, cancel the related order, and refund payments.
    """

    serializer_class = DeliverySerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [
        authentication.SessionAuthentication,
        authentication.TokenAuthentication,
    ]

    def get_queryset(self):
        user = self.request.user
        qs = Delivery.objects.select_related("order").filter(order__user=user)

        status_param = self.request.query_params.get("status")
        if status_param:
            normalized = status_param.strip().lower()
            status_map = {
                "pending": "Pending",
                "done": "Done",
                "delivered": "Done",
                "failed": "Failed",
                "cancelled": "Cancelled",
                "canceled": "Cancelled",
            }
            status_value = status_map.get(normalized, status_param.strip())
            qs = qs.filter(status__iexact=status_value)
        else:
            qs = qs.filter(status="Pending")

        return qs.order_by("-date", "-id")

    @action(detail=True, methods=["post"])
    def confirm(self, request, pk=None):
        delivery = self.get_object()

        if delivery.status != "Pending":
            return Response(
                {
                    "success": False,
                    "error": "Only pending deliveries can be confirmed.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        delivery.status = "Done"
        delivery.save(update_fields=["status"])

        return Response(
            {
                "success": True,
                "delivery_id": delivery.id,
                "new_status": delivery.status,
            },
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=["post"],
        url_path="confirm-with-photo",
        parser_classes=[MultiPartParser, FormParser],
    )
    def confirm_with_photo(self, request, pk=None):
        """
        Confirm delivery with photo proof and QR validation
        
        Expected: multipart/form-data with 'photo' or 'confirmation_photo' file
        Returns: Confirmed delivery or error
        """
        delivery = self.get_object()
        
        # Validate delivery is pending
        if delivery.status != "Pending":
            return Response(
                {
                    "error": f"Delivery status is {delivery.status}, not Pending",
                    "current_status": delivery.status
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get photo from request
        photo = request.FILES.get("photo") or request.FILES.get("confirmation_photo")
        if not photo:
            return Response(
                {"error": "Photo file is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            photo_bytes = photo.read()
            
            # TODO: Validate QR code in photo
            # For now, just accept the photo
            # In future, mobile app will validate QR before upload
            
            # Store photo and mark as done
            delivery.confirmation_photo = photo_bytes
            delivery.confirmed_at = timezone.now()
            delivery.status = "Done"
            delivery.save()
            
            logger.info(f"Delivery {delivery.id} confirmed with photo")
            
            return Response({
                "success": True,
                "delivery_id": delivery.id,
                "status": delivery.status,
                "confirmed_at": delivery.confirmed_at
            })
        
        except Exception as e:
            logger.error(f"Error confirming delivery: {str(e)}")
            return Response(
                {"error": f"Failed to process photo: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        delivery = self.get_object()
        order = delivery.order

        if delivery.status != "Pending":
            return Response(
                {
                    "success": False,
                    "error": "Only pending deliveries can be cancelled.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            delivery.status = "Cancelled"
            delivery.save(update_fields=["status"])

            # Cancel order
            order.order_status = "Cancelled"
            order.save(update_fields=["order_status"])

            # Refund payments for this order
            Payment.objects.filter(order=order, payment_status="Paid").update(
                payment_status="Refunded"
            )

        return Response(
            {
                "success": True,
                "delivery_id": delivery.id,
                "order_id": order.id,
                "order_status": order.order_status,
                "delivery_status": delivery.status,
            },
            status=status.HTTP_200_OK,
        )


@method_decorator(csrf_exempt, name='dispatch')
class CurrentUserView(APIView):
    """Read-only profile endpoint for the authenticated user.

    - GET /api/v1/users/me/:
        returns a minimal profile with name and address parts that the
        mobile app can use for things like Google Maps integration.
    """

    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [
        authentication.SessionAuthentication,
        authentication.TokenAuthentication,
    ]

    def get(self, request, *args, **kwargs):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)


@method_decorator(csrf_exempt, name='dispatch')
class LogoutView(APIView):
    """Simple token revocation endpoint for mobile/external clients.

    - POST /api/v1/auth/logout/:
        Deletes all auth tokens for the current user. After this call,
        any previously issued tokens will no longer authenticate.
    """

    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [
        authentication.SessionAuthentication,
        authentication.TokenAuthentication,
    ]

    def post(self, request, *args, **kwargs):
        Token.objects.filter(user=request.user).delete()
        return Response({"success": True}, status=status.HTTP_200_OK)


@method_decorator(csrf_exempt, name='dispatch')
class BusinessStatsView(APIView):
    """Get business statistics - caches on client side
    
    - GET /api/v1/stats/:
        Returns dynamic business statistics
    """
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [
        authentication.SessionAuthentication,
        authentication.TokenAuthentication,
    ]
    
    def get(self, request):
        """Retrieve business statistics"""
        try:
            stats = get_business_stats()
            return Response(stats)
        except Exception as e:
            logger.error(f"Error fetching stats: {str(e)}")
            return Response(
                {"error": "Failed to fetch statistics"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class TopReviewsView(APIView):
    """Get top 5-star reviews with text
    
    - GET /api/v1/reviews/top-rated/:
        Returns top 5-star reviews
    """
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        """Retrieve top 5-star reviews"""
        try:
            reviews = Review.objects.filter(
                rating=5
            ).exclude(
                comment__exact=""
            ).order_by("-date")[:10]
            
            # Serialize manually
            review_data = []
            for review in reviews:
                review_data.append({
                    "id": review.id,
                    "user_name": f"{review.user.first_name} {review.user.last_name}".strip(),
                    "rating": review.rating,
                    "comment": review.comment,
                    "date": review.date.strftime("%b %d, %Y")
                })
            
            return Response(review_data)
        except Exception as e:
            logger.error(f"Error fetching reviews: {str(e)}")
            return Response(
                {"error": "Failed to fetch reviews"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@method_decorator(csrf_exempt, name='dispatch')
class SignupView(APIView):
    """User registration endpoint for mobile app
    
    - POST /api/v1/auth/signup/:
        Register a new user
    """
    permission_classes = [permissions.AllowAny]
    
    @transaction.atomic
    def post(self, request):
        """
        Register a new user
        
        Expected fields:
        - username: str
        - first_name: str
        - last_name: str
        - email: str
        - password: str
        - phone_number: str (optional)
        - street: str (optional)
        - region: str (optional)
        - gender: str (M/F, optional)
        """
        
        User = get_user_model()
        
        # Validate required fields
        required_fields = ["username", "first_name", "last_name", "email", "password"]
        missing_fields = [f for f in required_fields if not request.data.get(f)]
        
        if missing_fields:
            return Response(
                {"error": f"Missing required fields: {', '.join(missing_fields)}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if user already exists
        if User.objects.filter(username=request.data["username"]).exists():
            return Response(
                {"error": "Username already exists"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if User.objects.filter(email=request.data["email"]).exists():
            return Response(
                {"error": "Email already registered"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Create user
            user = User.objects.create_user(
                username=request.data["username"],
                email=request.data["email"],
                password=request.data["password"],
                first_name=request.data["first_name"],
                last_name=request.data["last_name"],
                phone_number=request.data.get("phone_number", ""),
                street=request.data.get("street", ""),
                region=request.data.get("region", ""),
                gender=request.data.get("gender", ""),
                role="CUSTOMER"  # Default role for signup
            )
            
            # Generate token
            token, _ = Token.objects.get_or_create(user=user)
            
            logger.info(f"New user registered: {user.username}")
            
            serializer = UserProfileSerializer(user)

            return Response({
                "success": True,
                "data": {
                    "token": token.key,
                    "user": serializer.data
                }
            }, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            logger.error(f"Registration error: {str(e)}")
            return Response(
                {"error": f"Registration failed: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )


@method_decorator(csrf_exempt, name='dispatch')
class CustomTokenView(APIView):
    """Custom token endpoint that returns data in format expected by mobile app"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        """
        Login endpoint - returns token and user info
        
        Expected fields:
        - username: str
        - password: str
        """
        from django.contrib.auth import authenticate
        from rest_framework.authtoken.models import Token
        
        username = (request.data.get("username") or "").strip()
        password = (request.data.get("password") or "").strip()
        
        if not username or not password:
            return Response(
                {"success": False, "message": "Username and password are required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = authenticate(request, username=username, password=password)

        # Convenience: allow logging in with email in the "username" field.
        if not user and "@" in username:
            User = get_user_model()
            matched = User.objects.filter(email__iexact=username).only("username").first()
            if matched:
                user = authenticate(request, username=matched.username, password=password)
        
        if not user:
            logger.debug(
                "API token auth failed",
                extra={
                    "username_repr": repr(username),
                    "username_len": len(username),
                    "username_has_whitespace": any(c.isspace() for c in username),
                    "content_type": request.META.get("CONTENT_TYPE"),
                },
            )
            return Response(
                {"success": False, "message": "Invalid credentials"},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        token, _ = Token.objects.get_or_create(user=user)
        serializer = UserProfileSerializer(user)

        
        return Response({
            "success": True,
            "data": {
                "token": token.key,
                "user": serializer.data
            }
        }, status=status.HTTP_200_OK)
    


 
