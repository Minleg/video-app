from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db.models.functions import Lower
from .forms import VideoForm, SearchForm
from .models import Video

def home(request):
    app_name = 'Programming Tutorials' # put your own category
    return render(request, 'video_collection/home.html', {'app_name': app_name})

def add(request):
    
    if request.method == 'POST':
        new_video_form = VideoForm(request.POST)
        if new_video_form.is_valid(): # checks if every required fields are filled
            try:
                new_video_form.save() # save to the database
                return redirect('video_list')
                # messages.info(request, 'New video saved!')
                # todo redirect to list of videos
            except ValidationError:
                messages.warning(request, 'Invalid YouTube URL')
            except IntegrityError:
                messages.warning(request, 'You already added that video')
        
        messages.warning(request, 'Please check the data entered.')
        return render(request, 'video_collection/add.html', {'new_video_form': new_video_form})
        
    new_video_form = VideoForm()
    return render(request, 'video_collection/add.html', {'new_video_form': new_video_form})

def video_list(request):
    
    search_form = SearchForm(request.GET) # build form from data user has sent to app
    
    if search_form.is_valid():
        search_term = search_form.cleaned_data['search_term'] # search any topic like python or java - should match form in forms.py
        videos = Video.objects.filter(name__icontains=search_term).order_by(Lower('name'))
        
    else: # form is not filled in or this is the first time the user sees the page
        search_form = SearchForm()
        videos = Video.objects.order_by(Lower('name')) # gets all videos from database
        
    #videos = Video.objects.all() # gets all videos from database
    return render(request, 'video_collection/video_list.html', {'videos': videos, 'search_form': search_form})

def video_detail(request, video_pk):
    video = get_object_or_404(Video, pk=video_pk)
    
    return render(request, 'video_collection/video_detail.html', {'video' : video})

def video_delete(request, video_pk):
    """ gets the video to delete, checks if the request is POST(i.e. deletion) and asks the user for reconfirmation of delete option, 
    If they decide, it is deleted and directed to video list page, otherwise it stays on the video detail page. If the request
    is not POST, shows the confirmation page"""
    video = get_object_or_404(Video, pk=video_pk)
    
    if request.method == 'POST':
        return redirect('video_confirmation', video.pk) # shows the confirmation page
    else: 
        return render(request, 'video_collection/video_delail.html', {'video': video}) # if request is not post, stays on the video detail page
    

def video_confirmation(request, video_pk):
    video = get_object_or_404(Video, pk=video_pk)
    if request.method == 'POST':
        if request.POST.get('confirm') == 'yes': # asking user confirmation to delete the video
            video.delete()
            # messages.success(request, 'Video deleted')
            return redirect('video_list')
        else:
            return redirect('video_detail', video_pk=video_pk)
        
    return render(request, 'video_collection/video_delete_confirmation.html', {'video': video})
    
