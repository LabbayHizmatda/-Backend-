from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import RegisterView

from django.urls import path, include
from .views import UserViewSet, PassportViewSet, BankCardViewSet, CvViewSet, CategoryViewSet, JobViewSet, OrderViewSet, ProposalViewSet, ProposalUpdateStatusView, AppealViewSet, ReviewViewSet

from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'passports', PassportViewSet)
router.register(r'bank-cards', BankCardViewSet)
router.register(r'cvs', CvViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'orders', OrderViewSet)
router.register(r'proposals', ProposalViewSet)
router.register(r'jobs', JobViewSet)
router.register(r'appeals', AppealViewSet)
router.register(r'reviews', ReviewViewSet)

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', RegisterView.as_view(), name='register'),

    path('', include(router.urls)),
    path('proposals/<int:pk>/update_status/', ProposalUpdateStatusView.as_view(), name='proposal-update-status'),
]

