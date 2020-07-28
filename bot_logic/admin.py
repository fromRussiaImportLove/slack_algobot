from django.contrib import admin
from .models import Problem, Test, Hint, Restriction


class ProblemAdmin(admin.ModelAdmin):
    list_display = ('title', 'sprint_number', 'contest_number')
    search_fields = ('sprint_number', 'title')
    list_filter = ('sprint_number', 'contest_number', 'title')


class TestAdmin(admin.ModelAdmin):
    list_display = ('number', 'problem')
    search_fields = ('problem', 'number')


class HintAdmin(admin.ModelAdmin):
    list_display = ('text', 'problem')
    search_fields = ('problem', 'text')


class RestrictionAdmin(admin.ModelAdmin):
    list_display = ('user', 'problem', 'counter')
    search_fields = ('user',)


admin.site.register(Problem, ProblemAdmin)
admin.site.register(Test, TestAdmin)
admin.site.register(Hint, HintAdmin)
admin.site.register(Restriction, RestrictionAdmin)
