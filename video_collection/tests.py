from django.test import TestCase
from django.urls import reverse
from .models import Video
from django.db import IntegrityError
from django.core.exceptions import ValidationError

class TestHomePageMessage(TestCase):
    
    def test_app_title_message_shown_on_home_page(self):
        url = reverse('home')
        response = self.client.get(url)
        self.assertContains(response, 'Programming Tutorials')

class TestAddVideos(TestCase):
    
    def test_add_video(self):
        
        valid_video = {
            'name': 'JavaScript',
            'url': 'https://www.youtube.com/watch?v=SBmSRK3feww',
            'notes': 'complete javascript course'
        }
        
        url = reverse('add_video')
        response = self.client.post(url, data=valid_video, follow=True) # post the video and allow redirects with follow
        
        self.assertTemplateUsed('video_collection/video_list.html') # checking if the correct template is being used
        
        # does the video list show the new video?
        self.assertContains(response, 'JavaScript')
        self.assertContains(response, 'complete javascript course')
        self.assertContains(response, 'https://www.youtube.com/watch?v=SBmSRK3feww')
        
        video_count = Video.objects.count() # checking the database if it contains only one video that we just added
        self.assertEqual(1, video_count)
        
        video = Video.objects.first() # gets the only video added - django takes care of cleaning the database before and after running the test
        
        self.assertEqual('JavaScript', video.name)
        self.assertEqual('https://www.youtube.com/watch?v=SBmSRK3feww', video.url)
        self.assertEqual('complete javascript course', video.notes)
        self.assertEqual('SBmSRK3feww', video.video_id)
        
    def test_add_video_invalid_url_not_added(self):
        
        invalid_video_urls = [
            'https://www.youtube.com/watch',
            'https://www.youtube.com/watch?',
            'https://www.youtube.com/watch?abc=123',
            'https://www.youtube.com/watch?v=',
            'https://www.github.com',
            'https://www.minneapolis.edu',
            'https://www.minneapolis.edu?v=123456'
        ]
        
        for invalid_video_url in invalid_video_urls:
            
            new_video = {
                'name': 'example',
                'url': invalid_video_url,
                'notes': 'example notes'
            }
            
            url = reverse('add_video')
            response = self.client.post(url, new_video)
            
            self.assertTemplateNotUsed('video_collection/add.html') # add.html should not be using as add won't be successful
            
            messages = response.context['messages'] # gets the list of messages
            message_texts = [ message.message for message in messages ]
            
            self.assertIn('Invalid YouTube URL', message_texts) # checks each message
            self.assertIn('Please check the data entered.', message_texts)
            
            video_count = Video.objects.count() # there shouldnot be any video in the database as adding failed because of invalid url
            self.assertEqual(0, video_count)
        
        

class TestVideoList(TestCase):
    
    def test_all_videos_displayed_in_correct_order(self):
        
        v1 = Video.objects.create(name='ZXY', notes='example', url='https://www.youtube.com/watch?v=123')
        v2 = Video.objects.create(name='abc', notes='example', url='https://www.youtube.com/watch?v=124')
        v3 = Video.objects.create(name='AAA', notes='example', url='https://www.youtube.com/watch?v=125')
        v4 = Video.objects.create(name='lmn', notes='example', url='https://www.youtube.com/watch?v=126')
        
        expected_video_order = [ v3, v2, v4, v1]
        
        url = reverse('video_list')
        response = self.client.get(url)
        
        videos_in_template = list(response.context['videos']) # context refers to data sent from our program to html
        
        self.assertEqual(videos_in_template, expected_video_order)
        
    def test_no_video_message(self):
        # test to check no video message when there is no video in database
        url = reverse('video_list')
        response = self.client.get(url)
        self.assertContains(response, 'No videos')
        self.assertEqual(0, len(response.context['videos']))
        
    def test_video_number_message_one_video(self):
        v1 = Video.objects.create(name='ZXY', notes='example', url='https://www.youtube.com/watch?v=123')
        url = reverse('video_list')
        response = self.client.get(url)
        
        self.assertContains(response, '1 video')
        self.assertNotContains(response, '1 videos')
        
    def test_video_number_message_two_videos(self):
        v1 = Video.objects.create(name='ZXY', notes='example', url='https://www.youtube.com/watch?v=123')
        v2 = Video.objects.create(name='abc', notes='example', url='https://www.youtube.com/watch?v=124')
        url = reverse('video_list')
        response = self.client.get(url)
        
        self.assertContains(response, '2 videos')
        
        
        
class TestVideoSearch(TestCase):
    pass


class TestVideoModel(TestCase):
    
    def test_invalid_url_raises_validation_error(self):
        
        invalid_video_urls = [
            'https://www.youtube.com/watch',
            'https://www.youtube.com/watch/somethingelse',
            'https://www.youtube.com/watch/somethingelse?v=1234567',
            'https://www.youtube.com/watch?',
            'https://www.youtube.com/watch?abc=123',
            'https://www.youtube.com/watch?v=',
            'https://www.github.com',
            '123456564567543',
            'hhhhhhttps://www.youtube.com/watch',
            'http://www.youtube.com/watch',
            'https://www.minneapolis.edu',
            'https://www.minneapolis.edu?v=123456'
        ]
        
        for invalid_video_url in invalid_video_urls:
            with self.assertRaises(ValidationError): # for each invalid url, raises ValidationError
                Video.objects.create(name='example', url=invalid_video_url, notes='example note')
        
        self.assertEqual(0, Video.objects.count()) # none of the videos will be added to database as urls are invalid
    
    def test_duplicate_video_raises_integrity_error(self):
        
        v1 = Video.objects.create(name='ZXY', notes='example', url='https://www.youtube.com/watch?v=123')
        with self.assertRaises(IntegrityError):
            Video.objects.create(name='ZXY', notes='example', url='https://www.youtube.com/watch?v=123')
            
class TestVideoDetail(TestCase):
    
    def test_video_detail_shows_all_information(self):
        """ A test that verifies that the page shows all the information about one video, if that video exists """
        
        v1 = Video.objects.create(name='ZXY', notes='example', url='https://www.youtube.com/watch?v=123')
        
        response = self.client.get(reverse('video_detail', kwargs={'video_pk' : 1} ))
        self.assertTemplateUsed(response, 'video_collection/video_detail.html')
        
        self.assertContains(response, 'example')
        self.assertContains(response, 'ZXY')
        

    def test_status_404_for_video_detail_for_video_that_does_not_exist(self):
        
        """ A test that verifies a request for a page for a video that doesn't exist, returns a 404 status  """
        
        v1 = Video.objects.create(name='ZXY', notes='example', url='https://www.youtube.com/watch?v=123')
        response = self.client.get(reverse('video_detail', kwargs={'video_pk' : 100}))
        self.assertEqual(response.status_code, 404)
        
        
