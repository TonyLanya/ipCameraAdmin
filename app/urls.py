from django.conf.urls import url
from app import views, camera, user, properties, agents, auth
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Matches any html file - to be used for gentella
    # Avoid using your .html in your resources.
    # Or create a separate django app.
    # url(r'^.*\.html', views.gentella_html, name='gentella'),
    url(r'^index.html', views.gentella_html, name='gentella'),
    url(r'^ipcameras', views.ipcamera_html),
    url(r'^users', views.users_html),
    url(r'^properties', views.properties_html),
    url(r'^agents', views.agents_html),
    url(r'^login', auth_views.login),
    #url(r'^authenticate', auth.login, {'template_name' : ''}),
    # url(r'^logout', auth.logout),
    url(r'^logout', auth_views.logout, {'next_page': '/'}, name='logout'),

    # The home page
    url(r'^$', views.ipcamera_html, name='index'),

    url(r'video_feed', camera.video_feed, name='video_feed'),
    url(r'^start-video', camera.start_video),
    url(r'^stop-record', camera.stop_record),

    url(r'^server-side', views.cameras_asJson, name='my_ajax_url'),
    url(r'^get_user_table', views.users_asJson, name='get_user_table'),
    url(r'^get_properties_table', views.properties_asJson, name='get_properties_table'),
    url(r'^get_agents_table', views.agents_asJson, name='get_agents_table'),
    url(r'^email-receiver', views.email_receiver),
    url(r'^get-notify', views.get_notify),
    url(r'^camera/create-new', camera.create_new),
    url(r'^user/create-new', user.create_new),
    url(r'^property/create-new', properties.create_new),
    url(r'^agent/create-new', agents.create_new),
    url(r'^get-camera', camera.get_camera),
    url(r'^remove-notis', views.remove_notis),
    url(r'^cam-authorize', camera.cam_authorize)
]