import pytest
from rest_framework.test import APIClient
from model_bakery import baker
from django.urls import reverse

from students.models import Course, Student

pytestmark = pytest.mark.django_db


# ФИКСТУРЫ


@pytest.fixture
def api_client():
    """Фикстура для DRF APIClient"""
    return APIClient()


@pytest.fixture
def course_factory():
    """Фикстура для создания курсов через model_bakery"""

    def factory(**kwargs):
        return baker.make(Course, **kwargs)

    return factory


@pytest.fixture
def student_factory():
    """Фикстура для создания студентов через model_bakery"""

    def factory(**kwargs):
        return baker.make(Student, **kwargs)

    return factory


# ОСНОВНЫЕ ТЕСТЫ


def test_retrieve_course(api_client, course_factory):
    """Проверка получения одного курса"""
    course = course_factory(name="Python 101")
    url = reverse("courses-detail", args=[course.id])
    response = api_client.get(url)

    assert response.status_code == 200
    assert response.data["id"] == course.id
    assert response.data["name"] == "Python 101"


def test_list_courses(api_client, course_factory):
    """Проверка получения списка курсов"""
    courses = course_factory(_quantity=5)
    url = reverse("courses-list")
    response = api_client.get(url)

    assert response.status_code == 200
    assert len(response.data) == len(courses)
    returned_ids = {c["id"] for c in response.data}
    expected_ids = {c.id for c in courses}
    assert returned_ids == expected_ids


def test_filter_courses_by_id(api_client, course_factory):
    """Проверка фильтрации курсов по id"""
    courses = course_factory(_quantity=5)
    target = courses[0]
    url = reverse("courses-list")
    response = api_client.get(url, data={"id": target.id})

    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]["id"] == target.id


def test_filter_courses_by_name(api_client, course_factory):
    """Проверка фильтрации курсов по name"""
    course_factory(name="Python")
    course_factory(name="Django")
    url = reverse("courses-list")
    response = api_client.get(url, data={"name": "Python"})

    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]["name"] == "Python"


def test_create_course(api_client):
    """Проверка успешного создания курса"""
    url = reverse("courses-list")
    data = {"name": "New Course"}
    response = api_client.post(url, data=data)

    assert response.status_code == 201
    created = Course.objects.first()
    assert created.name == "New Course"


def test_update_course(api_client, course_factory):
    """Проверка успешного обновления курса"""
    course = course_factory(name="Old Name")
    url = reverse("courses-detail", args=[course.id])
    response = api_client.patch(url, data={"name": "Updated Name"})

    assert response.status_code == 200
    course.refresh_from_db()
    assert course.name == "Updated Name"


def test_delete_course(api_client, course_factory):
    """Проверка успешного удаления курса"""
    course = course_factory()
    url = reverse("courses-detail", args=[course.id])
    response = api_client.delete(url)

    assert response.status_code == 204
    assert Course.objects.count() == 0


# ДОПОЛНИТЕЛЬНОЕ ЗАДАНИЕ


@pytest.mark.parametrize(
    "max_students, expected_status",
    [
        (20, 201),  # не превышает лимит
        (21, 400),  # превышает лимит
    ],
)
def test_max_students_per_course_limit(
    settings, api_client, student_factory, max_students, expected_status
):
    """
    Проверка ограничения максимального количества студентов на курсе.
    Использует параметр settings.MAX_STUDENTS_PER_COURSE.
    """
    settings.MAX_STUDENTS_PER_COURSE = 20

    # создаем студентов
    students = student_factory(_quantity=max_students)
    student_ids = [s.id for s in students]

    url = reverse("courses-list")
    data = {"name": f"Test Limit {max_students}", "students": student_ids}

    response = api_client.post(url, data=data)
    assert response.status_code == expected_status

    if expected_status == 201:
        course = Course.objects.get(name=f"Test Limit {max_students}")
        assert course.students.count() == max_students
    else:
        # если 400 — курс не должен быть создан
        assert not Course.objects.filter(name=f"Test Limit {max_students}").exists()
