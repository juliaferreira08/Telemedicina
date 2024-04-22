from django.contrib import admin
from .models import Especialidades, DadosMedico, DatasAbertas
# Register your models here. a

admin.site.register(Especialidades) 
admin.site.register(DadosMedico)
admin.site.register(DatasAbertas)