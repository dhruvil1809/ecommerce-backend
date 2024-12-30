import ast
import string
from shop.views.utils import *
from rest_framework import generics, filters
from django_filters.rest_framework import DjangoFilterBackend
from shop.views.utils import ProductFilter
from django.db.models import Avg, Min, Max
from rest_framework.pagination import PageNumberPagination
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db.models import Prefetch
from django.db.models import Q
from django.core.files import File



class TagAPIView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [CustomRenderer]

    def get(self, request):
        tags = Tag.objects.filter(deleted=False)

        paginator = PageNumberPagination()
        paginator.page_size = 20

        paginated_tags = paginator.paginate_queryset(tags, request)

        serializer = TagSerializer(paginated_tags, many=True)

        return paginator.get_paginated_response(
            {
                "tags_data": serializer.data,
                "current_page": paginator.page.number,
                "total_pages": paginator.page.paginator.num_pages,
                "page_size": paginator.page_size,
                "message": "Tags retrieved successfully.",
                "status_code": status.HTTP_200_OK,
            }
        )

    def post(self, request):
        serializer = TagSerializer(data=request.data)
        var_title = request.data.get('var_title')
        print(request.data)

        if Tag.objects.filter(var_title=var_title, deleted=False).exists():
            return Response(
                {
                    "errors": {
                        "error": "A tag with this var_title already exists.",
                        "status_code": status.HTTP_200_OK
                        }
                },
                status=status.HTTP_200_OK,
            )
        
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    **serializer.data,
                    "message": "Tag create successfully.",
                    "status_code": status.HTTP_200_OK,
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            {"errors": serializer.errors, "status_code": status.HTTP_400_BAD_REQUEST},
            status=status.HTTP_400_BAD_REQUEST,
        )
    
    def put(self, request, id):
        try:
            tag = Tag.objects.get(id=id, deleted=False)
        except Tag.DoesNotExist:
            return Response(
                {
                    "errors": {
                        "error": "Tag not found.",
                        "status_code": status.HTTP_200_OK
                        }
                },
                status=status.HTTP_200_OK,
            )

        serializer = TagSerializer(tag, data=request.data)
        var_title = request.data.get('var_title')

        if Tag.objects.filter(var_title=var_title, deleted=False).exclude(id=id).exists():
            return Response(
                {
                    "errors": {
                        "error": "Tag with this var_title already exists.",
                        "status_code": status.HTTP_200_OK
                        }
                },
                status=status.HTTP_200_OK,
            )
        
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    **serializer.data,
                    "message": "Tag updated successfully.",
                    "status_code": status.HTTP_200_OK,
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            {"errors": serializer.errors, "status_code": status.HTTP_400_BAD_REQUEST},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def delete(self, request, id):
        try:
            tag = Tag.objects.get(id=id, deleted=False)
        except Tag.DoesNotExist:
            return Response(
                {
                    "errors": {
                        "error": "Tag not found.",
                        "status_code": status.HTTP_200_OK
                        }
                },
                status=status.HTTP_200_OK,
            )

        tag.delete()

        return Response(
            {
                "message": "Tag deleted successfully.",
                "status_code": status.HTTP_200_OK,
            },
            status=status.HTTP_200_OK,
        )


class GetAllTagAPIView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [CustomRenderer]

    def get(self, request):
        tags = Tag.objects.filter(deleted=False)

        serializer = TagSerializer(tags, many=True)

        return Response(
            {
                "tags_data": serializer.data,
                "message": "Tags retrieved successfully.",
                "status_code": status.HTTP_200_OK,
            },
            status=status.HTTP_200_OK
        )


