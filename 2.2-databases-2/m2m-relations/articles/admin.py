from django.contrib import admin
from django.core.exceptions import ValidationError
from django.forms import BaseInlineFormSet

from .models import Article, Tag, Scope


class ScopeInlineFormset(BaseInlineFormSet):
    def clean(self):
        super().clean()
        main_count = 0
        for form in self.forms:
            if form.cleaned_data and not form.cleaned_data.get("DELETE", False):
                if form.cleaned_data.get("is_main"):
                    main_count += 1
        if main_count == 0:
            raise ValidationError("У статьи должен быть один основной раздел!")
        elif main_count > 1:
            raise ValidationError(
                "У статьи не может быть больше одного основного раздела!"
            )


class ScopeInline(admin.TabularInline):
    model = Scope
    formset = ScopeInlineFormset
    extra = 1


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    inlines = [ScopeInline]


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ["name"]
