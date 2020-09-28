from django.contrib import admin
from tweets.models import Tweets, Comments

# Register your models here.

class TweetAdmin(admin.ModelAdmin):
    list_display = ['tweep','texts', 'date_posted',]
    search_fields = ['tweep__username', 'tweep__email']


class CommentAdmin(admin.ModelAdmin):
    list_display = ['commenter', 'comment', 'tweet', 'date_commented']
    list_display_links = ['tweet']
    search_fields = ['commenter__username', 'commenter__email']
admin.site.site_header = 'TwitIt Admin Dashboard'
admin.site.register(Tweets, TweetAdmin)
admin.site.register(Comments, CommentAdmin)