class AttributeAPIView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [CustomRenderer]

    def get(self, request):
        attributes = Attribute.objects.filter(deleted=False).prefetch_related(Prefetch('values',
            queryset=AttributeValue.objects.filter(deleted=False),to_attr='filtered_values'))

        paginator = PageNumberPagination()
        paginator.page_size = 20

        paginated_attributes = paginator.paginate_queryset(attributes, request)

        serializer = AttributeSerializer(paginated_attributes, many=True)

        return paginator.get_paginated_response(
            {
                "attributes_data": serializer.data,
                "current_page": paginator.page.number,
                "total_pages": paginator.page.paginator.num_pages,
                "page_size": paginator.page_size,
                "message": "attributes retrieved successfully.",
                "status_code": status.HTTP_200_OK,
            }
        )

    def post(self, request):
        serializer = AttributeSerializer(data=request.data)
        var_title = request.data.get('var_title')
        print(request.data)

        if Attribute.objects.filter(var_title=var_title, deleted=False).exists():
            return Response(
                {
                    "errors": {
                        "error": "A attribute with this var_title already exists.",
                        "status_code": status.HTTP_200_OK
                        }
                },
                status=status.HTTP_200_OK,
            )
        
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    **serializer.data,
                    "message": "Attribute create successfully.",
                    "status_code": status.HTTP_200_OK,
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            {"errors": serializer.errors, "status_code": status.HTTP_400_BAD_REQUEST},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def put(self, request, id):
        try:
            attribute = Attribute.objects.get(id=id, deleted=False)
        except Attribute.DoesNotExist:
            return Response(
                {
                    "errors": {
                        "error": "Attribute not found.",
                        "status_code": status.HTTP_200_OK
                        }
                },
                status=status.HTTP_200_OK,
            )

        serializer = AttributeSerializer(attribute, data=request.data)
        var_title = request.data.get('var_title')

        if Attribute.objects.filter(var_title=var_title, deleted=False).exclude(id=id).exists():
            return Response(
                {
                    "errors": {
                        "error": "Attribute with this var_title already exists.",
                        "status_code": status.HTTP_200_OK
                        }
                },
                status=status.HTTP_200_OK,
            )
        
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    **serializer.data,
                    "message": "Attribute updated successfully.",
                    "status_code": status.HTTP_200_OK,
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            {"errors": serializer.errors, "status_code": status.HTTP_400_BAD_REQUEST},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def delete(self, request, id):
        try:
            attribute = Attribute.objects.get(id=id, deleted=False)
        except Attribute.DoesNotExist:
            return Response(
                {
                    "errors": {
                        "error": "Attribute not found.",
                        "status_code": status.HTTP_200_OK
                        }
                },
                status=status.HTTP_200_OK,
            )

        attribute.delete()

        return Response(
            {
                "message": "Attribute deleted successfully.",
                "status_code": status.HTTP_200_OK,
            },
            status=status.HTTP_200_OK,
        )


class GetAllAttributeAPIView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [CustomRenderer]

    def get(self, request):
        attributes = Attribute.objects.filter(deleted=False).prefetch_related(Prefetch('values',
            queryset=AttributeValue.objects.filter(deleted=False),to_attr='filtered_values'))

        serializer = AttributeSerializer(attributes, many=True)

        return Response(
            {
                "attributes_data": serializer.data,
                "message": "Attributes retrieved successfully.",
                "status_code": status.HTTP_200_OK,
            },
            status=status.HTTP_200_OK
        )


class AttributeValueAPIView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [CustomRenderer]

    def get(self, request, attribute_id):
        try:
            attribute = Attribute.objects.get(id=attribute_id, deleted=False)
        except Attribute.DoesNotExist:
            return Response(
                {
                    "errors": {
                        "error": "Attribute not found.",
                        "status_code": status.HTTP_200_OK
                        }
                },
                status=status.HTTP_200_OK,
            )
        
        values = AttributeValue.objects.filter(attribute=attribute_id, deleted=False)
        
        paginator = PageNumberPagination()
        paginator.page_size = 20

        paginated_attribute_values = paginator.paginate_queryset(values, request)

        serializer = AttributeValueSerializer(paginated_attribute_values, many=True)

        return paginator.get_paginated_response(
            {
                "attribute_values_data": serializer.data,
                "current_page": paginator.page.number,
                "total_pages": paginator.page.paginator.num_pages,
                "page_size": paginator.page_size,
                "message": "Attribute values retrieved successfully.",
                "status_code": status.HTTP_200_OK,
            }
        )

    def post(self, request):
        serializer = AttributeValueSerializer(data=request.data)
        var_title = request.data.get('var_title')
        attribute = request.data.get('attribute')

        if AttributeValue.objects.filter(var_title=var_title, deleted=False).exists():
            return Response(
                {
                    "errors": {
                        "error": "Attribute value with this var_title already exists.",
                        "status_code": status.HTTP_200_OK
                        }
                },
                status=status.HTTP_200_OK,
            )
        
        if not Attribute.objects.filter(id=attribute, deleted=False).exists():
            return Response(
                {
                    "errors": {
                        "error": "Attribute not found.",
                        "status_code": status.HTTP_200_OK
                        }
                },
                status=status.HTTP_200_OK,
            )

        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    **serializer.data,
                    "message": "Attribute value create successfully.",
                    "status_code": status.HTTP_200_OK,
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            {"errors": serializer.errors, "status_code": status.HTTP_400_BAD_REQUEST},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def put(self, request, id):
        try:
            var_title = AttributeValue.objects.get(id=id, deleted=False)
        except AttributeValue.DoesNotExist:
            return Response(
                {
                    "errors": {
                        "error": "Attribute value not found.",
                        "status_code": status.HTTP_200_OK
                        }
                },
                status=status.HTTP_200_OK,
            )

        if AttributeValue.objects.filter(var_title=var_title, deleted=False).exclude(id=id).exists():
            return Response(
                {
                    "errors": {
                        "error": "Attribute value with this var_title already exists.",
                        "status_code": status.HTTP_200_OK
                        }
                },
                status=status.HTTP_200_OK,
            )

        serializer = UpdateAttributeValueSerializer(var_title, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    **serializer.data,
                    "message": "Attribute value updated successfully.",
                    "status_code": status.HTTP_200_OK,
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            {"errors": serializer.errors, "status_code": status.HTTP_400_BAD_REQUEST},
            status=status.HTTP_400_BAD_REQUEST,
        )
    
    def delete(self, request, id):
        try:
            var_title = AttributeValue.objects.get(id=id, deleted=False)
        except AttributeValue.DoesNotExist:
            return Response(
                {
                    "errors": {
                        "error": "Attribute value not found.",
                        "status_code": status.HTTP_200_OK
                        }
                },
                status=status.HTTP_200_OK,
            )

        var_title.delete()

        return Response(
            {
                "message": "Attribute value deleted successfully.",
                "status_code": status.HTTP_200_OK,
            },
            status=status.HTTP_200_OK,
        )



