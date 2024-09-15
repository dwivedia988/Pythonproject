from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Item
from .serializers import ItemSerializer
from rest_framework import serializers
from rest_framework import status
from django.shortcuts import get_object_or_404
import stripe
from django.conf import settings

@api_view(['GET'])
def ApiOverview(request):
	api_urls = {
		'all_items': '/',
		'Search by Category': '/?category=category_name',
		'Search by Subcategory': '/?subcategory=category_name',
		'Add': '/create',
		'Update': '/update/pk',
		'Delete': '/item/pk/delete'
	}

	return Response(api_urls)

@api_view(['POST'])
def add_items(request):
	item = ItemSerializer(data=request.data)

	# validating for already existing data
	if Item.objects.filter(**request.data).exists():
		raise serializers.ValidationError('This data already exists')

	if item.is_valid():
		item.save()
		return Response(item.data)
	else:
		return Response(status=status.HTTP_404_NOT_FOUND)
	
@api_view(['GET'])
def view_items(request):
	
	# checking for the parameters from the URL
	if request.query_params:
		items = Item.objects.filter(**request.query_params.dict())
	else:
		items = Item.objects.all()

	# if there is something in items else raise error
	if items:
		serializer = ItemSerializer(items, many=True)
		return Response(serializer.data)
	else:
		return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def update_items(request, pk):
	item = Item.objects.get(pk=pk)
	data = ItemSerializer(instance=item, data=request.data)

	if data.is_valid():
		data.save()
		return Response(data.data)
	else:
		return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(['DELETE'])
def delete_items(request, pk):
	item = get_object_or_404(Item, pk=pk)
	item.delete()
	return Response(status=status.HTTP_202_ACCEPTED)





# Set up Stripe with your secret key
stripe.api_key = settings.STRIPE_TEST_KEY

@api_view(['POST'])
def create_checkout_session(request):
    try:
        title = request.data.get('title')
        description = request.data.get('description')
        bidprice = request.data.get('bidprice')
        user_email = request.data.get('user_email')

        # Create a new product
        product = stripe.Product.create(
            name=title,
            description=description
        )

        # Create a new price for the product
        price = stripe.Price.create(
            product=product.id,
            unit_amount=int(float(bidprice) * 100),  # Convert to cents
            currency='inr'
        )

        # Create a new Checkout Session
        session = stripe.checkout.Session.create(
            line_items=[
                {
                    'price': price.id,
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url='http://localhost:3000/success',
            cancel_url='http://localhost:3001/cancel',
            customer_email=user_email,
        )

        return Response({'url': session.url, 'success_url': session.success_url})

    except Exception as e:
        print(f"Error creating payment session: {e}")
        return Response({'error': 'Internal Server Error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
