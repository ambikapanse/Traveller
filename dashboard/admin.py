from django.contrib import admin
from dashboard.models import *

admin.site.unregister(User)

admin.site.register(User)
admin.site.register(Post)
admin.site.register(Follow)
admin.site.register(Stream)
