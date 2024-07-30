from rest_framework import generics, viewsets, mixins, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import get_user_model
from .models import Passport, BankCard, Cv, Category, Order, Proposal, Job, Appeal, Review
from .serializers import UserSerializer, PassportSerializer, BankCardSerializer, CvSerializer, CategorySerializer, \
                        OrderSerializer, ProposalSerializer, JobSerializer, AppealSerializer, ReviewSerializer
from .permissions import IsAdmin
from rest_framework.response import Response
from django.db.models import Q
from .pagination import StandardResultsSetPagination

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)


class UserViewSet(mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.DestroyModelMixin,
                  mixins.ListModelMixin,
                  viewsets.GenericViewSet):

    queryset = User.objects.select_related('bank_card', 'cv').all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        user = self.request.user
        if 'Admin' in user.roles:
            return User.objects.all()
        else:
            return User.objects.filter(id=user.id)


class PassportViewSet(viewsets.ModelViewSet):
    queryset = Passport.objects.all()
    serializer_class = PassportSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        user = self.request.user
        if 'Admin' in user.roles:
            return Passport.objects.all()
        else:
            return Passport.objects.filter(owner=user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class BankCardViewSet(viewsets.ModelViewSet):
    queryset = BankCard.objects.all()
    serializer_class = BankCardSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        user = self.request.user
        if 'Admin' in user.roles:
            return BankCard.objects.all()
        else:
            return BankCard.objects.filter(owner=user)

    def create(self, request, *args, **kwargs):
        if 'Worker' not in request.user.roles:
            return Response({"detail": "Банк карту может создать только человек с ролю Worker."}, status=status.HTTP_403_FORBIDDEN)
        return super().create(request, *args, **kwargs)
    
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class CvViewSet(viewsets.ModelViewSet):
    queryset = Cv.objects.all()
    serializer_class = CvSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        user = self.request.user
        if 'Admin' in user.roles:
            return Cv.objects.all()
        else:
            return Cv.objects.filter(owner=user)
        
    def create(self, request, *args, **kwargs):
        if 'Worker' not in request.user.roles or 'Customer' not in request.user.roles:
            return Response({"detail": "Резюме может создать только человек с ролью Worker."}, status=status.HTTP_403_FORBIDDEN)
        return super().create(request, *args, **kwargs)
    
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        user = self.request.user
        if 'Admin' in user.roles:
            return Order.objects.all()
        else:
            return Order.objects.filter(owner=user)
        
    def create(self, request, *args, **kwargs):
        if 'Customer' not in request.user.roles:
            return Response({"detail": "Заказ может создать только человек с ролью Customer."}, status=status.HTTP_403_FORBIDDEN)
        return super().create(request, *args, **kwargs)
        
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class ProposalViewSet(viewsets.ModelViewSet):
    queryset = Proposal.objects.all()
    serializer_class = ProposalSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        user = self.request.user
        if 'Admin' in user.roles:
            return Proposal.objects.all()
        else:
            return Proposal.objects.filter(owner=user)

    def create(self, request, *args, **kwargs):
        if 'Worker' not in request.user.roles:
            return Response({"detail": "Отклик может создать только человек с ролью Worker."}, status=status.HTTP_403_FORBIDDEN)

        order_id = request.data.get('order')
        user = request.user
        
        if Proposal.objects.filter(owner=user, order_id=order_id).exists():
            return Response({"detail": "Вы уже оставили отклик на этот заказ."}, status=status.HTTP_400_BAD_REQUEST)
        
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class ProposalUpdateStatusView(generics.UpdateAPIView):
    queryset = Proposal.objects.all()
    serializer_class = ProposalSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        if instance:
            instance.status = request.data.get('status', instance.status)
            instance.save()
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        else:
            return Response({"detail": "No Proposal matches the given query."}, status=status.HTTP_404_NOT_FOUND)
        

class JobViewSet(viewsets.ModelViewSet):
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        user = self.request.user
        if 'Admin' in user.roles:
            return Job.objects.all()
        else:
            return Job.objects.filter(Q(proposal__owner=user) | Q(order__owner=user))


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated, IsAdmin]


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        user = self.request.user
        if 'Admin' in user.roles:
            return Review.objects.all()
        else:
            return Review.objects.filter(Q(owner=user) | Q(whom=user))

    def create(self, request, *args, **kwargs):
        user = request.user
        job = request.data.get('job')

        if Review.objects.filter(owner=user, job=job).exists():
            return Response({"detail": "You have already left a review for this job."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class AppealViewSet(viewsets.ModelViewSet):
    queryset = Appeal.objects.all()
    serializer_class = AppealSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        user = self.request.user
        if 'Admin' in user.roles:
            return Appeal.objects.all()
        else:
            return Appeal.objects.filter(job__proposal__owner=user)
        
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)