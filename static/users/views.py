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
from django.shortcuts import get_object_or_404

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
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def add_role(self, request, pk=None):
        user = self.get_object()

        if 'Worker' in user.roles and 'Customer' not in user.roles:
            user.roles.append('Customer')
        elif 'Customer' in user.roles and 'Worker' not in user.roles:
            user.roles.append('Worker')
        else:
            return Response({"detail": "У этого пользователя уже есть аккаунт с таким ролем"}, status=status.HTTP_400_BAD_REQUEST)

        user.save()
        return Response({"detail": "Role added successfully."}, status=status.HTTP_200_OK)
        

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
    queryset = Cv.objects.all()  

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

    @action(detail=True, methods=['post'], url_path='cancel')
    def deactivate_order(self, request, *args, **kwargs):
        order = self.get_object()
        if request.user == order.owner or 'Admin' in request.user.roles:
            if order.status == OrderStatusChoices.OPEN:
                order.status = OrderStatusChoices.CLOSED
                order.save()
                serializer = self.get_serializer(order)
                return Response(serializer.data)
            else:
                return Response({"detail": "Order is already closed or in an invalid state."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"detail": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)
    
    @action(detail=True, methods=['post'], url_path='restore')
    def activate_order(self, request, *args, **kwargs):
        order = self.get_object()
        if request.user == order.owner or 'Admin' in request.user.roles:
            if order.status == OrderStatusChoices.CLOSED:
                order.status = OrderStatusChoices.OPEN
                order.save()
                serializer = self.get_serializer(order)
                return Response(serializer.data)
            else:
                return Response({"detail": "Order is already open or in an invalid state."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"detail": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)


class ProposalViewSet(viewsets.ModelViewSet):
    serializer_class = ProposalSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = ProposalFilter

    def get_queryset(self):
        user = self.request.user
        if 'Admin' in user.roles:
            return Proposal.objects.select_related('order').all()
        return Proposal.objects.select_related('order').filter(owner=user)

    def list(self, request, *args, **kwargs):
        user = request.user
        queryset = self.get_queryset()
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
        return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

    def create(self, request, *args, **kwargs):
        user = request.user

        if not Cv.objects.filter(owner=user).exists():
            return Response({"detail": "Для создания отклика у пользователя должен быть создан CV."}, status=status.HTTP_400_BAD_REQUEST)

        if 'Worker' not in user.roles:
            return Response({"detail": "Откликнуться может только человек с ролью Worker."}, status=status.HTTP_403_FORBIDDEN)

        order_id = request.data.get('order')
        order = get_object_or_404(Order, id=order_id)

        if order.status != OrderStatusChoices.OPEN:
            return Response({"detail": "Можно подать предложение только на открытые заказы."}, status=status.HTTP_400_BAD_REQUEST)

        if Proposal.objects.filter(owner=user, order=order).exists():
            return Response({"detail": "Вы уже подали предложение на этот заказ."}, status=status.HTTP_400_BAD_REQUEST)

        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=['patch'], url_path='cancel')
    def cancel_proposal(self, request, *args, **kwargs):
        proposal = self.get_object()
        
        if proposal.status != ProposalStatusChoices.WAITING:
            return Response({"detail": "Only proposals with WAITING status can be canceled."}, status=status.HTTP_400_BAD_REQUEST)
        
        proposal.status = ProposalStatusChoices.CANCELED
        proposal.save()
        
        return Response({"detail": "Proposal status updated to CANCELED."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['patch'], url_path='restore')
    def restore_proposal(self, request, *args, **kwargs):
        proposal = self.get_object()
        
        if proposal.status != ProposalStatusChoices.CANCELED:
            return Response({"detail": "Only canceled proposals can be restored."}, status=status.HTTP_400_BAD_REQUEST)
        
        proposal.status = ProposalStatusChoices.WAITING
        proposal.save()
        
        return Response({"detail": "Proposal status updated to WAITING."}, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'], url_path='approve')
    def approve_proposal(self, request, *args, **kwargs):
        proposal = self.get_object()
        
        if proposal.status == ProposalStatusChoices.CANCELED or proposal.status == ProposalStatusChoices.REJECTED:
            return Response({"detail": "You can't approve CANCELED or REJECTED proposal"}, status=status.HTTP_400_BAD_REQUEST)
        
        proposal.status = ProposalStatusChoices.APPROVED
        proposal.save()
        
        return Response({"detail": "Proposal status updated to WAITING."}, status=status.HTTP_200_OK)
        

class JobViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = JobSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = JobFilter
    queryset = Job.objects.all() 

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

    @action(detail=True, methods=['post'], url_path='work-done')
    def work_done(self, request, *args, **kwargs):
        job = self.get_object()

        job.status = JobStatusChoices.PAYMENT
        job.save()

        serializer = self.get_serializer(job)
        return Response(serializer.data)

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
    
    @action(detail=True, methods=['post'], url_path='problem-payment-customer')
    def problem_payment_customer(self, request, *args, **kwargs):
        job = self.get_object()
        if request.user != job.order.owner:
            return Response({"detail": "Only the customer can confirm payment."}, status=status.HTTP_403_FORBIDDEN)
        
        job.payment_confirmed_by_customer = PaymentStatusChoices.PROBLEM
        job.save()
        
        serializer = self.get_serializer(job)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='problem-payment-worker')
    def problem_payment_worker(self, request, *args, **kwargs):
        job = self.get_object()
        if request.user != job.assignee:
            return Response({"detail": "Only the worker can confirm payment."}, status=status.HTTP_403_FORBIDDEN)
        
        job.payment_confirmed_by_worker = PaymentStatusChoices.PROBLEM
        job.save()
        
        serializer = self.get_serializer(job)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], url_path='appeal')
    def appeal(self, request, *args, **kwargs):
        job = self.get_object()
        user = request.user

        job_status_choice = JobStatusChoices
        appeal_status_choice = AppealTypeChoices

        appeal_data = request.data.get('appeals', [{}])[0]
        appeal_type = appeal_data.get('to')
        problem = appeal_data.get('problem', '')

        if job.status == job_status_choice.REVIEW:
            return Response({"detail": "Вы уже почти закончили работу, так как вы уже подтвердили что оплата закончена. Осталось только написать отзывы и окончить работу."}, status=status.HTTP_400_BAD_REQUEST)

        if job.status != job_status_choice.WARNING:
            job.status = job_status_choice.WARNING
            job.save()

        if appeal_type not in appeal_status_choice.values:
            return Response({"detail": "Invalid appeal type."}, status=status.HTTP_400_BAD_REQUEST)

        appeal_data = {
            'job': job.id,
            'owner': user.id,
            'whom': job.proposal.owner.id if user == job.order.owner else job.order.owner.id,
            'problem': problem,
            'to': appeal_type
        }

        serializer = AppealSerializer(data=appeal_data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'], url_path='review')
    def review(self, request, *args, **kwargs):
        job = self.get_object()
        user = request.user

        if job.status != JobStatusChoices.REVIEW:
            return Response({"detail": "Для создание отзыва, Job должен быть на статусе REVIEW."}, status=status.HTTP_400_BAD_REQUEST)

        if 'Customer' in user.roles:
            if job.review_written_by_customer:
                return Response({"detail": "Вы уже до этого писали отзыв."}, status=status.HTTP_400_BAD_REQUEST)
            job.review_written_by_customer = True
        elif 'Worker' in user.roles:
            if job.review_written_by_worker:
                return Response({"detail": "Вы уже до этого писали отзыв."}, status=status.HTTP_400_BAD_REQUEST)
            job.review_written_by_worker = True
        else:
            return Response({"detail": "Пользователь который пишет отзыв должен быть Работадателем или Работником"}, status=status.HTTP_403_FORBIDDEN)

        review_data = {
            'job': job.id,
            'whom': job.proposal.owner.id if 'Customer' in user.roles else job.order.owner.id,
            'rating': request.data.get('rating'),
            'comment': request.data.get('comment', '')
        }

        serializer = ReviewSerializer(data=review_data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            job.save()  
            return Response({"detail": "Review submitted successfully."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated, IsAdmin]
    queryset = Category.objects.all()  


class AppealViewSet(viewsets.ModelViewSet):
    serializer_class = AppealSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = AppealFilter
    queryset = Appeal.objects.all()  

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
    queryset = Review.objects.all()

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