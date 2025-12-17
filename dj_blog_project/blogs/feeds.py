from django.contrib.syndication.views import Feed
from django.urls import reverse

from .models import BlogPost


class LatestPostsFeed(Feed):
    title = "Blog - 最新文章"
    link = "/"
    description = "最新发布的博客文章"

    def items(self):
        return BlogPost.objects.filter(is_published=True).order_by("-date_added")[:20]

    def item_title(self, item: BlogPost):
        return item.title

    def item_description(self, item: BlogPost):
        return item.excerpt

    def item_link(self, item: BlogPost):
        return item.get_absolute_url()
