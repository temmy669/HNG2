# from django.shortcuts import render
# from django.contrib.auth import authenticate
# from rest_framework import generics, status, viewsets
# from rest_framework.response import Response
# from rest_framework.permissions import IsAuthenticated
# from rest_framework_simplejwt.tokens import RefreshToken
# from .models import User, Organisation
# from .serializers import UserSerializer, OrganisationSerializer, LoginSerializer

# class RegisterView(generics.CreateAPIView):
#     queryset = User.objects.all()
#     serializer_class = UserSerializer

#     def post(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         if serializer.is_valid():
#             user = serializer.save()
#             refresh = RefreshToken.for_user(user)
#             return Response({
#                 "status": "success",
#                 "message": "Registration successful",
#                 "data": {
#                     "accessToken": str(refresh.access_token),
#                     "user": UserSerializer(user).data
#                 }
#             }, status=status.HTTP_201_CREATED)
#         return Response({
#             "status": "Bad request",
#             "message": "Registration unsuccessful",
#             "statusCode": 422,
#             "errors": serializer.errors
#         }, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

# class LoginView(generics.GenericAPIView):
#     serializer_class = LoginSerializer

#     def post(self, request, *args, **kwargs):
#         email = request.data.get('email')
#         password = request.data.get('password')
#         user = authenticate(email=email, password=password)
#         if user is not None:
#             refresh = RefreshToken.for_user(user)
#             return Response({
#                 "status": "success",
#                 "message": "Login successful",
#                 "data": {
#                     "accessToken": str(refresh.access_token),
#                     "user": UserSerializer(user).data
#                 }
#             }, status=status.HTTP_200_OK)
#         return Response({
#             "status": "Bad request",
#             "message": "Authentication failed",
#             "statusCode": 401
#         }, status=status.HTTP_401_UNAUTHORIZED)

# class UserDetailView(generics.RetrieveAPIView):
#     queryset = User.objects.all()
#     serializer_class = UserSerializer
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         user = self.request.user
#         return User.objects.filter(id=user.id)

# class OrganisationViewSet(viewsets.ModelViewSet):
#     serializer_class = OrganisationSerializer
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         user = self.request.user
#         return user.organisations.all()

#     def perform_create(self, serializer):
#         serializer.save(users=[self.request.user])

# class OrganisationDetailView(generics.RetrieveAPIView):
#     queryset = Organisation.objects.all()
#     serializer_class = OrganisationSerializer
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         user = self.request.user
#         return Organisation.objects.filter(users=user)

# class AddUserToOrganisationView(generics.GenericAPIView):
#     queryset = Organisation.objects.all()
#     serializer_class = OrganisationSerializer
#     permission_classes = [IsAuthenticated]

#     def post(self, request, orgId):
#         try:
#             organisation = Organisation.objects.get(id=orgId)
#         except Organisation.DoesNotExist:
#             return Response({
#                 "status": "Bad request",
#                 "message": "Organisation not found",
#                 "statusCode": 404
#             }, status=status.HTTP_404_NOT_FOUND)

#         userId = request.data.get('userId')
#         try:
#             user = User.objects.get(id=userId)
#         except User.DoesNotExist:
#             return Response({
#                 "status": "Bad request",
#                 "message": "User not found",
#                 "statusCode": 404
#             }, status=status.HTTP_404_NOT_FOUND)

#         organisation.users.add(user)
#         return Response({
#             "status": "success",
#             "message": "User added to organisation successfully"
#         }, status=status.HTTP_200_OK)



from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate
from rest_framework import generics, status, viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, Organisation
from .serializers import UserSerializer, OrganisationSerializer, LoginSerializer


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                "status": "success",
                "message": "Registration successful",
                "data": {
                    "accessToken": str(refresh.access_token),
                    "user": UserSerializer(user).data
                }
            }, status=status.HTTP_201_CREATED)
        return Response({
            "status": "Bad request",
            "message": "Registration unsuccessful",
            "statusCode": 422,
            "errors": serializer.errors
        }, status=status.HTTP_422_UNPROCESSABLE_ENTITY)


