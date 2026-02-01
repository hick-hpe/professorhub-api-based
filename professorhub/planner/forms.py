from django import forms
from .models import *
from datetime import date
from django.shortcuts import get_object_or_404

class CalendarioLetivoForm(forms.ModelForm):
    class Meta:
        model = CalendarioLetivo
        fields = ['nome', 'data_inicio', 'data_fim']

    nome = forms.CharField(
        label="Nome",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'id': 'nome',
            'required': True,
        })
    )

    data_inicio = forms.DateField(
        label="Data de início",
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'id': 'data_inicio',
            'type': 'date',
            'required': True
        })
    )

    data_fim = forms.DateField(
        label="Data final",
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'id': 'data_fim',
            'type': 'date',
            'required': True
        })
    )


class DataImportanteForm(forms.ModelForm):
    detalhes = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Detalhes da data',
        }),
    )

    class Meta:
        model = DataImportante
        fields = ['data', 'calendario', 'detalhes', 'dia_letivo']
        widgets = {
            'data': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'dia_letivo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        # print('cleaned_data:', cleaned_data)
        data = cleaned_data.get('data')
        calendario = cleaned_data.get('calendario')

        if calendario and data:
            print("calendario:", calendario)
            if not (calendario.data_inicio <= data <= calendario.data_fim):
                print('data inválida')
                self.add_error('data', 'A data deve estar dentro do intervalo do calendário letivo.')
        
        print('erros -> ', self.non_field_errors)
        return cleaned_data


class PeriodoImportanteForm(forms.ModelForm):
    detalhes = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Detalhes do período',
        }),
    )

    class Meta:
        model = PeriodoImportante
        fields = ['detalhes', 'data_inicio', 'data_fim', 'eh_letivo', 'calendario']
        labels = {
            'eh_letivo': 'É período letivo?',
            'data_inicio': 'Data de Início',
            'data_fim': 'Data Final',
        }
        widgets = {
            'data_inicio': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'data_fim': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'eh_letivo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['eh_letivo'].initial = False
    
    # validação no model?? 
    def clean(self):
        cleaned_data = super().clean()
        data_inicio = cleaned_data.get('data_inicio')
        data_fim = cleaned_data.get('data_fim')
        calendario = cleaned_data.get('calendario')

        if data_inicio and data_fim and data_inicio > data_fim:
            self.add_error('data_fim', "A data final deve ser maior ou igual à data de início.")
        
        if calendario and data_inicio and data_fim:
            if not (calendario.data_inicio <= data_inicio <= calendario.data_fim):
                self.add_error('data_inicio', 'A data de início deve estar dentro do intervalo do calendário letivo.')
            if not (calendario.data_inicio <= data_fim <= calendario.data_fim):
                self.add_error('data_fim', 'A data final deve estar dentro do intervalo do calendário letivo.')
        
        if data_fim and data_inicio and data_fim < data_inicio:
            self.add_error('data_fim', "A data final não pode ser anterior à data de início.")
        
        # sobreposição de períodos no mesmo calendário
        periodos_existentes = PeriodoImportante.objects.filter(calendario=calendario)
        for periodo in periodos_existentes:
            if (data_inicio <= periodo.data_fim and data_fim >= periodo.data_inicio):
                # nome do perido sobreposto
                self.add_error(
                    None,
                    f"O período informado sobrepõe-se ao período '{periodo.detalhes}', "
                    f"que ocorre de {periodo.data_inicio.strftime('%d/%m/%Y')} "
                    f"a {periodo.data_fim.strftime('%d/%m/%Y')}."
                )

        return cleaned_data


class DisciplinaForm(forms.ModelForm):
    CHOICE_PERIODOS = (
        ('semestral', 'Semestral'),
        ('anual', 'Anual'),
    )

    periodo = forms.ChoiceField(
        choices=CHOICE_PERIODOS,
        widget=forms.Select(attrs={'class': 'form-control'}),
        initial='semestral'
    )

    class Meta:
        model = Disciplina
        fields = ['nome', 'periodo', 'carga_horaria']
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'form-control',
                'maxlength': 100
            }),
            'periodo': forms.Select(attrs={
                'class': 'form-control'
            }),
            'carga_horaria': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 1000
            }),
        }

    def clean_nome(self):
        nome = self.cleaned_data.get('nome')
        if not nome or len(nome.strip()) == 0:
            raise forms.ValidationError('O nome da disciplina é obrigatório.')
        if len(nome.strip()) < 2:
            raise forms.ValidationError('O nome da disciplina deve ter pelo menos 2 caracteres.')
        return nome.strip()

    def clean_carga_horaria(self):
        carga_horaria = self.cleaned_data.get('carga_horaria')
        if not carga_horaria:
            raise forms.ValidationError('A carga horária é obrigatória.')
        if carga_horaria <= 0:
            raise forms.ValidationError('A carga horária deve ser maior que zero.')
        if carga_horaria > 200:
            raise forms.ValidationError('A carga horária não pode ser maior que 200 horas.')
        return carga_horaria

class PlanoAulaForm(forms.ModelForm):
    class Meta:
        model = PlanoAula
        fields = ['titulo', 'data']

class TarefaForm(forms.ModelForm):
    class Meta:
        model = Tarefa
        fields = ['disciplina', 'nome', 'descricao', 'prazo']
        widgets = {
            'prazo': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            })
        }

class AvaliacaoForm(forms.ModelForm):
    TIPO_CHOICES = [
        ('avaliacao', 'Avaliação'),
        ('prova', 'Prova'),
        ('trabalho', 'Trabalho'),
        ('recuperacao', 'Recuperação'),
        ('seminario', 'Seminário'),
    ]

    tipo = forms.ChoiceField(
        choices=TIPO_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        initial='prova'
    )

    class Meta:
        model = Avaliacao
        fields = ['disciplina', 'tipo', 'data', 'identificador']
        widgets = {
            'data': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'identificador': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Identificador da avaliação'
            }),
        }


class EmentaForm(forms.ModelForm):
    class Meta:
        model = Ementa
        fields = ['descricao']
        widgets = {
            'descricao': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Descrição da ementa',
                'maxlength': 255,
                'required': True
            }),
        }


class ObjetivoForm(forms.ModelForm):
    class Meta:
        model = Objetivo
        fields = ['descricao']
        widgets = {
            'descricao': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Descrição do objetivo',
                'maxlength': 255,
                'required': True
            }),
        }

