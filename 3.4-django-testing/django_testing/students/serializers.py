from rest_framework import serializers
from django.conf import settings
from students.models import Course


class CourseSerializer(serializers.ModelSerializer):

    class Meta:
        model = Course
        fields = ("id", "name", "students")

    def validate_students(self, students):
        max_students = getattr(settings, "MAX_STUDENTS_PER_COURSE", 20)
        if len(students) > max_students:
            raise serializers.ValidationError(
                f"Максимум {max_students} студентов на курс."
            )
        return students