class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')
        user = authenticate(email=email, password=password)
        
        if user is not None:
            refresh = RefreshToken.for_user(user)
            
            # # Get organizations user belongs to
            # organisations = Organisation.objects.filter(users=user)
            # organisation_data = OrganisationSerializer(organisations, many=True).data
            
            return Response({
                "status": "success",
                "message": "Login successful",
                "data": {
                    "accessToken": str(refresh.access_token),
                    "user": UserSerializer(user).data,
                    # "organisations": organisation_data  # Include organisations data
                }
            }, status=status.HTTP_200_OK)
        
        return Response({
            "status": "Bad request",
            "message": "Authentication failed",
            "statusCode": 401
        }, status=status.HTTP_401_UNAUTHORIZED)


class UserDetailView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def get(self, request, *args, **kwargs):
        user = self.get_object()
        response_data = UserSerializer(user).data
        print("User Detail Response Data:", response_data)  # Debug print
        return Response({
            "status": "success",
            "message": "User details retrieved successfully",
            "data": response_data
        }, status=status.HTTP_200_OK)




class CreateOrganisationView(generics.CreateAPIView):
    serializer_class = OrganisationSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            organisation = serializer.save(users=[self.request.user])
            return Response({
                "status": "success",
                "message": "Organisation created successfully",
                "data": {
                    "orgId": organisation.orgId,
                    "name": organisation.name,
                    "description": organisation.description
                }
            }, status=status.HTTP_201_CREATED)
        return Response({
            "status": "Bad Request",
            "message": "Client error",
            "statusCode": 400,
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class OrganisationViewSet(viewsets.ModelViewSet):
    serializer_class = OrganisationSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'orgId'

    def get_queryset(self):
        if self.request.user.is_authenticated:
            user = self.request.user
            return user.organisations.all()
        return Organisation.objects.all()

    def perform_create(self, serializer):
        serializer.save(users=[self.request.user])

class OrganisationListCreateView(generics.ListCreateAPIView):
    serializer_class = OrganisationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # This will return organisations for the authenticated user
        return Organisation.objects.filter(users=self.request.user)

    def perform_create(self, serializer):
        # Save the new organisation with the current user as one of its members
        serializer.save(users=[self.request.user])

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "status": "success",
            "message": "Organisations retrieved successfully",
            "data": {
                "organisations": serializer.data
            }
        }, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            organisation = serializer.save(users=[self.request.user])
            return Response({
                "status": "success",
                "message": "Organisation created successfully",
                "data": {
                    "orgId": organisation.orgId,
                    "name": organisation.name,
                    "description": organisation.description
                }
            }, status=status.HTTP_201_CREATED)
        return Response({
            "status": "Bad Request",
            "message": "Client error",
            "statusCode": 400,
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)




class OrganisationDetailView(generics.RetrieveAPIView):
    queryset = Organisation.objects.all()
    serializer_class = OrganisationSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'orgId'

    def get_queryset(self):
        if self.request.user.is_authenticated:
            user = self.request.user
            return Organisation.objects.filter(users=user)
        return Organisation.objects.all()


class AddUserToOrganisationView(generics.GenericAPIView):
    queryset = Organisation.objects.all()
    serializer_class = OrganisationSerializer
    permission_classes = [AllowAny]

    def post(self, request, orgId):
        organisation = get_object_or_404(Organisation, orgId=orgId)
        userId = request.data.get('userId')
        
        if not userId:
            return Response({
                "status": "Bad request",
                "message": "userId not provided",
                "statusCode": 400
            }, status=status.HTTP_400_BAD_REQUEST)
        
        user = get_object_or_404(User, userId=userId)
        
        organisation.users.add(user)
        return Response({
            "status": "success",
            "message": "User added to organisation successfully"
        }, status=status.HTTP_200_OK)
class UserOrganisationsView(generics.ListAPIView):
    serializer_class = OrganisationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_authenticated:
            user = self.request.user
            return Organisation.objects.filter(users=user)
        return Organisation.objects.none()  # Or handle unauthenticated access as needed

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "status": "success",
            "message": "Organisations retrieved successfully",
            "data": {
                "organisations": serializer.data
            }
        }, status=status.HTTP_200_OK)
    
