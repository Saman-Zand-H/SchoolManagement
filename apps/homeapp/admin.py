from django.contrib import admin

from mainapp.models import Article


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'school', 'timestamp')
    list_filter = ('author', 'school')
    search_fields = ('title', 'author__username', 'school__name')
    ordering = ('-timestamp',)