from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
#from .models import ReviewData
from .restapis import get_dealers_from_cf, get_dealer_by_id_from_cf, post_request, get_cars
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.


# Create an `about` view to render a static about page
def about(request):
    return render(request, 'djangoapp/about.html')

# Create a `contact` view to return a static contact page
def contact(request):
    return render(request, 'djangoapp/contact.html')

# Create a `login_request` view to handle sign in request
def login_request(request):
    context = {}
    # Handles POST request
    if request.method == "POST":
        # Get username and password from request.POST dictionary
        username = request.POST['username']
        password = request.POST['psw']
        # Try to check if provide credential can be authenticated
        user = authenticate(username=username, password=password)
        if user is not None:
            # If user is valid, call login method to login current user
            login(request, user)
            return redirect('djangoapp:index')
        else:
            context['message'] = "Invalid username or password."
            return render(request, 'djangoapp/login.html', context)
    else:
        return render(request, 'djangoapp/login.html', context)

# Create a `logout_request` view to handle sign out request
def logout_request(request):
    # Logout user in the request
    logout(request)
    # Redirect user back to course list view
    return redirect('djangoapp:index')

# Create a `registration_request` view to handle sign up request
def registration_request(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'djangoapp/registration.html', context)
    elif request.method == 'POST':
        # Check if user exists
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist = False
        try:
            User.objects.get(username=username)
            user_exist = True
        except:
            logger.error("New user")
        if not user_exist:
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,
                                            password=password)
            login(request, user)
            return redirect("djangoapp:index")
        else:
            context['message'] = "User already exists."
            return render(request, 'djangoapp/registration.html', context)


# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request):
    if request.method == "GET":
        url = "https://serrique-3000.theiadocker-2-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/dealerships/get"
        # Get dealers from the URL
        dealerships = get_dealers_from_cf(url)
        # Concat all dealer's short name
        dealer_names = ' '.join([dealer.short_name for dealer in dealerships])
        # Prepare context with dealer data
        context = {'dealerships': dealerships, 'dealer_names': dealer_names}
        # Return a list of dealer short name with request and context
        return render(request, 'djangoapp/index.html', context)


# Create a `get_dealer_details` view to render the reviews of a dealer
# def get_dealer_details(request, dealer_id):
# ...
def get_dealer_details(request, dealer_id):
    if request.method == "GET":
        url = "https://serrique-3001.theiadocker-2-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/reviews/get"
        # Get reviews from the URL
        reviews = get_dealer_by_id_from_cf(url, dealer_id)
        # Concat all reviews's id
        #dealer_id = ' '.join([review.id for review in reviews])
        # Prepare context with review data
        context = {'reviews': reviews, 'dealer_id': dealer_id}
        # Return a list of dealer short name with request and context
        return render(request, 'djangoapp/dealer_details.html', context)

# Create a `add_review` view to submit a review
# def add_review(request, dealer_id):
# ...


def add_review(request, dealer_id):
    if request.user.is_authenticated:
        if request.method == "GET":
            # Fetch cars based on dealer_id
            url = "https://serrique-3000.theiadocker-2-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/dealerships/get"
            cars = get_cars(dealer_id, url)  # Implement this function
            return render(request, "djangoapp/add_review.html", {"cars": cars, "dealer_id": dealer_id})

        elif request.method == "POST":
            #try:

                #"time": datetime.datetime.utcnow().isoformat(),
                id = ""
                name = request.POST.get("user")
                dealership = dealer_id
                review = request.POST.get("content")
                purchase = request.POST.get("purchasecheck") == "on"
                temp_date = request.POST.get("purchasedate")
                date_obj = datetime.strptime(temp_date, '%Y-%m-%d')
                purchase_date = date_obj.strftime('%m/%d/%Y')
                car_make = request.POST.get("car_maker")
                car_model = request.POST.get("car_name")
                car_year_str = request.POST.get("car_year")
                car_year = int(car_year_str)

                json_payload = {
                    "id": id,
                    "name": name,
                    "dealership": dealership,
                    "review": review,
                    "purchase": purchase,
                    "purchase_date": purchase_date,
                    "car_make": car_make,
                    "car_model": car_model,
                    "car_year": car_year,
                }

                
                url = "https://serrique-5000.theiadocker-2-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/api/post_review"
                response = post_request(url, json_payload)
                # Optionally handle the response here
                
                return redirect('djangoapp:dealer_details', dealer_id)  # Redirect to a success page
                
    else:
        return HttpResponse("User is not authenticated")

