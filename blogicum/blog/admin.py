from django.contrib import admin

from .models import Category, Location, Post, Comment


class PostInline(admin.TabularInline):
    model = Post
    extra = 0


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 1
    fields = ('author', 'text', 'created_at')
    readonly_fields = ('created_at',)


class CategoryAdmin(admin.ModelAdmin):
    inlines = (
        PostInline,
    )


class LocationAdmin(admin.ModelAdmin):
    inlines = (
        PostInline,
    )


class PostAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'author',
        'category',
        'location',
        'is_published',
        'pub_date',
        'created_at'
    )
    list_editable = (
        'is_published',
        'category',
        'location'
    )
    search_fields = ('title',)
    list_filter = ('is_published',)
    list_display_links = ('title',)
    inlines = (CommentInline,)


admin.site.register(Category, CategoryAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Comment)
