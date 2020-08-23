from django.contrib import admin

from .models import (Contest, Faculty, Hint, Problem, ResponseTasks,
                     Restriction, Specialty, Sprint, Student, Test,
                     UserHintPair, UserTestPair)


class FacultyAdmin(admin.ModelAdmin):
    list_display = ('title', )
    search_fields = ('title', )


class SpecialtyAdmin(admin.ModelAdmin):
    list_display = ('title', 'faculty', )
    search_fields = ('title', )
    list_filter = ('faculty', )


class SprintAdmin(admin.ModelAdmin):
    list_display = ('number', 'title', 'specialty', )
    search_fields = ('number', 'title', )


class ContestAdmin(admin.ModelAdmin):
    list_display = ('number', 'title', 'test_limit', )
    search_fields = ('number', 'title', )
    list_filter = ('sprint', )


class ProblemAdmin(admin.ModelAdmin):
    list_display = ('title', 'full_title',
                    'contest', 'test_limit', )
    search_fields = ('title', 'full_title', )
    list_filter = ('contest__sprint', 'contest', )


class TestAdmin(admin.ModelAdmin):
    list_display = ('number', 'problem')
    search_fields = ('number', )
    list_filter = ('problem', )


class HintAdmin(admin.ModelAdmin):
    list_display = ('number', 'text', 'problem')
    search_fields = ('text', )
    list_filter = ('problem', )


class RestrictionAdmin(admin.ModelAdmin):
    list_display = ('user', 'problem', 'contest', 'request_counter', )
    search_fields = ('user__first_name', 'user__last_name',
                     'problem__full_title', 'contest__title', )


class UserTestPairAdmin(admin.ModelAdmin):
    list_display = ('user', 'test', 'timestamp')
    search_fields = ('user__first_name', 'user__last_name')
    list_filter = ('test', )


class UserHintPairAdmin(admin.ModelAdmin):
    list_display = ('user', 'hint', 'timestamp')
    search_fields = ('user__first_name', 'user__last_name')
    list_filter = ('hint', )


class StudentAdmin(admin.ModelAdmin):
    list_display = ('slack_id', 'first_name', 'last_name',
                    'specialty', 'cohort', )
    search_fields = ('first_name', 'last_name', 'slack_id', )
    list_filter = ('specialty', 'cohort', )


class ResponseTasksAdmin(admin.ModelAdmin):
    list_display = ('id', 'student', 'test', 'created')
    search_fields = ('student__first_name', 'student__last_name')


admin.site.register(Sprint, SprintAdmin)
admin.site.register(Contest, ContestAdmin)
admin.site.register(Problem, ProblemAdmin)
admin.site.register(Test, TestAdmin)
admin.site.register(Hint, HintAdmin)
admin.site.register(Restriction, RestrictionAdmin)
admin.site.register(UserTestPair, UserTestPairAdmin)
admin.site.register(Student, StudentAdmin)
admin.site.register(Faculty, FacultyAdmin)
admin.site.register(Specialty, SpecialtyAdmin)
admin.site.register(UserHintPair, UserHintPairAdmin)
admin.site.register(ResponseTasks, ResponseTasksAdmin)
