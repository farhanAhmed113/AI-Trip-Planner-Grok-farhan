from django.shortcuts import render, get_object_or_404, redirect
from .models import Place, Hotel, SavedTrip
import folium
import razorpay
from django.conf import settings
from django.http import JsonResponse
import json
from .grok_ai import generate_trip_plan  # ✅ Correct import
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from rest_framework.decorators import api_view
import traceback
import time
from concurrent.futures import TimeoutError


def weather(request):
    """Weather page"""
    return render(request, 'hotels/weather.html')


# ✅ Razorpay client
razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


@login_required
def hotel_details(request, hotel_id):
    """Show hotel details and create Razorpay order"""
    hotel = get_object_or_404(Hotel, id=hotel_id)

    order_amount = int(hotel.price * 100)  # Convert price to paise
    order_currency = "INR"
    order = razorpay_client.order.create({
        "amount": order_amount,
        "currency": order_currency,
        "payment_capture": "1"
    })

    return render(request, 'hotels/hotel_details.html', {
        'hotel': hotel,
        'order_id': order['id'],
        'razorpay_key': settings.RAZORPAY_KEY_ID
    })


@csrf_exempt
@login_required
def payment_success(request, hotel_id):
    """Handle successful payment and update user travel history"""
    if request.method == 'POST':
        hotel = get_object_or_404(Hotel, id=hotel_id)
        user = request.user

        payment_id = request.POST.get('razorpay_payment_id', '')
        payment_status = 'completed'

        import datetime
        booking_details = {
            "hotel_id": hotel.id,
            "hotel_name": hotel.name,
            "place_id": hotel.place.id,
            "place_name": hotel.place.name,
            "image": hotel.image.url if hotel.image else "",
            "booking_date": datetime.datetime.now().strftime("%Y-%m-%d"),
            "price": str(hotel.price),
            "payment_id": payment_id,
            "payment_status": payment_status
        }

        # Update user travel history
        try:
            history_list = json.loads(user.profile.travel_history) if user.profile.travel_history else []
            if not isinstance(history_list, list):
                history_list = [history_list]
        except:
            history_list = []

        history_list.append(booking_details)
        user.profile.travel_history = json.dumps(history_list)
        user.profile.save()

        messages.success(request, f'Booking confirmed for {hotel.name}!')
        return redirect('profile')

    return redirect('home')


@api_view(['POST'])
def generate_ai_trip(request):
    """Generate trip itinerary using Grok AI"""
    if request.method == 'POST':
        try:
            data = request.data
            destination = data.get('destination')
            place_id = data.get('place_id')
            start_date = data.get('start_date')
            end_date = data.get('end_date')
            companions = data.get('companions')
            activities = data.get('activities')
            origin_location = data.get('origin_location', '')
            transportation_mode = data.get('transportation_mode', '')

            # Validate required fields
            if not all([destination, start_date, end_date, companions, activities]):
                return JsonResponse({'success': False, 'error': 'Missing required fields'})

            # Calculate duration
            from datetime import datetime
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.strptime(end_date, '%Y-%m-%d')
            duration = (end - start).days + 1

            formatted_activities = ', '.join(activities)
            companion_mapping = {
                'solo': 'solo traveler',
                'partner': 'couple',
                'friends': 'group of friends',
                'family': 'family with children'
            }
            formatted_companions = companion_mapping.get(companions, companions)

            # Generate trip using Grok AI
            try:
                start_time = time.time()

                trip_content = generate_trip_plan(
                    destination=destination,
                    duration=duration,
                    activities=formatted_activities,
                    companions=formatted_companions,
                    start_date=start_date,
                    origin_location=origin_location,
                    transportation_mode=transportation_mode
                )

                if not trip_content or len(trip_content) < 100:
                    raise Exception("Generated content is too short or empty")

                # Save trip if user is logged in
                if request.user.is_authenticated:
                    SavedTrip.objects.create(
                        user=request.user,
                        destination=destination,
                        place_id=place_id,
                        start_date=start,
                        end_date=end,
                        companions=companions,
                        activities=','.join(activities),
                        trip_html=trip_content,
                        origin_location=origin_location,
                        transportation_mode=transportation_mode
                    )

                return JsonResponse({
                    'success': True,
                    'content': trip_content,
                    'generation_time': round(time.time() - start_time, 2)
                })

            except TimeoutError:
                print("AI generation timeout")
                return JsonResponse({
                    'success': False,
                    'error': 'The AI service took too long to respond. Please try again.'
                })
            except Exception as ai_error:
                print(f"AI generation error: {str(ai_error)}")
                print(traceback.format_exc())
                return JsonResponse({
                    'success': False,
                    'error': f'Error generating trip content: {str(ai_error)}'
                })

        except Exception as e:
            print(f"Error generating AI trip: {str(e)}")
            print(traceback.format_exc())
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request method'})