class ProductVariantFilterView(APIView):
    permission_classes = [IsAuthenticated]
    # renderer_classes = [CustomRenderer]

    def post(self, request, *args, **kwargs):
        payload = request.data
        product_id = payload.get("product_id")
        attributes = payload.get("attributes", {})

        product = Product.objects.get(id=product_id)
        

        # Filter variants based on attributes
        variants = Variant.objects.filter(product=product)
        for key, value in attributes.items():
            variants = variants.filter(
                variant_attributes__attribute__var_title__iexact=key,
                variant_attributes__value__id=value
            ).distinct()

        # Serialize the filtered variants
        serializer = VariantSerializer(variants, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)




class ProductAPIView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [CustomRenderer]

    def get(self, request):
        products = Product.objects.filter(deleted=False, status=True).prefetch_related('tags', 'variants')
        
        paginator = PageNumberPagination()
        paginator.page_size = 21

        paginated_products = paginator.paginate_queryset(products, request)

        serializer = GetProductSerializer(paginated_products, many=True, context={'request': request})

        return paginator.get_paginated_response(
            {
                "Products_data": serializer.data,
                "current_page": paginator.page.number,
                "total_pages": paginator.page.paginator.num_pages,
                "page_size": paginator.page_size,
                "message": "Products retrieved successfully.",
                "status_code": status.HTTP_200_OK,
            }
        )
    
    def post(self, request, *args, **kwargs):
            data = request.data.copy()
            print(data)

            # Validate related fields
            category_id = data.get("category")
            sub_category_id = data.get("sub_category")
            name = data.get("name")
            tags = data.get('tags', [])

            if Product.objects.filter(name=name, deleted=False).exists():
                return Response(
                    {
                        "errors": {
                            "error": "A Product with this name already exists.",
                            "status_code": status.HTTP_200_OK
                        }
                    },
                    status=status.HTTP_200_OK,
                )

            if not Category.objects.filter(id=category_id).exists():
                return Response(
                    {
                        "errors": {
                            "error": "Category does not exist.",
                            "status_code": status.HTTP_200_OK
                        }
                    },
                    status=status.HTTP_200_OK,
                )

            if not SubCategory.objects.filter(id=sub_category_id).exists():
                return Response(
                    {
                        "errors": {
                            "error": "SubCategory does not exist.",
                            "status_code": status.HTTP_200_OK
                        }
                    },
                    status=status.HTTP_200_OK,
                )
            
            # Ensure that all tags exist in the database
            tags = json.loads(tags)
            valid_tags = Tag.objects.filter(id__in=tags)
            if len(valid_tags) != len(tags):
                return Response(
                    {
                        "errors": {
                            "error": "Some of the tags do not exist.",
                            "status_code": status.HTTP_200_OK
                        }
                    },
                    status=status.HTTP_200_OK,
                )
            

            product_serializer = ProductSerializer(data=data, context={'request': request})
            if product_serializer.is_valid():
                product = product_serializer.save()

                product.tags.set(valid_tags)

                # Handle variants
                variants_count = len([key for key in data.keys() if key.startswith('variants[')])
                for i in range(variants_count):
                    product_code = data.get(f"variants[{i}][product_code]")
                    product_sku = data.get(f"variants[{i}][product_sku]")
                    quantity = int(data.get(f"variants[{i}][quantity]", 0))
                    regular_price = float(data.get(f"variants[{i}][regular_price]", 0))
                    sale_price = float(data.get(f"variants[{i}][sale_price]", 0))

                    # Parse product_details
                    product_details_raw = data.get(f"variants[{i}][product_details]", [None])
                    product_details = None
                    if isinstance(product_details_raw, str):
                        try:
                            product_details = json.loads(product_details_raw)
                        except json.JSONDecodeError:
                            return Response(
                                {
                                    "errors": {
                                        "error": f"Invalid JSON format for variants[{i}][product_details].",
                                        "status_code": status.HTTP_200_OK
                                    }
                                },
                                status=status.HTTP_200_OK,
                            )
                    
                    # Parse product_descriptions
                    product_descriptions_raw = data.get(f"variants[{i}][product_descriptions]", [None])
                    product_descriptions = None
                    if isinstance(product_descriptions_raw, str):
                        try:
                            product_descriptions = json.loads(product_descriptions_raw)
                        except json.JSONDecodeError:
                            return Response(
                                {
                                    "errors": {
                                        "error": f"Invalid JSON format for variants[{i}][product_descriptions].",
                                        "status_code": status.HTTP_200_OK
                                    }
                                },
                                status=status.HTTP_200_OK,
                            )
                

                    if product_code and product_sku and quantity > 0 and regular_price > 0 and sale_price >= 0 and product_details and product_descriptions:
                        variant_data = {
                            "product_code": product_code,
                            "product_sku": product_sku,
                            "quantity": quantity,
                            "regular_price": regular_price,
                            "sale_price": sale_price,
                            "product": product,
                            "product_details": product_details,
                            "product_descriptions": product_descriptions,
                        }

                        print(":::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
                        print(variant_data)

                        # Create variant
                        variant = Variant.objects.create(**variant_data)

                        # Handle attributes
                        attributes_count = len([key for key in data.keys() if key.startswith(f"variants[{i}][attributes]")])
                        print(attributes_count)

                        for j in range(attributes_count):
                            attribute_id = data.get(f"variants[{i}][attributes][{j}][id]")
                            value_id = data.get(f"variants[{i}][attributes][{j}][value][id]")

                            # Validate and convert attributes to integer values
                            if attribute_id and value_id:

                                print(":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
                                print(f"Attribute id: {attribute_id}, Value id: {value_id}")

                                attribute_id = int(attribute_id)
                                value_id = int(value_id)

                                try:
                                    attribute = Attribute.objects.get(id=attribute_id)
                                except Attribute.DoesNotExist:
                                    product.delete()
                                    return Response(
                                        {
                                            "errors": {
                                                "error": f"Attribute with id {attribute_id} does not exist.",
                                                "status_code": status.HTTP_200_OK,
                                            }
                                        },
                                        status=status.HTTP_200_OK,
                                    )

                                try:
                                    value = AttributeValue.objects.get(id=value_id, attribute=attribute)
                                except AttributeValue.DoesNotExist:
                                    product.delete()
                                    return Response(
                                        {
                                            "errors": {
                                                "error": f"Value with id {value_id} does not exist for attribute with id {attribute_id}.",
                                                "status_code": status.HTTP_200_OK,
                                            }
                                        },
                                        status=status.HTTP_200_OK,
                                    )
                                
                                print(":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
                                print(f"Attribute: {attribute.var_title}, Value: {value.var_title}")

                                VariantAttribute.objects.create(
                                    variant=variant,
                                    attribute=attribute,
                                    value=value
                                )


                        # Handle variant images
                        image_keys = [key for key in data.keys() if key.startswith(f"variants[{i}][variant_images][")]
                        print(image_keys)
                        for key in image_keys:
                            image = data.get(key)
                            if image:
                                VariantImage.objects.create(variant=variant, image=image)

                return Response(
                    {
                        **product_serializer.data,
                        "message": "Product created successfully.",
                        "status_code": status.HTTP_200_OK,
                    },
                    status=status.HTTP_200_OK,
                )
            return Response(
                {"errors": product_serializer.errors, "status_code": status.HTTP_400_BAD_REQUEST},
                status=status.HTTP_400_BAD_REQUEST,
            )
    
    def put(self, request, *args, slug):
        data = request.data.copy()
        print(data)

        try:
            product = Product.objects.get(slug=slug, deleted=False)
        except Product.DoesNotExist:
            return Response(
                {
                    "errors": {
                        "error": "Product does not exist.",
                        "status_code": status.HTTP_200_OK,
                    }
                },
                status=status.HTTP_200_OK,
            )

        category_id = data.get("category")
        sub_category_id = data.get("sub_category")
        name = data.get("name")
        tags = data.get("tags", [])
        has_variants = data.get("has_variants", False)

        if name and Product.objects.filter(name=name, deleted=False).exclude(slug=slug).exists():
            return Response(
                {
                    "errors": {
                        "error": "A Product with this name already exists.",
                        "status_code": status.HTTP_200_OK,
                    }
                },
                status=status.HTTP_200_OK,
            )

        if category_id and not Category.objects.filter(id=category_id).exists():
            return Response(
                {
                    "errors": {
                        "error": "Category does not exist.",
                        "status_code": status.HTTP_200_OK,
                    }
                },
                status=status.HTTP_200_OK,
            )

        if sub_category_id and not SubCategory.objects.filter(id=sub_category_id).exists():
            return Response(
                {
                    "errors": {
                        "error": "SubCategory does not exist.",
                        "status_code": status.HTTP_200_OK,
                    }
                },
                status=status.HTTP_200_OK,
            )

        if tags:
            tags = json.loads(tags)
            valid_tags = Tag.objects.filter(id__in=tags)
            if len(valid_tags) != len(tags):
                return Response(
                    {
                        "errors": {
                            "error": "Some of the tags do not exist.",
                            "status_code": status.HTTP_200_OK,
                        }
                    },
                    status=status.HTTP_200_OK,
                )

        serializer = ProductSerializer(product, data=data, partial=True, context={'request': request})
        if serializer.is_valid():
            updated_product = serializer.save()

            if tags:
                updated_product.tags.set(valid_tags)
            
            # Handle variants
            variants_count = len([key for key in data.keys() if key.startswith("variants[")])
            saved_variant_ids = []

            for i in range(variants_count):
                variant_id = data.get(f"variants[{i}][id]")

                if variant_id == "false":
                    variant = Variant(product=product) 
                elif variant_id and variant_id != "false": 
                    try:
                        variant = Variant.objects.get(id=variant_id, product=product)
                    except Variant.DoesNotExist:
                        return Response(
                            {
                                "errors": {
                                    "error": f"Variant with id {variant_id} does not exist.",
                                    "status_code": status.HTTP_404_NOT_FOUND
                                }
                            },
                            status=status.HTTP_404_NOT_FOUND,
                        )
                else:  # Skip if variant_id is None
                    continue

                # Parse product_details
                product_details_raw = data.get(f"variants[{i}][product_details]", [None])
                if product_details_raw and isinstance(product_details_raw, str):
                    try:
                        product_details = json.loads(product_details_raw)
                    except json.JSONDecodeError:
                        return Response(
                            {
                                "errors": {
                                    "error": f"Invalid JSON format for variants[{i}][product_details].",
                                    "status_code": status.HTTP_200_OK
                                }
                            },
                            status=status.HTTP_200_OK,
                        )
                else:
                    product_details = variant.product_details
                
                # Parse product_descriptions
                product_descriptions_raw = data.get(f"variants[{i}][product_descriptions]", [None])
                if product_descriptions_raw and isinstance(product_descriptions_raw, str):
                    try:
                        product_descriptions = json.loads(product_descriptions_raw)
                    except json.JSONDecodeError:
                        return Response(
                            {
                                "errors": {
                                    "error": f"Invalid JSON format for variants[{i}][product_descriptions].",
                                    "status_code": status.HTTP_200_OK
                                }
                            },
                            status=status.HTTP_200_OK,
                        )
                else:
                    product_descriptions = variant.product_descriptions
                    
                variant_data = {
                    "product_code": data.get(f"variants[{i}][product_code]", variant.product_code),
                    "product_sku": data.get(f"variants[{i}][product_sku]", variant.product_sku),
                    "quantity": int(data.get(f"variants[{i}][quantity]", variant.quantity)),
                    "regular_price": float(data.get(f"variants[{i}][regular_price]", variant.regular_price)),
                    "sale_price": float(data.get(f"variants[{i}][sale_price]", variant.sale_price)),
                    "product_details": product_details,
                    "product_descriptions": product_descriptions,
                }
                for field, value in variant_data.items():
                    setattr(variant, field, value)
                variant.save()
                print("$$$$$$$$$$$$$$$$::::::::::::::::::::::::::::::::::::::::::",variant)
                saved_variant_ids.append(variant.id)

                # Handle variant attributes
                attributes_count = len([key for key in data.keys() if key.startswith(f"variants[{i}][attributes]")])
                if has_variants == "false":
                    VariantAttribute.objects.filter(variant=variant).delete()

                if attributes_count != 0:
                    VariantAttribute.objects.filter(variant=variant).delete()

                for j in range(attributes_count):
                    attribute_id = data.get(f"variants[{i}][attributes][{j}][id]")
                    value_id = data.get(f"variants[{i}][attributes][{j}][value][id]")

                    if attribute_id and value_id:
                            attribute_id = int(attribute_id)
                            value_id = int(value_id)

                            try:
                                attribute = Attribute.objects.get(id=attribute_id)
                            except Attribute.DoesNotExist:
                                return Response(
                                    {
                                        "errors": {
                                            "error": f"Attribute with id {attribute_id} does not exist.",
                                            "status_code": status.HTTP_200_OK,
                                        }
                                    },
                                    status=status.HTTP_200_OK,
                                )

                            try:
                                value = AttributeValue.objects.get(id=value_id, attribute=attribute)
                            except AttributeValue.DoesNotExist:
                                return Response(
                                    {
                                        "errors": {
                                            "error": f"Value with id {value_id} does not exist for attribute with id {attribute_id}.",
                                            "status_code": status.HTTP_200_OK,
                                        }
                                    },
                                    status=status.HTTP_200_OK,
                                )

                            variant_attribute, created = VariantAttribute.objects.update_or_create(
                                variant=variant,
                                attribute=attribute,
                                value=value,
                                defaults={
                                    'variant': variant,
                                    'attribute': attribute,
                                    'value': value
                                }
                            )
                

                # Handle variant images
                image_keys = [key for key in data.keys() if key.startswith(f"variants[{i}][variant_images][")]
                if image_keys:
                    existing_images = VariantImage.objects.filter(variant=variant)

                    image_ids = []
                    new_files = []

                    for key in image_keys:
                        image = data.get(key)
                        if isinstance(image, str):
                            try:
                                parsed_data = ast.literal_eval(image)
                                if 'id' in parsed_data:
                                    image_ids.append(parsed_data['id'])
                            except (SyntaxError, ValueError) as e:
                                print(f"Error parsing image data: {e}")
                        
                        elif isinstance(image, InMemoryUploadedFile):
                            new_files.append(image)

                    image_ids = [int(i) for i in image_ids]

                    existing_images.exclude(id__in=image_ids).delete()

                    for file in new_files:
                        VariantImage.objects.create(variant=variant, image=file)

            if has_variants == "false":
                print(":::::::::::::::::::::::::::::::::::::::::::::",saved_variant_ids)
                Variant.objects.filter(product=product).exclude(id__in=saved_variant_ids).delete()

            return Response(
                {
                    **serializer.data,
                    "message": "Product updated successfully.",
                    "status_code": status.HTTP_200_OK,
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {"errors": serializer.errors, "status_code": status.HTTP_400_BAD_REQUEST},
            status=status.HTTP_400_BAD_REQUEST,
        )
    
    def delete(self, request, slug):
        try:
            product = Product.objects.get(slug=slug, deleted=False)
        except Product.DoesNotExist:
            return Response(
                {
                    "errors": {
                        "error": "Product not found.",
                        "status_code": status.HTTP_200_OK
                    }
                },
                status=status.HTTP_200_OK,
            )

        # Soft delete
        product.deleted = True
        product.save()

        return Response(
            {
                "message": "Product deleted successfully.",
                "status_code": status.HTTP_200_OK,
            },
            status=status.HTTP_200_OK,
        )



class DeleteVariantApi(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [CustomRenderer]

    def delete(self, request, id):
        try:
            variant = Variant.objects.get(id=id)
        except Variant.DoesNotExist:
            return Response(
                {
                    "errors": {
                        "error": "Variant not found.",
                        "status_code": status.HTTP_200_OK
                    }
                },
                status=status.HTTP_200_OK,
            )

        variant.delete()

        return Response(
            {
                "message": "Variant deleted successfully.",
                "status_code": status.HTTP_200_OK,
            },
            status=status.HTTP_200_OK,
        )



class AllProductAPIView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [CustomRenderer]

    def get(self, request):
        products = Product.objects.filter(deleted=False, status=True)

        serializer = GetProductSerializer(products, many=True, context={'request': request})

        return Response(
            {
                "Products_data": serializer.data,
                "message": "Products retrieved successfully.",
                "status_code": status.HTTP_200_OK,
            },
            status=status.HTTP_200_OK
        )
    

class HomePageData(APIView):
    renderer_classes = [CustomRenderer]

    def get(self, request):

        categories = Category.objects.filter(add_to_home=True, deleted=False)
        categories_serializer = CategorySerializer(categories, many=True)

        # products = Product.objects.filter(top_collection=True, deleted=False).order_by('-created_at')[:8]
        # products_serializer = GetProductSerializer(products, many=True, context={'request': request})

        # best_sellers = Product.objects.filter(best_seller=True).order_by('-updated_at')
        # best_sellers_serializer = GetProductSerializer(best_sellers, many=True, context={'request': request})


        return Response(
                {
                    "categories": categories_serializer.data,
                    # "top_collection": products_serializer.data,
                    # "best_sellers": best_sellers_serializer.data,
                    "message": "Data retrieved successfully.",
                    "status_code": status.HTTP_200_OK,
                },
                status=status.HTTP_200_OK
            )
    

class ProductsByCategoryAPIView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [CustomRenderer]

    def get(self, request, category_slug):
        try:
            category = Category.objects.get(slug=category_slug, deleted=False, status=True)
            products = Product.objects.filter(category=category, deleted=False, status=True)
        
            paginator = PageNumberPagination()
            paginator.page_size = 21

            paginated_categories = paginator.paginate_queryset(products, request)

            serializer = GetProductSerializer(paginated_categories, many=True, context={'request': request})

            return paginator.get_paginated_response(
                {
                    "products": serializer.data,
                    "current_page": paginator.page.number,
                    "total_pages": paginator.page.paginator.num_pages,
                    "page_size": paginator.page_size,
                    "message": "Products retrieved successfully.",
                    "status_code": status.HTTP_200_OK,
                }
            )
    
        except Category.DoesNotExist:
            return Response(
                {
                    "errors": {
                        "error": "Category not found.",
                        "status_code": status.HTTP_200_OK
                    }
                },
                status=status.HTTP_200_OK,
            )
        

class ProductBySlugAPIView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [CustomRenderer]

    def get(self, request, product_slug):
        try:
            product = Product.objects.get(slug=product_slug, deleted=False, status=True)

            product_serializer = GetProductSerializer(product, context={'request': request})

            related_products = Product.objects.filter(
                sub_category=product.sub_category,
                deleted=False, 
                status=True
            ).exclude(id=product.id)[:4]

            related_products_serializer = GetProductSerializer(
                related_products, 
                many=True, 
                context={'request': request}
            )

            return Response(
                {
                    "product": product_serializer.data,
                    "related_products": related_products_serializer.data,
                    "message": "Product retrieved successfully.",
                    "status_code": status.HTTP_200_OK,
                },
                status=status.HTTP_200_OK,
            )
        except Product.DoesNotExist:
            return Response(
                {
                    "errors": {
                        "error": "Product not found.",
                        "status_code": status.HTTP_200_OK
                    }
                },
                status=status.HTTP_200_OK,
            )

        

class ProductLikeAPIView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [CustomRenderer]

    def get(self, request, *args, **kwargs):
        user = request.user

        liked_products = Product.objects.filter(liked_by=user, deleted=False, status=True)
    
        paginator = PageNumberPagination()
        paginator.page_size = 20

        paginated_categories = paginator.paginate_queryset(liked_products, request)

        serializer = GetProductSerializer(paginated_categories, many=True, context={'request': request})

        return paginator.get_paginated_response(
            {
                "product": serializer.data,
                "current_page": paginator.page.number,
                "total_pages": paginator.page.paginator.num_pages,
                "page_size": paginator.page_size,
                "message": "Product retrieved successfully.",
                "status_code": status.HTTP_200_OK,
            }
        )
        

    def post(self, request, product_slug):
        try:
            product = Product.objects.get(slug=product_slug, deleted=False, status=True)
            user = request.user

            if user in product.liked_by.all():
                product.liked_by.remove(user)  # Unlike the product
                liked = False
            else:
                product.liked_by.add(user)  # Like the product
                liked = True

            product.save()

            return Response(
                {
                    "message": "Product like status updated successfully.",
                    "liked": liked,
                    "status_code": status.HTTP_200_OK
                },
                status=status.HTTP_200_OK
            )
        except Product.DoesNotExist:
            return Response(
                {
                    "errors": {
                        "error": "Product not found.",
                        "status_code": status.HTTP_200_OK
                    }
                },
                status=status.HTTP_200_OK,
            )


# class ProductFilterView(generics.ListAPIView):
#     renderer_classes = [CustomRenderer]
#     queryset = Product.objects.filter(deleted=False, status=True)
#     serializer_class = GetProductSerializer
#     filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
#     filterset_class = ProductFilter

#     def get_queryset(self):
#         queryset = super().get_queryset()
#         top_rated = self.request.query_params.get('top_rated', None)
#         category_slug = self.request.query_params.get('category', None)

#         # Apply category-specific filtering if a category is specified
#         if category_slug:
#             queryset = queryset.filter(category__slug=category_slug)

#         if top_rated:
#             queryset = queryset.annotate(avg_rating=Avg('reviews__rating')).order_by('-avg_rating')

#         return queryset

    # def list(self, request, *args, **kwargs):
    #     queryset = self.filter_queryset(self.get_queryset())

    #     category_slug = self.request.query_params.get('category', None)

    #     # Paginator
    #     paginator = PageNumberPagination()
    #     paginator.page_size = 21
    #     paginated_queryset = paginator.paginate_queryset(queryset, request)

    #     # Aggregating filter options
    #     inventory_queryset = Inventory.objects.filter(product__deleted=False, product__status=True)
    #     if category_slug:
    #         inventory_queryset = inventory_queryset.filter(product__category__slug=category_slug)

    #     colors = inventory_queryset.values_list('color', flat=True).distinct()
    #     sizes = inventory_queryset.values_list('size', flat=True).distinct()
    #     genders = queryset.values_list('gender', flat=True).distinct()
    #     min_price = queryset.aggregate(Min('sale_price'))['sale_price__min']
    #     max_price = queryset.aggregate(Max('sale_price'))['sale_price__max']

    #     # Serialize paginated data
    #     serializer = self.get_serializer(paginated_queryset, many=True)

    #     # Add pagination and filter metadata
    #     response = paginator.get_paginated_response(serializer.data)
    #     response.data['pagination'] = {
    #         'current_page': paginator.page.number,
    #         'total_pages': paginator.page.paginator.num_pages,
    #     }
    #     response.data['filters'] = {
    #         'colors': list(colors),
    #         'sizes': list(sizes),
    #         'genders': list(genders),
    #         'min_price': min_price,
    #         'max_price': max_price,
    #     }

    #     return response






class ProductFilterView(generics.ListAPIView):
    renderer_classes = [CustomRenderer]
    queryset = Product.objects.filter(deleted=False, status=True)
    serializer_class = GetProductSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = ProductFilter

    def get_queryset(self):
        queryset = super().get_queryset()
        top_rated = self.request.query_params.get('top_rated', None)

        if top_rated:
            queryset = queryset.annotate(avg_rating=Avg('reviews__rating')).order_by('-avg_rating')

        return queryset
    
    def list(self, request, *args, **kwargs):
        # Filter and paginate the queryset
        queryset = self.filter_queryset(self.get_queryset())
        paginator = PageNumberPagination()
        paginator.page_size = 21
        paginated_queryset = paginator.paginate_queryset(queryset, request)

        # Fetch query parameters
        category_slug = self.request.query_params.get('category', None)

        # Aggregate variant data for filters
        variant_queryset = Variant.objects.filter(product__deleted=False, product__status=True)
        if category_slug:
            variant_queryset = variant_queryset.filter(product__category__slug=category_slug)

        # Aggregate gender, price range, and attributes with values
        genders = queryset.values_list('gender', flat=True).distinct()
        price_data = variant_queryset.aggregate(
            min_price=Min('sale_price'),
            max_price=Max('sale_price')
        )
        attributes_with_values = (
            Attribute.objects.filter(variant_attributes__variant__in=variant_queryset)
            .distinct()
            .prefetch_related('values')
        )
        attributes_data = [
            {
                "attribute": attr.var_title,
                "values": [{"id": val.id, "value": val.var_title} for val in attr.values.all()]
            }
            for attr in attributes_with_values
        ]

        # Serialize the paginated data
        serializer = self.get_serializer(paginated_queryset, many=True)

        # Construct the response
        response = paginator.get_paginated_response(serializer.data)
        response.data.update({
            'pagination': {
                'current_page': paginator.page.number,
                'total_pages': paginator.page.paginator.num_pages,
            },
            'filters': {
                'genders': list(genders),
                'min_price': price_data['min_price'],
                'max_price': price_data['max_price'],
                'attributes': attributes_data,
            },
        })

        return response


