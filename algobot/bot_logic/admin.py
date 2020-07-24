from django.contrib import admin
from .models import Sprint, Contest, Problem, Test, Hint, TestRestriction


class SprintAdmin(admin.ModelAdmin):
    list_display = ('title', 'number')
    search_fields = ('number',)


class ContestAdmin(admin.ModelAdmin):
    list_display = ('sprint_number', 'title', 'number')
    search_fields = ('number',)
    list_filter = ('sprint_number',)


class ProblemAdmin(admin.ModelAdmin):
    list_display = ('sprint_number', 'contest_number', 'title')
    search_fields = ('number',)
    list_filter = ('sprint_number', 'contest_number', 'title',)


class TestAdmin(admin.ModelAdmin):
    list_display = ('problem_title', 'number')
    search_fields = ('number',)
    # list_filter = ('problem_title', 'problem_title__sprint_number',
    #                'problem_title__contest_number')


class HintAdmin(admin.ModelAdmin):
    list_display = ('problem_title', 'text')
    search_fields = ('text',)
    # list_filter = ('problem_title', 'problem_title__sprint_number',
    #                'problem_title__contest_number')


# class TestRestrictionAdmin(admin.ModelAdmin):
#     list_display = '__all__'
#     search_fields = ('user',)


admin.site.register(Sprint, SprintAdmin)
admin.site.register(Contest, ContestAdmin)
admin.site.register(Problem, ProblemAdmin)
admin.site.register(Test, TestAdmin)
admin.site.register(Hint, HintAdmin)
# admin.site.register(TestRestriction, TestRestriction)
