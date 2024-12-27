from fastapi import APIRouter

from .login import router as login_router
from .logout import router as logout_router
# from .posts import router as posts_router
# from .rate_limits import router as rate_limits_router
# from .tasks import router as tasks_router
# from .tiers import router as tiers_router
from .users import router as users_router
from .rooms import router as rooms_router
from .image import router as image_router
from .booking import router as booking_router
from .water_quality import router as water_quality_router

router = APIRouter(prefix="/v1")
# router.include_router(login_router)
# router.include_router(logout_router)
# router.include_router(users_router)
# router.include_router(rooms_router)
# router.include_router(image_router)
# router.include_router(booking_router)
# router.include_router(posts_router)
# router.include_router(tasks_router)
# router.include_router(tiers_router)
# router.include_router(rate_limits_router)
router.include_router(water_quality_router)