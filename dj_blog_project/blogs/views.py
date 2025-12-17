from urllib.parse import urlencode

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q
from django.shortcuts import redirect, get_object_or_404
from django.views.generic import ListView, DetailView, DeleteView, UpdateView, CreateView

from .forms import BlogPostForm
from .models import BlogPost, Tag


class OrderQueryMixin:
    """
    支持 ?order=new|old 切换排序，并生成模板用的 querystring：
    - qs_keep: 保留除 page 外全部参数（分页用）
    - qs_no_order: 保留除 page/order 外全部参数（切换排序用，切换后回到第 1 页）
    """
    default_order = "new"

    def _parse_order(self):
        order = (self.request.GET.get("order") or self.default_order).lower()
        if order in ("old", "asc", "oldest"):
            return "old", ("date_added", "id")
        return "new", ("-date_added", "-id")

    def _build_querystrings(self):
        keep = self.request.GET.copy()
        keep.pop("page", None)
        qs_keep = urlencode(keep, doseq=True)
        qs_keep = (qs_keep + "&") if qs_keep else ""

        no_order = self.request.GET.copy()
        no_order.pop("page", None)
        no_order.pop("order", None)
        qs_no_order = urlencode(no_order, doseq=True)
        qs_no_order = (qs_no_order + "&") if qs_no_order else ""

        return qs_keep, qs_no_order

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        q = (self.request.GET.get("q") or "").strip()
        order, _ = self._parse_order()
        qs_keep, qs_no_order = self._build_querystrings()
        ctx["q"] = q
        ctx["order"] = order
        ctx["qs_keep"] = qs_keep
        ctx["qs_no_order"] = qs_no_order
        return ctx


class HomeListView(OrderQueryMixin, ListView):
    model = BlogPost
    template_name = "blogs/home.html"
    context_object_name = "posts"
    paginate_by = 5

    def get_queryset(self):
        qs = BlogPost.objects.filter(is_published=True).select_related("owner").prefetch_related("tags")

        q = (self.request.GET.get("q") or "").strip()
        if q:
            qs = qs.filter(Q(title__icontains=q) | Q(text__icontains=q))

        _, order_by = self._parse_order()
        return qs.order_by(*order_by)


class TagPostListView(OrderQueryMixin, ListView):
    model = BlogPost
    template_name = "blogs/home.html"
    context_object_name = "posts"
    paginate_by = 5

    def get_queryset(self):
        self.tag = get_object_or_404(Tag, slug=self.kwargs["slug"])
        qs = (
            BlogPost.objects.filter(is_published=True, tags=self.tag)
            .select_related("owner")
            .prefetch_related("tags")
        )

        q = (self.request.GET.get("q") or "").strip()
        if q:
            qs = qs.filter(Q(title__icontains=q) | Q(text__icontains=q))

        _, order_by = self._parse_order()
        return qs.order_by(*order_by)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["tag"] = self.tag
        return ctx


class PostDetailView(DetailView):
    model = BlogPost
    template_name = "blogs/detail.html"
    context_object_name = "post"

    def get_queryset(self):
        # 防止未发布文章被别人猜 URL 直接访问：匿名只能看发布的；作者可看自己的草稿
        qs = BlogPost.objects.select_related("owner").prefetch_related("tags")
        user = self.request.user
        if user.is_authenticated:
            return qs.filter(Q(is_published=True) | Q(owner=user))
        return qs.filter(is_published=True)


class OwnerRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        obj = self.get_object()
        return self.request.user.is_authenticated and obj.owner_id == self.request.user.id


class PostCreateView(LoginRequiredMixin, CreateView):
    model = BlogPost
    form_class = BlogPostForm
    template_name = "blogs/post_form.html"

    def form_valid(self, form):
        self.object = form.save(owner=self.request.user)
        return redirect(self.object.get_absolute_url())


class PostUpdateView(LoginRequiredMixin, OwnerRequiredMixin, UpdateView):
    model = BlogPost
    form_class = BlogPostForm
    template_name = "blogs/post_form.html"

    def form_valid(self, form):
        self.object = form.save()  # owner 不变
        return redirect(self.object.get_absolute_url())


class PostDeleteView(LoginRequiredMixin, OwnerRequiredMixin, DeleteView):
    model = BlogPost
    template_name = "blogs/post_confirm_delete.html"

    def get_success_url(self):
        return "/"
