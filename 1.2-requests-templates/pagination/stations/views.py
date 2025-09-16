import csv
from django.conf import settings
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.urls import reverse


def index(request):
    return redirect(reverse('bus_stations'))


def bus_stations(request):
    # читаем csv
    with open(settings.BUS_STATION_CSV, encoding='utf-8') as f:
        reader = csv.DictReader(f)
        stations = list(reader)

    # получаем номер страницы из GET-параметров (?page=2)
    page_number = int(request.GET.get('page', 1))

    # пагинация (по 10 записей на страницу)
    paginator = Paginator(stations, 10)
    page = paginator.get_page(page_number)

    context = {
        'bus_stations': page.object_list,  # записи текущей страницы
        'page': page,                      # объект страницы (для next/previous)
    }
    return render(request, 'stations/index.html', context)