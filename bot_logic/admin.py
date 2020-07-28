from django.contrib import admin

from .models import (Contest, Hint, Problem, Restriction, Sprint, Test, User,
                     UserTestPair)


class SprintAdmin(admin.ModelAdmin):
    list_display = ('sprint_number', 'sprint_title', 'faculty', )
    search_fields = ('number', 'title', )


class ContestAdmin(admin.ModelAdmin):
    list_display = ('contest_number', 'contest_title', 'sprint_number', )
    search_fields = ('contest_number', 'contest_title', )
    list_filter = ('sprint_number', )


class ProblemAdmin(admin.ModelAdmin):
    list_display = ('title', 'full_title', 'sprint_number',
                    'contest_number', 'test_limit', )
    search_fields = ('sprint_number', 'title',
                     'full_title', 'contest_number', )
    list_filter = ('sprint_number', 'contest_number', )


class TestAdmin(admin.ModelAdmin):
    list_display = ('number', 'problem')
    search_fields = ('problem', 'number')


class HintAdmin(admin.ModelAdmin):
    list_display = ('text', 'problem')
    search_fields = ('problem', 'text')
    list_filter = ('problem', )


class RestrictionAdmin(admin.ModelAdmin):
    list_display = ('user', 'problem', 'request_counter', )
    search_fields = ('user', 'problem', )


class UserTestPairAdmin(admin.ModelAdmin):
    list_display = ('user', 'test', )
    search_fields = ('user', 'test', )


class UserAdmin(admin.ModelAdmin):
    list_display = ('slack_id', 'first_name', 'last_name', 'cohort', )
    search_fields = ('first_name', 'last_name', 'slack_id', )


admin.site.register(Sprint, SprintAdmin)
admin.site.register(Contest, ContestAdmin)
admin.site.register(Problem, ProblemAdmin)
admin.site.register(Test, TestAdmin)
admin.site.register(Hint, HintAdmin)
admin.site.register(Restriction, RestrictionAdmin)
admin.site.register(UserTestPair, UserTestPairAdmin)
admin.site.register(User, UserAdmin)
