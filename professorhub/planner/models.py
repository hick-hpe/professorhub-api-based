from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta
from django.utils import timezone

class Professor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    conta_ativada = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username
    
class TokenAtivacaoConta(models.Model):
    email = models.CharField(max_length=64, unique=True, blank=True)
    token = models.CharField(max_length=64, unique=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    def codigo_expirou(self):
        # tempo_limite = timedelta(minutes=3)
        tempo_limite = timedelta(minutes=1)
        agora = timezone.now()
        return agora - self.criado_em > tempo_limite

    def __str__(self):
        return f'{self.email} - {self.token}'

# alterar para "CodigoRecuperacaoSenha"
class Codigo(models.Model):
    email = models.CharField(max_length=30, blank=True)
    code = models.CharField(max_length=6)
    data_criacao = models.DateTimeField(auto_now_add=True, null=True)

    def codigo_expirou(self):
        tempo_limite = timedelta(minutes=3)
        agora = timezone.now()
        return agora - self.data_criacao > tempo_limite

    def __str__(self):
        return self.email

class CalendarioLetivo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='calendarios')
    nome = models.CharField(max_length=100)
    data_inicio = models.DateField(null=True)
    data_fim = models.DateField(null=True)

    def __str__(self):
        return self.nome

class DataImportante(models.Model):
    calendario = models.ForeignKey(CalendarioLetivo, on_delete=models.CASCADE, related_name='datas')
    data = models.DateField()
    detalhes = models.CharField(max_length=255, default='')
    dia_letivo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.data} - {self.detalhes}"

class Disciplina(models.Model):
    PERIODO = [
        ('semestral', 'semestral'),
        ('anual', 'anual'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='disciplinas')
    calendario = models.ForeignKey(CalendarioLetivo, on_delete=models.CASCADE, related_name='disciplinas')
    nome = models.CharField(max_length=100)
    periodo = models.CharField(max_length=20, choices=PERIODO)
    carga_horaria = models.PositiveIntegerField()
    # rever como tratar isso dps
    aviso = models.CharField(max_length=100, default='')

    def __str__(self):
        return self.nome

class Ementa(models.Model):
    disciplina = models.ForeignKey(Disciplina, on_delete=models.CASCADE, related_name='ementas')
    descricao = models.CharField(max_length=255)
    abordado = models.BooleanField(default=False)
    plano_aula = models.ForeignKey('PlanoAula', on_delete=models.SET_NULL, null=True, blank=True, related_name='ementas_abordadas')
    
    class Meta:
        ordering = ['id']
        verbose_name = 'Ementa'
        verbose_name_plural = 'Ementas'
    
    def __str__(self):
        return f"{self.descricao} ({'Abordado' if self.abordado else 'Não abordado'})"

class Objetivo(models.Model):
    disciplina = models.ForeignKey(Disciplina, on_delete=models.CASCADE, related_name='objetivos')
    descricao = models.CharField(max_length=255)
    alcancado = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['id']
        verbose_name = 'Objetivo'
        verbose_name_plural = 'Objetivos'
    
    def __str__(self):
        return f"{self.descricao} ({'Alcançado' if self.alcancado else 'Não alcançado'})"

class PlanoAula(models.Model):
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('criado', 'Criado'),
        ('nao_planejada', 'Não planejada'),
        ('planejada', 'Planejada'),
        ('material_em_desenvolvimento', 'Material em desenvolvimento'),
        ('material_concluido', 'Material concluído'),
    ]
    disciplina = models.ForeignKey(Disciplina, on_delete=models.CASCADE, related_name='planos')
    data = models.DateField()
    titulo = models.CharField(max_length=100)
    objetivos = models.TextField(default='')
    conteudos = models.TextField(default='')
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='criado')
    num_aulas = models.PositiveIntegerField(default=2)

    def __str__(self):
        return f'{self.titulo} - {self.disciplina}'

class Tarefa(models.Model):
    STATUS_CHOICES = [
        ('criada', 'Criada'),
        ('em_andamento', 'Em andamento'),
        ('pendente', 'Pendente'),
        ('concluida', 'Concluída'),
        # ('concluida_com_atraso', 'Concluída com atraso'),
        # ('cancelada', 'Cancelada'),
    ]
    # user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tarefas')
    nome = models.CharField(max_length=50, default='')
    disciplina = models.ForeignKey(Disciplina, on_delete=models.CASCADE, related_name='tarefas')
    plano_aula = models.ForeignKey(PlanoAula, on_delete=models.CASCADE, related_name='tarefas', null=True, blank=True)
    descricao = models.TextField()
    prazo = models.DateField()
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='criada')

    def atualizar_para_pendente_se_expirou(self):
        agora = timezone.localdate()
        if self.status != 'pendente' and agora > self.prazo:
            self.status = 'pendente'
            self.save(update_fields=['status'])

    def __str__(self):
        if self.plano_aula:
            return f"{self.descricao[:50]} ({self.plano_aula.data.strftime('%d/%m/%Y')})"
        return f"{self.descricao[:50]} (Sem plano de aula)"

class Avaliacao(models.Model):
    STATUS_CHOICES = [
        ('nao_planejada', 'Não planejada'),
        ('planejada', 'Planejada'),
        ('em_elaboracao', 'Em elaboração'),
        ('elaborada', 'Elaborada'),
        ('aplicada', 'Aplicada'),
        ('corrigida', 'Corrigida'),
        ('agendada', 'Agendada'),
    ]
    TIPO_CHOICES = [
        ('avaliacao', 'Avaliação'),
        ('prova', 'Prova'),
        ('trabalho', 'Trabalho'),
        ('recuperacao', 'Recuperação'),
        ('seminario', 'Seminário'),
    ]
    ETAPAS_CHOICES = []
    disciplina = models.ForeignKey(Disciplina, on_delete=models.CASCADE, related_name='avaliacoes')
    plano_aula = models.ForeignKey(PlanoAula, on_delete=models.CASCADE, related_name='avaliacoes', null=True, blank=True)
    tipo = models.CharField(max_length=50, choices=TIPO_CHOICES)
    etapa = models.CharField(max_length=50, choices=ETAPAS_CHOICES, default='', null=True, blank=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='agendada')
    data = models.DateField()
    identificador = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.identificador} ({self.data.strftime('%d/%m/%Y')})"
