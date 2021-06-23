from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework import serializers
from rest_framework.serializers import Serializer
from .models import Product, User
from .serializers import ProductSerializer, UserSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
import random
from .producer import publish

# Create your views here.

class ProductViewSet(viewsets.ViewSet):
    def list(self, request): # /api/products
        products = Product.objects.all()
        serializer = ProductSerializer(products, many = True)
        # publish()
        return Response(serializer.data)

    def create(self, request): # /api/products
        serializer = ProductSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        publish('product_created',serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None): # /api/products/<str:id>
        product = Product.objects.get(id=pk)
        serializer = ProductSerializer(product)
        return Response(serializer.data)

    def update(self, request, pk=None): # /api/products/<str:id>
        product = Product.objects.get(id=pk)
        serializer = ProductSerializer(instance=product, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        publish('product_updated',serializer.data)
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)


    def destroy(self, request, pk=None): # /api/products/<str:id>
        product = Product.objects.get(id=pk)
        product.delete()
        publish('product_deleted',pk)
        return Response(status=status.HTTP_204_NO_CONTENT)

# class UserAPIView(APIView):
#     def get(self, _):
#         users = User.objects.all()
#         user = random.choice(users)
#         return Response({
#             'id':user.id
#         })

#     def create_user(self, request): # /api/products
#         serializer = UserSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         publish('user_created',serializer.data)
#         return Response(serializer.data, status=status.HTTP_201_CREATED)

class UserAPIView(viewsets.ViewSet):
    def get_user(self, request):
        users = User.objects.all()
        user = random.choice(users)
        return Response({
            'id':user.id
        })

    def create_user(self, request): # /api/products
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        # publish('user_created',serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
