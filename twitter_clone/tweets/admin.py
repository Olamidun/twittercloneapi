from django.contrib import admin
from tweets.models import Comments, CommentFile, Follow, Stream,  Tweets, TweetFile

# Register your models here.

class TweetAdmin(admin.ModelAdmin):
    list_display = ['tweep','texts', 'likes', 'date_posted',]
    search_fields = ['tweep__username', 'tweep__email']


class CommentAdmin(admin.ModelAdmin):
    list_display = ['commenter', 'comment', 'tweet', "comment_likes",'date_commented']
    list_display_links = ['tweet', 'comment']
    search_fields = ['commenter__username', 'commenter__email']
admin.site.site_header = 'TwitIt Admin Dashboard'
admin.site.register(Tweets, TweetAdmin)
admin.site.register(Comments, CommentAdmin)
admin.site.register(CommentFile)
admin.site.register(Follow)
admin.site.register(TweetFile)
admin.site.register(Stream)