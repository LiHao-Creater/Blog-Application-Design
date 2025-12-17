from django import forms
from django.utils.text import slugify

from .models import BlogPost, Tag


class BlogPostForm(forms.ModelForm):
    tags = forms.CharField(
        required=False,
        help_text="用逗号分隔，例如：Django, 安全, 生活",
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )

    class Meta:
        model = BlogPost
        fields = ["title", "text", "tags", "is_published"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "text": forms.Textarea(attrs={"class": "form-control", "rows": 12}),
            "is_published": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields["tags"].initial = ", ".join(t.name for t in self.instance.tags.all())

    def clean_tags(self):
        raw = self.cleaned_data.get("tags", "")
        names = [x.strip() for x in raw.split(",") if x.strip()]
        seen, out = set(), []
        for n in names:
            key = n.lower()
            if key not in seen:
                seen.add(key)
                out.append(n)
        return out

    def save(self, commit=True, owner=None):
        post = super().save(commit=False)
        if owner is not None and not post.pk:
            post.owner = owner

        if commit:
            post.save()

            post.tags.clear()
            for name in self.cleaned_data.get("tags", []):
                tag, _ = Tag.objects.get_or_create(
                    name=name,
                    defaults={"slug": slugify(name)},
                )
                post.tags.add(tag)

        return post
