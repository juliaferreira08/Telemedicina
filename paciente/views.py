from django.shortcuts import render, redirect
from medico.models import DadosMedico, Especialidades, DatasAbertas, is_medico
from django.http import HttpResponse
from datetime import datetime
from .models import Consulta, Documento
from django.contrib import messages
from django.contrib.messages import constants

# Create your views here.
def home(request):
    if request.method == 'GET':
        medico_filtrar = request.GET.get('medico')
        especialidade_filtrar = request.GET.getlist('especialidades')
        medicos = DadosMedico.objects.all()

        if medico_filtrar:
            medicos = medicos.filter(nome__icontains=medico_filtrar)

        if especialidade_filtrar:
            medicos = medicos.filter(especialidade_id__in=especialidade_filtrar)

        especialidades = Especialidades.objects.all()
        proximas_consultas = Consulta.objects.filter(paciente=request.user).filter(data_aberta__data__gte=datetime.now()).filter(status='A')      
        
        return render(request, 'home.html', {'medicos': medicos, 'especialidades': especialidades, 'is_medico': is_medico(request.user), 'proximas_consultas': proximas_consultas})
    
def escolher_horario(request, id_dados_medicos):
    if request.method == 'GET':
        medico = DadosMedico.objects.get(id=id_dados_medicos)
        datas_abertas = DatasAbertas.objects.filter(user=medico.user).filter(data__gte=datetime.now()).filter(agendado=False)         

        return render(request, 'escolher_horario.html', {'medico': medico, 'datas_abertas': datas_abertas, 'is_medico': is_medico(request.user)})
    
def agendar_horario(request, id_data_aberta):
    if request.method == 'GET':
        data_aberta = DatasAbertas.objects.get(id=id_data_aberta)
        horario_agendado = Consulta(
            paciente = request.user,
            data_aberta = data_aberta 
        )

        horario_agendado.save()

        data_aberta.agendado = True
        data_aberta.save()

        messages.add_message(request, constants.SUCCESS, 'Consulta agendada com sucesso.')
        return redirect('/pacientes/minhas_consultas/')

def minhas_consultas(request):    
    if request.method == "GET":
        # Filtros
        data_filtrar = request.GET.get('data')
        especialidade_filtrar = request.GET.get('especialidades')
        minhas_consultas = Consulta.objects.filter(paciente=request.user)

        if data_filtrar:
            data_filtrar = datetime.strptime(data_filtrar, '%Y-%m-%d')
            minhas_consultas = minhas_consultas.filter(data_aberta__data__date=data_filtrar)
        else:
            minhas_consultas = minhas_consultas.filter(data_aberta__data__gte=datetime.now())

        if especialidade_filtrar:
            minhas_consultas = minhas_consultas.filter(data_aberta__user_id__dadosmedico__especialidade__especialidade__icontains=especialidade_filtrar)
      
        return render(request, 'minhas_consultas.html', {'minhas_consultas': minhas_consultas, 'is_medico': is_medico(request.user)})
    
def consulta(request, id_consulta):    
    if request.method == 'GET':        
        consulta = Consulta.objects.get(id=id_consulta)        
        dado_medico = DadosMedico.objects.get(user=consulta.data_aberta.user)       
        documentos = Documento.objects.filter(consulta=consulta) 
        
        return render(request, 'consulta.html', {'consulta': consulta, 'dado_medico': dado_medico, 'is_medico': is_medico(request.user), 'documentos': documentos})
    
def cancelar_consulta(request, id_consulta):    
    consulta = Consulta.objects.get(id=id_consulta)  
    
    if request.user != consulta.paciente:
        messages.add_message(request, constants.ERROR, 'Essa consulta não é sua.')  
        return redirect(f'/pacientes/minhas_consultas/')      

    consulta.status = 'C'
    consulta.save()

    messages.add_message(request, constants.SUCCESS, 'Consulta cancelada com sucesso.')

    return redirect(f'/pacientes/minhas_consultas/')

# fazer a validacao de segurança no restante dos pontos do código
# fazer o dashboard de desempenho dos médicos