def Trip(request):
    """Trip planner page"""
    return render(request, 'hotels/trip.html')


def home(request):
    """Home page — show all places"""
    places = Place.objects.all()
    return render(request, 'hotels/home.html', {'places': places})


def place_details(request, place_id):
    """Show details for a specific place"""
    place = get_object_or_404(Place, id=place_id)
    m = folium.Map(location=[place.latitude, place.longitude], zoom_start=12)
    folium.Marker(
        location=[place.latitude, place.longitude],
        popup=place.name,
        tooltip=place.name,
        icon=folium.Icon(color="red", icon="info-sign"),
    ).add_to(m)
    map_html = m._repr_html_()
    return render(request, 'hotels/place_details.html', {'place': place, 'map_html': map_html})


def hotels_near_place(request, place_id):
    """Show hotels near a place"""
    place = get_object_or_404(Place, id=place_id)
    hotels = place.hotels.all()

    m = folium.Map(location=[place.latitude, place.longitude], zoom_start=12)
    for hotel in hotels:
        folium.Marker(
            location=[hotel.latitude, hotel.longitude],
            popup=hotel.name,
            tooltip=hotel.name,
            icon=folium.Icon(color="blue"),
        ).add_to(m)

    map_html = m._repr_html_()
    return render(request, 'hotels/hotels_near_place.html', {'place': place, 'hotels': hotels, 'map_html': map_html})


def about(request):
    """About page"""
    return render(request, 'hotels/about.html')


def contact(request):
    """Contact page"""
    if request.method == 'POST':
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        subject = request.POST.get('subject', '')
        message = request.POST.get('message', '')
        messages.success(request, "Thank you for your message! We'll get back to you soon.")
        return redirect('contact')
    return render(request, 'hotels/contact.html')


def transportation_near_place(request, place_id):
    """Transportation map around a place"""
    place = get_object_or_404(Place, id=place_id)
    m = folium.Map(location=[place.latitude, place.longitude], zoom_start=13)

    folium.Marker(
        location=[place.latitude, place.longitude],
        popup=place.name,
        tooltip=place.name,
        icon=folium.Icon(color="red", icon="info-sign"),
    ).add_to(m)

    transportation_types = [
        {'name': 'Bus Stations', 'icon_color': 'blue', 'icon_name': 'bus'},
        {'name': 'Train Stations', 'icon_color': 'green', 'icon_name': 'train'},
        {'name': 'Taxi Stands', 'icon_color': 'orange', 'icon_name': 'taxi'},
        {'name': 'Metro Stations', 'icon_color': 'purple', 'icon_name': 'subway'}
    ]

    legend_html = '''
        <div style="position: fixed; bottom: 50px; left: 50px; z-index: 1000; background-color: white; 
                    padding: 10px; border: 2px solid grey; border-radius: 5px;">
        <h4>Transportation Options</h4>
        <div><i class="fa fa-map-marker" style="color: red"></i> Current Location</div>
    '''
    for t_type in transportation_types:
        legend_html += f'''
        <div><i class="fa fa-{t_type['icon_name']}" style="color: {t_type['icon_color']}"></i> {t_type['name']}</div>
        '''
    legend_html += '</div>'
    m.get_root().html.add_child(folium.Element(legend_html))

    map_html = m._repr_html_()
    return render(request, 'hotels/transportation_near_place.html', {
        'place': place,
        'map_html': map_html,
        'transportation_types': transportation_types
    })
