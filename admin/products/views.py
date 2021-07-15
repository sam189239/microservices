from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Product, User
from .producer import publish
from .serializers import ProductSerializer
import random

import os
from datetime import datetime
import time
import sys

from opencensus.trace.tracer import Tracer
from opencensus.trace import time_event as time_event_module
from opencensus.ext.zipkin.trace_exporter import ZipkinExporter
from opencensus.trace.samplers import AlwaysOnSampler

# 1a. Setup the exporter
ze = ZipkinExporter(service_name="test_api-tracing",
                                host_name='zipkins',
                                port=9411,
                                endpoint='/api/v2/spans')
# 1b. Set the tracer to use the exporter
# 2. Configure 100% sample rate, otherwise, few traces will be sampled.
# 3. Get the global singleton Tracer object
tracer = Tracer(exporter=ze, sampler=AlwaysOnSampler())



class ProductViewSet(viewsets.ViewSet):
    def list(self, request):
            with tracer.span(name="get_products") as span:
                    with tracer.span(name="get_products_chils") as span:
                        print("getting products")
                        products = Product.objects.all()
                        serializer = ProductSerializer(products, many=True)
                        return Response(serializer.data)

    def create(self, request):
            with tracer.span(name="create_product") as span:
                serializer = ProductSerializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                publish('product_created', serializer.data)
                return Response(serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        product = Product.objects.get(id=pk)
        serializer = ProductSerializer(product)
        return Response(serializer.data)

    def update(self, request, pk=None):
        product = Product.objects.get(id=pk)
        serializer = ProductSerializer(instance=product, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        publish('product_updated', serializer.data)
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)

    def destroy(self, request, pk=None):
        product = Product.objects.get(id=pk)
        product.delete()
        publish('product_deleted', pk)
        return Response(status=status.HTTP_204_NO_CONTENT)
        
    def destroy_all(self, request, pk=None):
            products = Product.objects.all().delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
            
                    


class UserAPIView(APIView):
    def get_user(self, request):
        users = User.objects.all()
        user = random.choice(users)
        return Response({
            'id':user.id
        })

    def create_user(self, request): 
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        # publish('user_created',serializer.data)
        print("New user Created")
        return Response(serializer.data, status=status.HTTP_201_CREATED)
