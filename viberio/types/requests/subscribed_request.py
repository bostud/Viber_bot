import attr

from viberio.utils.safe import ensure_cls
from viberio.types.user_profile import UserProfile
from .base import ViberReqestObject


@attr.s
class ViberSubscribedRequest(ViberReqestObject):
    user: UserProfile = attr.ib(converter=ensure_cls(UserProfile))
    api_version: str = attr.ib()
