from fastapi import APIRouter
from starlette import status

from app import schemas
from app.api import auth, user


router = APIRouter()

router.add_api_route(
    "/login",
    methods=["POST"],
    endpoint=auth.login,
    status_code=status.HTTP_200_OK,
    response_model=schemas.Token,
    tags=['Authentication'],
    responses={200: {'detail': 'Successfully logged in'},
               403: {'detail': 'Invalid credentials'}},
)

router.add_api_route(
    "/users",
    methods=["POST"],
    endpoint=user.create_user,
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.UserOut,
    tags=['CRUD Users'],
    responses={201: {'detail': 'User created'},
               409: {'detail': 'User already exists'},
               },
)

router.add_api_route(
    "/users/{idx}",
    methods=["GET"],
    endpoint=user.get_user,
    status_code=status.HTTP_200_OK,
    response_model=schemas.UserOut,
    tags=['CRUD Users'],
    responses={200: {'detail': 'Get user data'},
               404: {'detail': 'User does not exist'},
               },
)

router.add_api_route(
    "/users/{idx}",
    methods=["DELETE"],
    endpoint=user.delete_user,
    status_code=status.HTTP_204_NO_CONTENT,
    tags=['CRUD Users'],
    responses={204: {'detail': 'User deleted'},
               404: {'detail': 'User does not exist'},
               403: {'detail': 'Not authorized to perform requested action'},
               },
)

router.add_api_route(
    "/users/{idx}",
    methods=["PUT"],
    endpoint=user.update_user,
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.UserOut,
    tags=['CRUD Users'],
    responses={201: {'detail': 'User updated'},
               404: {'detail': 'User does not exist'},
               403: {'detail': 'Not authorized to perform requested action'},
               },
)

router.add_api_route(
    "/update-permission/{idx}",
    methods=["PATCH"],
    endpoint=user.update_user_permission,
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.UserPermission,
    tags=['Permissions'],
    responses={201: {'detail': 'Permission updated'},
               404: {'detail': 'User does not exist'},
               403: {'detail': 'Not authorized to perform requested action'},
               },
)

router.add_api_route(
    "/test-trade-access",
    methods=["GET"],
    endpoint=user.trade_access,
    status_code=status.HTTP_200_OK,
    tags=['Permissions'],
    responses={200: {'detail': 'User has trade access'},
               403: {'detail': 'Not authorized to perform requested action'},
               },
)

router.add_api_route(
    "/test-admin-access",
    methods=["GET"],
    endpoint=user.admin_access,
    status_code=status.HTTP_200_OK,
    tags=['Permissions'],
    responses={200: {'detail': 'User has admin access'},
               403: {'detail': 'Not authorized to perform requested action'},
               },
)


