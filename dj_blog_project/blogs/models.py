import math
import re

import bleach
import markdown as md
from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse
from django.utils.text import slugify

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(max_length=30, unique=True)
    slug = models.SlugField(max_length=40, unique=True)

    class Meta:
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name


class BlogPost(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="blog_posts")
    title = models.CharField(max_length=200)
    text = models.TextField()
    date_added = models.DateTimeField(auto_now_add=True)  # ✅ 你报错里显示的字段就是它
    updated_at = models.DateTimeField(auto_now=True)

    tags = models.ManyToManyField(Tag, blank=True, related_name="posts")
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ["-date_added"]

    def __str__(self) -> str:
        return self.title

    def get_absolute_url(self):
        return reverse("blogs:detail", kwargs={"pk": self.pk})

    @property
    def word_count(self) -> int:
        text = self.text or ""
        en = re.findall(r"[A-Za-z0-9']+", text)
        cjk = re.findall(r"[\u4e00-\u9fff]", text)
        return len(en) + len(cjk)

    @property
    def reading_time_minutes(self) -> int:
        text = self.text or ""
        en_words = len(re.findall(r"[A-Za-z0-9']+", text))
        cjk_chars = len(re.findall(r"[\u4e00-\u9fff]", text))
        minutes = (en_words / 200.0) + (cjk_chars / 400.0)
        return max(1, math.ceil(minutes))

    @property
    def excerpt(self) -> str:
        """RSS / 列表页摘要用：去掉 Markdown 符号，取前 180 字左右"""
        t = (self.text or "").strip()
        t = re.sub(r"`{1,3}.*?`{1,3}", "", t, flags=re.S)
        t = re.sub(r"[#>*_\\-]", " ", t)
        t = re.sub(r"\s+", " ", t).strip()
        return t[:180] + ("…" if len(t) > 180 else "")

    @property
    def html(self) -> str:
        """Markdown -> HTML（含 codehilite/Pygments）-> Bleach 安全清洗"""
        raw_html = md.markdown(
            self.text or "",
            extensions=[
                "fenced_code",
                "tables",
                "toc",
                "codehilite",  # ✅ Pygments 高亮
            ],
            extension_configs={
                "codehilite": {
                    "guess_lang": False,
                    "noclasses": False,  # ✅ 输出 class，配合 pygments css
                }
            },
        )

        allowed_tags = set(bleach.sanitizer.ALLOWED_TAGS) | {
            "p", "br",
            "h1", "h2", "h3", "h4", "h5",
            "pre", "code",
            "blockquote",
            "ul", "ol", "li",
            "strong", "em",
            "table", "thead", "tbody", "tr", "th", "td",
            "a",
            "div", "span",  # ✅ codehilite 会用到
        }

        allowed_attrs = dict(bleach.sanitizer.ALLOWED_ATTRIBUTES)
        allowed_attrs.update(
            {
                "*": ["class", "id"],
                "a": ["href", "title", "rel", "target"],
            }
        )

        cleaned = bleach.clean(
            raw_html,
            tags=allowed_tags,
            attributes=allowed_attrs,
            strip=True,
        )

        # 让链接默认 nofollow；并避免 linkify 污染代码块
        return bleach.linkify(
            cleaned,
            callbacks=[bleach.callbacks.nofollow],
            skip_tags=["pre", "code"],
        )
