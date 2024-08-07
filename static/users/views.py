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
from django_filters.rest_framework import DjangoFilterBackend
from .filters import CustomUserFilter, PassportFilter, OrderFilter, ProposalFilter, JobFilter, ReviewFilter, AppealFilter
from .status import *
from rest_framework.decorators import action

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
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = CustomUserFilter
    queryset = User.objects.all()  

    def list(self, request, *args, **kwargs):
        user = request.user
        if 'Admin' in user.roles:
            queryset = User.objects.select_related('bank_card', 'cv').prefetch_related('cv__reviews', 'cv__appeals').order_by('id')
        else:
            queryset = User.objects.select_related('bank_card', 'cv').prefetch_related('cv__reviews', 'cv__appeals').filter(id=user.id)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        user = request.user
        instance = self.get_object()
        if 'Admin' in user.roles or instance.id == user.id:
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        else:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        

class PassportViewSet(viewsets.ModelViewSet):
    serializer_class = PassportSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = PassportFilter

    def list(self, request, *args, **kwargs):
        user = request.user
        if 'Admin' in user.roles:
            queryset = Passport.objects.all()
        else:
            queryset = Passport.objects.filter(owner=user)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        user = request.user
        instance = self.get_object()
        if 'Admin' in user.roles or instance.owner == user:
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        else:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class BankCardViewSet(viewsets.ModelViewSet):
    serializer_class = BankCardSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def list(self, request, *args, **kwargs):
        user = request.user
        if 'Admin' in user.roles:
            queryset = BankCard.objects.all()
        else:
            queryset = BankCard.objects.filter(owner=user)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        user = request.user
        instance = self.get_object()
        if 'Admin' in user.roles or instance.owner == user:
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        else:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

    def create(self, request, *args, **kwargs):
        if 'Worker' not in request.user.roles:
            return Response({"detail": "Банк карту может создать только человек с ролью Worker."}, status=status.HTTP_403_FORBIDDEN)
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class CvViewSet(viewsets.ModelViewSet):
    serializer_class = CvSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    queryset = Cv.objects.all()  # Ensure this is defined for DRF schema generation

    def list(self, request, *args, **kwargs):
        user = request.user
        if 'Admin' in user.roles:
            queryset = Cv.objects.select_related('owner').prefetch_related('reviews', 'appeals')
        else:
            queryset = Cv.objects.select_related('owner').prefetch_related('reviews', 'appeals').filter(owner=user)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        user = request.user
        instance = self.get_object()
        if 'Admin' in user.roles or instance.owner == user:
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        else:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

    def create(self, request, *args, **kwargs):
        user = request.user
        if Cv.objects.filter(owner=user).exists():
            return Response({"detail": "У пользователя уже существует CV."}, status=status.HTTP_400_BAD_REQUEST)
        if 'Worker' not in user.roles and 'Customer' not in user.roles:
            return Response({"detail": "Резюме может создать только человек с ролью Worker или Customer."}, status=status.HTTP_403_FORBIDDEN)
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = OrderFilter

    def get_queryset(self):
        user = self.request.user
        if 'Admin' in user.roles:
            queryset = Order.objects.all().select_related('owner', 'category').prefetch_related('proposals')
        else:
            queryset = Order.objects.filter(owner=user).select_related('owner', 'category').prefetch_related('proposals')
        return queryset

    def create(self, request, *args, **kwargs):
        if 'Customer' not in request.user.roles:
            return Response({"detail": "Заказать может только человек с ролью Customer."}, status=status.HTTP_403_FORBIDDEN)

        if not Cv.objects.filter(owner=request.user).exists():
            return Response({"detail": "Для создания заказа у пользователя должен быть создан CV."}, status=status.HTTP_400_BAD_REQUEST)

        return super().create(request, *args, **kwargs)
    
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class ProposalViewSet(viewsets.ModelViewSet):
    serializer_class = ProposalSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = ProposalFilter

    def list(self, request, *args, **kwargs):
        user = request.user
        if 'Admin' in user.roles:
            queryset = Proposal.objects.select_related('order').all()
        else:
            queryset = Proposal.objects.select_related('order').filter(owner=user)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        user = request.user
        instance = self.get_object()
        if 'Admin' in user.roles or instance.owner == user:
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        else:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

    def create(self, request, *args, **kwargs):
        if 'Worker' not in request.user.roles:
            return Response({"detail": "Откликнуться может только человек с ролью Worker."}, status=status.HTTP_403_FORBIDDEN)

        if not Cv.objects.filter(owner=request.user).exists():
            return Response({"detail": "Для создания отклика у пользователя должен быть создан CV."}, status=status.HTTP_400_BAD_REQUEST)

        order = request.data.get('order')
        if Proposal.objects.filter(owner=request.user, order=order).exists():
            return Response({"detail": "Вы уже подали предложение на этот заказ."}, status=status.HTTP_400_BAD_REQUEST)

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
    serializer_class = JobSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = JobFilter
    queryset = Job.objects.all()  # Ensure this is defined for DRF schema generation

    def list(self, request, *args, **kwargs):
        user = request.user
        if 'Admin' in user.roles:
            queryset = Job.objects.all().select_related('order', 'proposal', 'assignee').prefetch_related('appeals')
        else:
            queryset = Job.objects.filter(
                Q(proposal__owner=user) | Q(order__owner=user)
            ).select_related('order', 'proposal', 'assignee').prefetch_related('appeals')
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        user = request.user
        instance = self.get_object()
        if 'Admin' in user.roles or instance.proposal.owner == user or instance.order.owner == user:
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        else:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

    def perform_create(self, serializer):
        serializer.save(assignee=self.request.user)

    @action(detail=True, methods=['post'], url_path='confirm-payment-customer')
    def confirm_payment_customer(self, request, *args, **kwargs):
        job = self.get_object()
        if request.user != job.order.owner:
            return Response({"detail": "Only the customer can confirm payment."}, status=status.HTTP_403_FORBIDDEN)
        
        job.payment_confirmed_by_customer = PaymentStatusChoices.APPROVED
        job.save()
        
        serializer = self.get_serializer(job)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='confirm-payment-worker')
    def confirm_payment_worker(self, request, *args, **kwargs):
        job = self.get_object()
        if request.user != job.assignee:
            return Response({"detail": "Only the worker can confirm payment."}, status=status.HTTP_403_FORBIDDEN)
        
        job.payment_confirmed_by_worker = PaymentStatusChoices.APPROVED
        job.save()
        
        serializer = self.get_serializer(job)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], url_path='appeal')
    def appeal(self, request, *args, **kwargs):
        job = self.get_object()
        user = request.user

        # Извлекаем данные из массива 'appeals'
        appeal_data = request.data.get('appeals', [{}])[0]  # Предполагается, что массив не пустой и содержит хотя бы один объект
        appeal_type = appeal_data.get('to')
        problem = appeal_data.get('problem', '')

        # Validate appeal type
        if appeal_type not in AppealTypeChoices.values:
            return Response({"detail": "Invalid appeal type."}, status=status.HTTP_400_BAD_REQUEST)

        if appeal_type == AppealTypeChoices.PAYMENT and job.status != JobStatusChoices.WARNING:
            return Response({"detail": "Can only report payment problems during PAYMENT status."}, status=status.HTTP_400_BAD_REQUEST)

        # Create the appeal data
        appeal_data = {
            'job': job.id,
            'owner': user.id,
            'whom': job.proposal.owner.id if user == job.order.owner else job.order.owner.id,
            'problem': problem,
            'to': appeal_type
        }

        # Create the appeal
        serializer = AppealSerializer(data=appeal_data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'], url_path='work-done')
    def work_done(self, request, *args, **kwargs):
        job = self.get_object()
        
        # if request.user != job.order.owner and request.user != job.assignee:
        #     return Response({"detail": "Only the customer or worker can change the status."}, status=status.HTTP_403_FORBIDDEN)
        
        # if job.status == JobStatusChoices.PAYMENT:
        #     return Response({"detail": "Job is already in PAYMENT status."}, status=status.HTTP_400_BAD_REQUEST)

        job.status = JobStatusChoices.PAYMENT
        job.save()

        serializer = self.get_serializer(job)
        return Response(serializer.data)
    
    


class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated, IsAdmin]


class AppealViewSet(viewsets.ModelViewSet):
    serializer_class = AppealSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = AppealFilter
    queryset = Appeal.objects.all()  # Add this line

    def list(self, request, *args, **kwargs):
        user = request.user
        if 'Admin' in user.roles:
            queryset = Appeal.objects.all()
        else:
            queryset = Appeal.objects.filter(owner=user)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        user = request.user
        instance = self.get_object()
        if 'Admin' in user.roles or instance.owner == user:
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        else:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = ReviewFilter
    queryset = Review.objects.all()  # Add this line

    def list(self, request, *args, **kwargs):
        user = request.user
        if 'Admin' in user.roles:
            queryset = Review.objects.all()
        else:
            queryset = Review.objects.filter(owner=user)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        user = request.user
        instance = self.get_object()
        if 'Admin' in user.roles or instance.owner == user:
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        else:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)