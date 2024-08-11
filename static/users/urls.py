from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import RegisterView, UserViewSet, PassportViewSet, BankCardViewSet, CvViewSet, CategoryViewSet, JobViewSet, OrderViewSet, ProposalViewSet, AppealViewSet, ReviewViewSet
from django.conf.urls.static import static
from django.conf import settings
from django.urls import path, include
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'passports', PassportViewSet, basename='passport')
router.register(r'bank-cards', BankCardViewSet, basename='bank-card')
router.register(r'cvs', CvViewSet, basename='cv')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'proposals', ProposalViewSet, basename='proposal')
router.register(r'jobs', JobViewSet, basename='job')
router.register(r'appeals', AppealViewSet, basename='appeal')
router.register(r'reviews', ReviewViewSet, basename='review')

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', RegisterView.as_view(), name='register'),

    path('', include(router.urls)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
