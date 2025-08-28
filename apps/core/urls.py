from django.urls import path
from . import views

urlpatterns = [
    path("chat/", views.chat_view, name="chat"),
    path("stream-chat/", views.stream_chat_view, name="stream_chat"),  # SSE stream
    path("stream-test/", views.stream_test, name="stream_test")
]