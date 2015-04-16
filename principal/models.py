# -*- coding: utf-8 -*-
from datetime import timedelta, date, datetime
from decimal import Decimal
import re

from django.contrib.auth.models import User
from django.contrib import admin
from django.core.urlresolvers import reverse
from django.db import models, transaction
from django.db.models import Sum
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.shortcuts import redirect

from funcoes import MESES, DIAS_SEMANA, TIPO_RECORRENCIA, hoje, valor, local_timezone, teste_operador


class Base(models.Model):
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name=u"Data Criação")
    data_alteracao = models.DateTimeField(auto_now=True, verbose_name=u"Data Alteração")

    class Meta:
        abstract = True

    def url_to_edit_object(self):
        url = reverse('admin:%s_%s_change' % (self._meta.app_label, self._meta.module_name), args=[self.id])
        return u'<a href="%s">Edit %s</a>' % (url, self.__unicode__())


class Empresa(Base):
    empresa = models.CharField(max_length=100, unique=True)
    usuarios = models.ManyToManyField(User, related_name='empresa_ususarios')
    conta_caixa = models.ForeignKey('Conta', related_name='empresa_conta_caixa', blank=True, null=True)
    operador_caixa = models.OneToOneField(User, related_name='empresa_operador_caixa', blank=True, null=True)
    abr = models.CharField(max_length=3, unique=True)

    def __unicode__(self):
        return unicode(self.empresa)

    class Meta:
        verbose_name = u"Empresa".encode('utf-8')
        verbose_name_plural = u"Empresas".encode('utf-8')
        ordering = ['empresa']

    class Admin(admin.ModelAdmin):
        list_display = ['empresa', ]
        search_fields = ['empresa']
        filter_horizontal = ['usuarios']


class EmpresaAtiva(Base):
    usuario = models.OneToOneField(User, related_name='usuario_empresa_ativa')
    empresa = models.ForeignKey(Empresa, blank=True, null=True)

    def __unicode__(self):
        return u"{} - Empresa Ativa: {}".format(self.usuario.first_name, self.empresa)

    class Meta:
        verbose_name = u"Empresa".encode('utf-8')
        verbose_name_plural = u"Empresa Ativa".encode('utf-8')
        ordering = ['usuario']

    class Admin(admin.ModelAdmin):
        list_display = ['usuario', 'empresa', ]
        list_editable = ['empresa', ]
        readonly_fields = ['usuario', ]

        def has_add_permission(self, request):
            return False

        def has_delete_permission(self, request, obj=None):
            return False

        def has_change_permission(self, request, obj=None):
            return True

        def changelist_view(self, request, extra_context=None):
            try:
                e = EmpresaAtiva.objects.get(usuario=request.user)
            except EmpresaAtiva.DoesNotExist:
                e = EmpresaAtiva(usuario=request.user)
                e.save()

            return redirect(
                reverse("admin:principal_empresaativa_change", args=(request.user.usuario_empresa_ativa.id,)))

        def get_queryset(self, request):
            q = super(EmpresaAtiva.Admin, self).get_queryset(request)
            return q.filter(usuario=request.user)

        def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
            if db_field.name == 'empresa':
                kwargs['queryset'] = Empresa.objects.filter(usuarios=request.user)
            return super(EmpresaAtiva.Admin, self).formfield_for_foreignkey(db_field, request, **kwargs)


@receiver(post_save, sender=User, dispatch_uid="cria_empresa_ativa")
def cria_empresa_ativa(signal, sender, instance, **kwargs):
    if kwargs['created']:
        e = EmpresaAtiva(usuario=instance)
        e.save()


class Recorrencia(Base):
    descricao = models.CharField(max_length=100, verbose_name=u"Descrição")
    tipo = models.IntegerField(choices=TIPO_RECORRENCIA, verbose_name=u"Tempo", default=2)
    qtd = models.IntegerField(default=1, verbose_name=u"A cada / Dia do Mês")
    dia_ano = models.IntegerField(blank=True, null=True, verbose_name=u"Dia Ano")
    mes_ano = models.IntegerField(blank=True, null=True, verbose_name=u"Mês Ano", choices=MESES)
    segunda = models.BooleanField(default=True)
    terca = models.BooleanField(default=True)
    quarta = models.BooleanField(default=True)
    quinta = models.BooleanField(default=True)
    sexta = models.BooleanField(default=True)
    sabado = models.BooleanField(default=True)
    domingo = models.BooleanField(default=True)

    def __unicode__(self):
        return unicode(self.descricao)

    class Meta:
        verbose_name = u"Recorrência".encode('utf-8')
        verbose_name_plural = u"Recorrências".encode('utf-8')
        ordering = ['descricao']

    class Admin(admin.ModelAdmin):
        list_display = ['descricao', ]
        search_fields = ['empresa', ]


class TesteRecorrencia(Base):
    inicio = models.DateField()
    recorrencia = models.ForeignKey(Recorrencia)
    numero = models.IntegerField(default=20)

    def __unicode__(self):
        return u"{} - {:%d/%m/%y}".format(self.recorrencia, self.inicio)

    class Meta:
        verbose_name = u"Teste Recorrência".encode('utf-8')
        verbose_name_plural = u"Recorrências - Teste".encode('utf-8')
        ordering = ['inicio']

    class Admin(admin.ModelAdmin):
        list_display = ['inicio', 'recorrencia', 'numero', ]
        date_hierarchy = 'inicio'
        list_editable = ['recorrencia', ]
        list_filter = ['recorrencia', ]

    def save(self, *args, **kwargs):
        super(TesteRecorrencia, self).save(*args, **kwargs)
        self.testerecorrenciaitem_set.all().delete()
        inicio = self.inicio
        check_dia = [self.recorrencia.segunda,
                     self.recorrencia.terca,
                     self.recorrencia.quarta,
                     self.recorrencia.quinta,
                     self.recorrencia.sexta,
                     self.recorrencia.sabado,
                     self.recorrencia.domingo,
                     ]
        for i in range(1, self.numero):
            data = inicio
            ok = True
            delta = None
            if self.recorrencia.tipo == 0:
                delta = timedelta(days=self.recorrencia.qtd)
            elif self.recorrencia.tipo == 1:
                delta = timedelta(weeks=self.recorrencia.qtd)
            elif self.recorrencia.tipo == 2:
                delta = timedelta(weeks=self.recorrencia.qtd * 4)
            elif self.recorrencia.tipo == 3:
                delta = timedelta(weeks=self.recorrencia.qtd * 52)
            elif self.recorrencia.tipo == 4:
                try:
                    data_ok = data.replace(month=data.month + 1)
                except ValueError:
                    if data.month == 12:
                        try:
                            data_ok = data.replace(year=data.year + 1, month=1)
                        except ValueError:
                            data_ok = None
                            d = 0
                            while data_ok is None:
                                d += 1
                                try:
                                    data_ok = data.replace(year=data.year + 1, month=1, day=data.day - d)
                                except ValueError:
                                    pass
                    else:
                        data_ok = None
                        d = 0
                        while data_ok is None:
                            d += 1
                            try:
                                data_ok = data.replace(month=data.month + 1, day=data.day - d)
                            except ValueError:
                                pass
                data = data_ok
            elif self.recorrencia.tipo == 5:
                data_ok = None
                d = -1
                while data_ok is None:
                    d += 1
                    try:
                        data_ok = date(data.year + 1, self.recorrencia.mes_ano, self.recorrencia.dia_ano - d)
                    except ValueError:
                        pass
                data = data_ok
            if delta:
                data = inicio + delta
            if data:
                r = 0
                while check_dia[data.weekday()] is False:
                    data += timedelta(days=1)
                    r += 1
                    if r > 10:
                        ok = False
                        break
                if ok:
                    t = TesteRecorrenciaItem(teste=self, item=i, data=data)
                    t.save()
            inicio = data


class TesteRecorrenciaItem(Base):
    teste = models.ForeignKey(TesteRecorrencia)
    item = models.IntegerField()
    data = models.DateField()

    def dia_semana(self):
        return DIAS_SEMANA[self.data.weekday()][1]

    dia_semana.short_description = u"Dia Semana"

    def __unicode__(self):
        return u"{} - {} - {:%d/%m/%y}".format(self.teste, self.item, self.data)

    class Meta:
        verbose_name = u"Item Teste Recorrência".encode('utf-8')
        verbose_name_plural = u"Recorrências - Teste - Item".encode('utf-8')
        ordering = ['teste', 'item', 'data']

    class Admin(admin.ModelAdmin):
        list_display = ['teste', 'item', 'data', 'dia_semana', ]
        date_hierarchy = 'data'
        list_filter = ['teste', ]


class Conta(Base):
    empresa = models.ForeignKey('principal.Empresa')
    conta = models.CharField(max_length=100)
    cartao = models.BooleanField(default=False)
    abr = models.CharField(max_length=3)

    def __unicode__(self):
        return u"{} - {}".format(self.empresa.abr, self.conta)

    def saldo_atual(self):
        lancamentos = self.lancamento_set.anteriores().aggregate(total=Sum('total'))['total'] or 0
        saida = self.transferencia_conta_de.anteriores().aggregate(total=Sum('total'))['total'] or 0
        entrada = self.transferencia_conta_para.anteriores().aggregate(total=Sum('total'))['total'] or 0
        return lancamentos - saida + entrada

    def lancamentos_futuros(self):
        lancamentos = self.lancamento_set.futuros().aggregate(total=Sum('total'))['total'] or 0
        saida = self.transferencia_conta_de.futuros().aggregate(total=Sum('total'))['total'] or 0
        entrada = self.transferencia_conta_para.futuros().aggregate(total=Sum('total'))['total'] or 0
        return lancamentos - saida + entrada

    class Meta:
        verbose_name = u"Conta Financeira".encode('utf-8')
        verbose_name_plural = u"Contas Financeiras".encode('utf-8')
        ordering = ['conta']
        unique_together = [('empresa', 'conta', ), ('empresa', 'abr', ), ]

    class Admin(admin.ModelAdmin):
        list_display = ['empresa', 'conta', 'saldo_atual', 'lancamentos_futuros', ]
        list_display_links = ['empresa', 'conta', ]
        search_fields = ['conta', ]

        def get_queryset(self, request):
            q = super(Conta.Admin, self).get_queryset(request)
            return q.filter(empresa__usuarios=request.user)


class FinanceiroGrupo(Base):
    grupo = models.CharField(max_length=50)
    abr = models.CharField(max_length=10)
    empresas = models.ManyToManyField('principal.Empresa')

    def __unicode__(self):
        return unicode(self.grupo)

    class Meta:
        verbose_name = u"Grupo Financeiro".encode('utf-8')
        verbose_name_plural = u"Grupos Financeiros".encode('utf-8')
        ordering = ['grupo', ]

    class Admin(admin.ModelAdmin):
        fields = ['grupo', 'abr', 'empresas', ]
        list_display = ['grupo', 'abr', ]
        search_fields = ['grupo', ]
        filter_horizontal = ['empresas', ]


class FinanceiroSubGrupo(Base):
    empresas = models.ManyToManyField('principal.Empresa', verbose_name=u"Empresas")
    grupo = models.ForeignKey(FinanceiroGrupo, verbose_name=u"Grupo")
    subgrupo = models.CharField(max_length=50, verbose_name=u"SubGrupo")
    abr = models.CharField(max_length=10, verbose_name=u"Abreviação")
    classes = models.ManyToManyField('contenttypes.ContentType', verbose_name=u"Classes")

    def __unicode__(self):
        return u"{} - {}".format(self.grupo, self.subgrupo)

    class Meta:
        verbose_name = u"SubGrupo Financeiro".encode('utf-8')
        verbose_name_plural = u"SubGrupos Financeiros".encode('utf-8')
        ordering = ['grupo__grupo', 'subgrupo']

    class Admin(admin.ModelAdmin):
        fields = ['grupo', 'subgrupo', 'abr', 'empresas', 'classes']
        list_display = ['grupo', 'subgrupo', 'abr', ]
        search_fields = ['subgrupo']
        list_filter = ['grupo']
        filter_horizontal = ['empresas', 'classes']


class LancamentoQuerySet(models.QuerySet):
    def anteriores(self):
        return self.filter(data__lte=hoje())

    def futuros(self):
        return self.filter(data__gt=hoje())


class Lancamento(Base):
    data = models.DateField(default=hoje, verbose_name=u"Data")
    conta = models.ForeignKey(Conta, verbose_name=u"Conta")
    subgrupo = models.ForeignKey(FinanceiroSubGrupo, verbose_name=u"SubGrupo")
    descricao = models.CharField(max_length=150, verbose_name=u"Descrição")
    valor = models.DecimalField(decimal_places=2, max_digits=18, verbose_name=u"Valor")
    total = models.DecimalField(decimal_places=2, max_digits=18, verbose_name=u"Valor")

    objects = LancamentoQuerySet.as_manager()

    def __unicode__(self):
        return u"{} - {} - {} - {}".format(self.conta, self.subgrupo, self.descricao, valor(self.total))

    class Meta:
        verbose_name = u"Lancamento Financeiro".encode('utf-8')
        verbose_name_plural = u"Lancamentos Financeiros".encode('utf-8')
        ordering = ['-data', 'conta__conta', 'subgrupo__grupo__grupo', 'subgrupo__subgrupo', 'total', ]

    class Admin(admin.ModelAdmin):
        fields = [('data', 'conta', ),
                  ('subgrupo', 'descricao'),
                  ('total', ),
                  ('data_criacao', 'data_modificacao', ), ]
        readonly_fields = ['data', 'conta', 'subgrupo', 'descricao', 'total', ]
        list_display = ['data', 'conta', 'subgrupo', 'total', ]
        search_fields = ['descricao', ]
        list_filter = ['conta', 'subgrupo__grupo', 'subgrupo', ]
        date_hierarchy = 'data'
        actions = None

        def has_add_permission(self, request):
            return False

        def has_delete_permission(self, request, obj=None):
            return False


class TransferenciaQuerySet(models.QuerySet):
    def anteriores(self):
        return self.filter(data__lte=hoje())

    def futuros(self):
        return self.filter(data__gt=hoje())


class ContaDeListFilter(admin.SimpleListFilter):
    title = u'Conta Saída'
    parameter_name = 'conta_de'

    def lookups(self, request, model_admin):
        contas = Conta.objects.filter(empresa__usuarios=request.user)
        for i in contas:
            yield (i.id, i.__unicode__())

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(conta_de=self.value())
        else:
            return queryset


class ContaParaListFilter(admin.SimpleListFilter):
    title = u'Conta Entrada'
    parameter_name = 'conta_para'

    def lookups(self, request, model_admin):
        contas = Conta.objects.filter(empresa__usuarios=request.user)
        for i in contas:
            yield (i.id, i.__unicode__())

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(conta_para=self.value())
        else:
            return queryset


class Transferencia(Base):
    data = models.DateField(default=hoje, verbose_name=u"Data")
    conta_de = models.ForeignKey(Conta, verbose_name=u"Conta Saída", related_name='transferencia_conta_de')
    conta_para = models.ForeignKey(Conta, verbose_name=u"Conta Entrada", related_name='transferencia_conta_para')
    descricao = models.CharField(max_length=150, verbose_name=u"Descrição")
    total = models.DecimalField(decimal_places=2, max_digits=18, verbose_name=u"Valor")

    objects = TransferenciaQuerySet.as_manager()

    def __unicode__(self):
        return u"{} - {} - {} - {}".format(self.conta_de, self.conta_de, self.descricao, valor(self.total))

    class Meta:
        verbose_name = u"Transferência Financeira".encode('utf-8')
        verbose_name_plural = u"Transferências Financeiras".encode('utf-8')
        ordering = ['-data', 'conta_de__conta', 'conta_para__conta', 'total']

    class Admin(admin.ModelAdmin):
        fields = ['data', ('conta_de', 'conta_para'), 'descricao', 'total', ]
        list_display = ['data', 'conta_de', 'conta_para', 'descricao', 'total', ]
        search_fields = ['descricao', ]
        list_filter = [ContaDeListFilter, ContaParaListFilter, ]
        date_hierarchy = 'data'

        def get_queryset(self, request):
            q = super(Transferencia.Admin, self).get_queryset(request)
            return q.filter(conta_de__empresa__usuarios=request.user, conta_para__empresa__usuarios=request.user)

        def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
            if db_field.name in ['conta_de', 'conta_para']:
                kwargs['queryset'] = Conta.objects.filter(empresa__usuarios=request.user)
            return super(Transferencia.Admin, self).formfield_for_foreignkey(db_field, request, **kwargs)


class Despesa(Lancamento):
    class Meta:
        verbose_name = u"Despesa".encode('utf-8')
        verbose_name_plural = u"Despesas".encode('utf-8')
        ordering = ['-data', 'conta', '-valor']

    class Admin(admin.ModelAdmin):
        fields = [('data', 'conta', ),
                  ('subgrupo', 'descricao', ),
                  ('valor', ),
                  ('data_criacao', 'data_modificacao', ), ]
        readonly_fields = ['data', 'conta', 'subgrupo', 'descricao', 'valor', ]
        list_display = ['data', 'conta', 'subgrupo', 'valor', ]
        search_fields = ['descricao', 'valor']
        list_filter = ['conta', 'subgrupo__grupo', 'subgrupo', ]
        date_hierarchy = 'data'

    def save(self, *args, **kwargs):
        self.total = -self.valor
        super(Despesa, self).save(*args, **kwargs)


class DespesaCaixa(Despesa):
    funcionario = models.ForeignKey('Funcionario', blank=True, null=True)

    class Meta:
        verbose_name = u"Despesa".encode('utf-8')
        verbose_name_plural = u"Caixa - Despesas".encode('utf-8')
        ordering = ['-data', ]

    class Admin(admin.ModelAdmin):
        fields = [('valor', 'data', ),
                  ('subgrupo', 'descricao', ),
                  ('funcionario', ), ]
        list_display = ['data', 'subgrupo', 'funcionario', 'valor', ]
        search_fields = ['descricao', 'valor', ]
        list_filter = ['subgrupo__grupo', 'subgrupo', ]
        date_hierarchy = 'data'

        def save_model(self, request, obj, form, change):
            # todo TESTAR
            obj.empresa = request.user.operador_caixa
            obj.conta = request.user.operador_caixa.conta_caixa
            obj.save()

        def has_add_permission(self, request, obj=None):
            return teste_operador(request.user)

        def has_change_permission(self, request, obj=None):
            return teste_operador(request.user)

        def has_delete_permission(self, request, obj=None):
            return teste_operador(request.user)


class PagamentoFuncionario(Lancamento):
    funcionario = models.ForeignKey('Funcionario')

    class Meta:
        verbose_name = u"Pagamento Funcionário".encode('utf-8')
        verbose_name_plural = u"Funcionários - Pagamentos".encode('utf-8')
        ordering = ['-data', 'conta', 'funcionario__nome']

    class Admin(admin.ModelAdmin):
        fields = [('valor', 'data', ),
                  ('funcionario', 'descricao', ), ]
        list_display = ['data', 'funcionario', 'valor', ]
        search_fields = ['descricao', 'valor', ]
        list_filter = ['subgrupo__grupo', 'subgrupo', ]
        date_hierarchy = 'data'

    def save(self, *args, **kwargs):
        self.total = -self.valor
        super(PagamentoFuncionario, self).save(*args, **kwargs)


class PagamentoCompra(Lancamento):
    parcela = models.ForeignKey('CompraParcela')

    def valor(self):
        return valor(self.parcela.valor)

    class Meta:
        verbose_name = u"Pagamento".encode('utf-8')
        verbose_name_plural = u"Compras - Pagamentos".encode('utf-8')
        ordering = ['-data', 'parcela__valor', ]

    class Admin(admin.ModelAdmin):
        raw_id_fields = ['parcela']
        autocomplete_lookup_fields = {'fk': ['parcela', ]}
        fields = [('parcela', ),
                  ('data', 'conta', 'valor', ), ]
        readonly_fields = ['valor']
        list_display = ['data', 'conta', 'parcela', 'valor', ]
        search_fields = ['parcela__nf']
        list_filter = ['conta', ]
        date_hierarchy = 'data'

    def save(self, *args, **kwargs):
        self.total = -self.parcela.valor
        super(PagamentoCompra, self).save(*args, **kwargs)


class Setor(models.Model):
    setor = models.CharField(max_length=100)

    def __unicode__(self):
        return unicode(self.setor)

    class Meta:
        verbose_name = u"Setor".encode('utf-8')
        verbose_name_plural = u"Setores".encode('utf-8')
        ordering = ['setor']

    class Admin(admin.ModelAdmin):
        list_display = ['setor', ]
        search_fields = ['setor', ]


class Diretoria(models.Model):
    nome = models.CharField(max_length=100)
    conta = models.ForeignKey(Conta)

    def __unicode__(self):
        return unicode(self.nome)

    class Meta:
        verbose_name = u"Diretor".encode('utf-8')
        verbose_name_plural = u"Diretoria".encode('utf-8')
        ordering = ['nome']

    class Admin(admin.ModelAdmin):
        list_display = ['nome', ]
        search_fields = ['nome', ]


class Funcionario(models.Model):
    data_admissao = models.DateField()
    data_demissao = models.DateField(blank=True, null=True)
    nome = models.CharField(max_length=100)
    segundo_nome = models.CharField(max_length=150)
    sobrenome = models.CharField(max_length=150)
    setor = models.ForeignKey(Setor)
    nome_pai = models.CharField(max_length=100)

    def saldo(self):
        return valor(self.saldo_vlr())

    def saldo_vlr(self):
        pagamentos = self.pagamentofuncionario_set.aggregate(total=Sum('total'))['total'] or 0
        despesas = self.despesacaixa_set.aggregate(total=Sum('total'))['total'] or 0
        # todo
        return pagamentos + despesas

    def __unicode__(self):
        return unicode(self.nome)

    class Meta:
        verbose_name = u"Funcionário".encode('utf-8')
        verbose_name_plural = u"Funcionários".encode('utf-8')
        ordering = ['nome']

    class Admin(admin.ModelAdmin):
        list_display = ['nome', 'setor', 'saldo']
        search_fields = ['nome', 'segundo_nome', 'sobrenome', ]
        list_filter = ['setor', ]


class Turno(models.Model):
    data = models.DateField(default=hoje)
    turno = models.IntegerField(choices=((0, u"Jantar"), (1, u"Almoço"), (2, u"Extra")))
    aberto = models.BooleanField(default=False)

    def numero_cupons(self):
        return self.cupomnovo_set.count()

    def venda(self):
        return self.cupomnovo_set.aggregate(total=Sum('total'))['total'] or 0

    def __unicode__(self):
        return u"{:%d/%m/%y} - {}".format(self.data, self.get_turno_display())

    class Meta:
        verbose_name = u"Turno".encode('utf-8')
        verbose_name_plural = u"Turnos".encode('utf-8')
        ordering = ['-data', '-turno']
        unique_together = ['data', 'turno']

    class Admin(admin.ModelAdmin):
        list_display = ['data', 'turno', 'aberto', 'numero_cupons', 'venda']
        list_filter = ['turno', ]
        list_editable = ['aberto']
        date_hierarchy = 'data'


class Cupom(models.Model):
    ccf = models.BigIntegerField(unique=True)
    coo = models.BigIntegerField(unique=True, blank=True, null=True)
    data = models.DateTimeField(blank=True, null=True)
    mesa = models.IntegerField(blank=True, null=True)
    subtotal = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    desconto = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    cancelado = models.BooleanField(default=False)
    qtd_belvitur = models.IntegerField(default=0)
    diretoria = models.ForeignKey(Diretoria, blank=True, null=True)
    funcionario = models.ForeignKey(Funcionario, blank=True, null=True)
    importado = models.BooleanField(default=False)

    def turno(self):
        return self.cupomnovo.turno

    def recebimentos(self):
        return valor(self.recebimento_set.aggregate(total=Sum('total'))['total'] or Decimal('0.00'))

    def cartao(self):
        itens = self.recebimento_set.filter(recebimentocartao__id__isnull=False)
        return valor(itens.aggregate(total=Sum('total'))['total'] or Decimal('0.00'))

    def dinheiro(self):
        itens = self.recebimento_set.filter(recebimentodinheiro__id__isnull=False)
        return valor(itens.aggregate(total=Sum('total'))['total'] or Decimal('0.00'))

    def cheque(self):
        itens = self.recebimento_set.filter(recebimentocheque__id__isnull=False)
        return valor(itens.aggregate(total=Sum('total'))['total'] or Decimal('0.00'))

    def outros(self):
        itens = self.recebimento_set.filter(recebimentooutros__id__isnull=False)
        return valor(itens.aggregate(total=Sum('total'))['total'] or Decimal('0.00'))

    def qtd_unimed(self):
        return self.cupomunimed_set.count() or 0

    def check_itens(self):
        return True if (self.cupomitem_set.aggregate(total=Sum('total'))['total'] or 0) == (
            self.total - self.desconto) else False

    check_itens.boolean = True

    def check_recebimento(self):
        return True if self.total <= (self.recebimento_set.aggregate(total=Sum('total'))['total'] or 0) else False

    check_recebimento.boolean = True

    def __unicode__(self):
        return u"CCF: {} - COO: {} - {} - Mesa: {} Total: {}".format(self.ccf,
                                                                     self.coo,
                                                                     self.data.strftime(
                                                                         "%d/%m/%y %H:%M") if self.data else '',
                                                                     self.mesa or '',
                                                                     valor(self.total) or '')

    class Meta:
        verbose_name = u"Cupom".encode('utf-8')
        verbose_name_plural = u"Cupons".encode('utf-8')
        ordering = ['cupomnovo__turno', 'ccf']

    class Admin(admin.ModelAdmin):
        fields = [('ccf', 'coo', 'turno'),
                  ('mesa', 'subtotal', 'desconto'),
                  ('total', 'qtd_belvitur', 'cancelado'),
                  ('recebimentos', 'diretoria', 'funcionario'), ]
        readonly_fields = ['ccf', 'coo', 'recebimentos', 'mesa', 'subtotal', 'desconto', 'total', 'turno', 'cancelado',
                           'turno']
        list_display = ['turno', 'ccf', 'coo', 'mesa', 'data', 'subtotal', 'desconto',
                        'total', 'recebimentos', 'cancelado', 'check_itens', 'check_recebimento']
        list_display_links = ['ccf', 'coo']
        list_filter = ['cupomnovo__turno', 'mesa', 'cancelado']
        search_fields = ['ccf', 'coo', 'subtotal', 'desconto', 'total']

        # def save(self, *args, **kwargs):
        # super(Cupom, self).save(*args, **kwargs)
        # for i in self.recebimento_set.all():
        # i.turno = self.turno
        # i.save()


class CupomNovo(Cupom):
    turno = models.ForeignKey(Turno, blank=False, null=False, default=1)

    def __unicode__(self):
        return u"CCF: {} - {}".format(self.ccf, self.recebimentos())

    class Meta:
        verbose_name = u"Cupom".encode('utf-8')
        verbose_name_plural = u"Caixa - Cupons".encode('utf-8')
        ordering = ['turno', 'ccf']

    class Admin(admin.ModelAdmin):
        fields = [('ccf', 'turno',), 'qtd_belvitur', ('recebimentos', 'diretoria', 'funcionario'), ]
        readonly_fields = ['recebimentos']
        list_display = ['turno', 'ccf', 'qtd_belvitur', 'qtd_unimed', 'recebimentos', 'cartao', 'dinheiro',
                        'cheque', 'outros']
        list_display_links = ['turno', 'ccf']
        list_filter = ['turno']
        search_fields = ['ccf', 'coo']

        def has_add_permission(self, request, obj=None):
            return teste_operador(request.user)

        def has_change_permission(self, request, obj=None):
            return teste_operador(request.user)

        def has_delete_permission(self, request, obj=None):
            return teste_operador(request.user)

        def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
            if db_field.name == 'turno':
                kwargs["queryset"] = Turno.objects.filter(aberto=True)
            return super(CupomNovo.Admin, self).formfield_for_foreignkey(db_field, request, **kwargs)


class CupomUnimed(models.Model):
    cupom = models.ForeignKey(Cupom)
    codigo = models.CharField(max_length=100)

    def __unicode__(self):
        return unicode(self.codigo)

    class Meta:
        verbose_name = u"Cupom Unimed".encode('utf-8')
        verbose_name_plural = u"Cupons Unimed".encode('utf-8')

    class Admin(admin.ModelAdmin):
        list_display = ['cupom', 'codigo']
        search_fields = ['codigo']


class Recebimento(Lancamento):
    cupom = models.ForeignKey(Cupom)
    tipo = models.IntegerField(choices=((0, u"Cartão"), (1, u"Dinheiro"), (2, u"Cheque"), (3, u"Outros")), default=0)

    def __unicode__(self):
        return u"CCF: {} - {} - {}".format(self.cupom.ccf, self.get_tipo_display(), valor(self.total))

    class Meta:
        verbose_name = u"Recebimento".encode('utf-8')
        verbose_name_plural = u"Recebimentos".encode('utf-8')
        ordering = ['-cupom__cupomnovo__turno__data', '-cupom__cupomnovo__turno', 'cupom__ccf', 'tipo', 'total']

    class Admin(admin.ModelAdmin):
        list_display = ['cupom', 'tipo', 'conta', 'total']
        list_filter = ['cupom__cupomnovo__turno', 'cupom__cancelado', 'conta']
        search_fields = ['cupom__ccf', 'cupom__coo']

        def has_add_permission(self, request):
            return False


class RecebimentoDinheiro(Recebimento):
    def __unicode__(self):
        return u"{} - DIN {}".format(self.cupom.ccf, valor(self.total))

    class Meta:
        verbose_name = u"Recebimento Dinheiro".encode('utf-8')
        verbose_name_plural = u"Recebimentos - Dinheiro".encode('utf-8')
        ordering = ['-cupom__cupomnovo__turno__data', '-cupom__cupomnovo__turno', 'cupom__ccf', 'total']

    class Admin(admin.ModelAdmin):
        fields = ['cupom', 'total']
        list_display = ['cupom', 'total']
        list_filter = ['cupom__cupomnovo__turno', 'cupom__cancelado']
        search_fields = ['cupom__ccf', 'cupom__coo', 'total']

    def save(self, *args, **kwargs):
        self.conta_id = 1
        self.tipo = 1
        super(RecebimentoDinheiro, self).save(*args, **kwargs)


class RecebimentoOutros(Recebimento):
    obs = models.TextField()

    def __unicode__(self):
        return u"{} - {} {}".format(self.cupom.ccf, self.obs[:100], valor(self.total))

    class Meta:
        verbose_name = u"Recebimento Outro".encode('utf-8')
        verbose_name_plural = u"Recebimentos - Outros".encode('utf-8')
        ordering = ['-cupom__cupomnovo__turno__data', '-cupom__cupomnovo__turno', 'cupom__ccf', 'total']

    class Admin(admin.ModelAdmin):
        fields = ['cupom', 'obs', 'total']
        list_display = ['cupom', 'obs', 'total']
        list_filter = ['cupom__cupomnovo__turno', 'cupom__cancelado']
        search_fields = ['cupom__ccf', 'cupom__coo', 'total', 'obs']

    def save(self, *args, **kwargs):
        self.conta_id = 1
        self.tipo = 3
        super(RecebimentoOutros, self).save(*args, **kwargs)


class RecebimentoCheque(Recebimento):
    banco = models.CharField(max_length=3)
    agencia = models.CharField(max_length=4)
    dv_agencia = models.CharField(max_length=1)
    cc = models.CharField(max_length=15)
    dv_cc = models.CharField(max_length=1)

    def __unicode__(self):
        return u"{} - CHE {}".format(self.cupom.ccf, valor(self.total))

    class Meta:
        verbose_name = u"Recebimento Cheque".encode('utf-8')
        verbose_name_plural = u"Recebimentos - Cheque".encode('utf-8')
        ordering = ['-cupom__cupomnovo__turno__data', '-cupom__cupomnovo__turno', 'cupom__ccf', 'total']

    class Admin(admin.ModelAdmin):
        fields = ['cupom', 'banco', 'agencia', 'dv_agencia', 'cc', 'dv_cc', 'total']
        list_display = ['cupom', 'banco', 'agencia', 'dv_agencia', 'cc', 'dv_cc', 'total']
        list_filter = ['cupom__cupomnovo__turno', 'cupom__cancelado', 'banco']
        search_fields = ['cupom__ccf', 'cupom__coo', 'agencia', 'cc', 'total']

    def save(self, *args, **kwargs):
        self.conta_id = 1
        self.tipo = 2
        super(RecebimentoCheque, self).save(*args, **kwargs)


class RecebimentoCartao(Recebimento):
    cartao = models.ForeignKey(Conta, limit_choices_to={'cartao': True}, default=1, blank=False, null=False)
    digitos = models.CharField(max_length=4)
    doc = models.CharField(max_length=100)
    autorizacao = models.CharField(max_length=100)

    def __unicode__(self):
        return u"{} - {} {}".format(self.cupom.ccf, self.cartao.abr, valor(self.total))

    class Meta:
        verbose_name = u"Recebimento Cartão".encode('utf-8')
        verbose_name_plural = u"Recebimentos - Cartão".encode('utf-8')
        ordering = ['-cupom__cupomnovo__turno__data', '-cupom__cupomnovo__turno', 'cupom__ccf', 'cartao__cartao',
                    'total']

    class Admin(admin.ModelAdmin):
        raw_id_fields = ['cupom']
        fields = ['cupom', 'cartao', 'digitos', 'doc', 'autorizacao', 'total']
        list_display = ['cupom', 'cartao', 'digitos', 'doc', 'autorizacao', 'total']
        search_fields = ['cupom__ccf', 'cupom__coo', 'digitos', 'doc', 'autorizacao', 'total']
        list_filter = ['cupom__cupomnovo__turno', 'cartao']

    def save(self, *args, **kwargs):
        self.conta = self.cartao
        self.tipo = 0
        super(RecebimentoCartao, self).save(*args, **kwargs)


class Fornecedor(models.Model):
    fornecedor = models.CharField(max_length=100)
    razao_social = models.CharField(max_length=200)
    cnpj = models.CharField(max_length=14, help_text=u"Sem pontos ou traços.")
    contato = models.CharField(max_length=100, blank=True, null=True)
    telefone_ddd = models.DecimalField(decimal_places=0, max_digits=2, blank=True, null=True)
    telefone = models.DecimalField(decimal_places=0, max_digits=9, blank=True, null=True)
    endereco = models.TextField(blank=True, null=True)

    @staticmethod
    def autocomplete_search_fields():
        return ["fornecedor__icontains", "razao_social__icontains", "cnpj__icontains", ]

    def __unicode__(self):
        return u"{}".format(self.fornecedor)

    class Meta:
        verbose_name = u"Fornecedor".encode('utf-8')
        verbose_name_plural = u"Fornecedores".encode('utf-8')
        ordering = ['fornecedor']

    class Admin(admin.ModelAdmin):
        list_display = ['fornecedor', 'razao_social', 'cnpj', 'contato', 'telefone_ddd', 'telefone']
        search_fields = ['fornecedor', 'razao_social', 'cnpj', 'contato', 'telefone', 'endereco']
        list_filter = ['telefone_ddd']


class Compra(models.Model):
    nf = models.CharField(max_length=30)
    fornecedor = models.ForeignKey(Fornecedor)
    data_emissao = models.DateField(default=hoje)
    data_recebimento = models.DateField(default=hoje)
    desconto = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    valor_extra = models.DecimalField(max_digits=18, decimal_places=2, default=0)

    @staticmethod
    def autocomplete_search_fields():
        return ["nf__icontains", "fornecedor__fornecedor__icontains", ]

    def total(self):
        return valor(self.total_vlr())

    def total_vlr(self):
        return self.valor_extra + (self.compraitem_set.aggregate(total=Sum('total'))['total'] or 0) - self.desconto

    def check_parcelas(self):
        return True if self.total_vlr() == (
            self.compraparcela_set.aggregate(total=Sum('valor'))['total'] or 0) else False

    check_parcelas.boolean = True

    def __unicode__(self):
        return u"NF: {} - {} - {:%d/%m/%y}".format(self.nf, self.fornecedor, self.data_recebimento)

    class Meta:
        verbose_name = u"Compra".encode('utf-8')
        verbose_name_plural = u"Compras".encode('utf-8')
        ordering = ['-data_recebimento', 'fornecedor', 'nf']

    class Admin(admin.ModelAdmin):
        fields = [('nf', 'fornecedor',), ('data_emissao', 'data_recebimento',),
                  ('valor_extra', 'desconto', 'total', 'check_parcelas'), ]
        readonly_fields = ['total', 'check_parcelas']
        raw_id_fields = ['fornecedor']
        autocomplete_lookup_fields = {
            'fk': ['fornecedor'],
        }
        list_display = ['nf', 'fornecedor', 'data_recebimento', 'valor_extra', 'total', 'check_parcelas', ]
        search_fields = ['nf', 'fornecedor__fonecedor', 'valor_extra']
        list_filter = ['fornecedor']
        date_hierarchy = 'data_recebimento'


class CompraParcela(models.Model):
    compra = models.ForeignKey(Compra)
    data_vencimento = models.DateField()
    valor = models.DecimalField(max_digits=18, decimal_places=2)

    def __unicode__(self):
        return u"NF: {} - {} - {:%d/%m/%y} - {}".format(self.compra.nf,
                                                        self.compra.fornecedor,
                                                        self.data_vencimento,
                                                        valor(self.valor))

    class Meta:
        verbose_name = u"Parcela".encode('utf-8')
        verbose_name_plural = u"Compras - Parcelas".encode('utf-8')
        ordering = ['-data_vencimento', ]

    class Admin(admin.ModelAdmin):
        raw_id_fields = ['compra']
        list_display = ['data_vencimento', 'compra', 'valor']
        date_hierarchy = 'data_vencimento'
        search_fields = ['valor']


class ProdutoGrupo(models.Model):
    grupo = models.CharField(max_length=100)

    def __unicode__(self):
        return u"{}".format(self.grupo)

    class Meta:
        verbose_name = u"Grupo".encode('utf-8')
        verbose_name_plural = u"Produtos - Grupos".encode('utf-8')
        ordering = ['grupo']

    class Admin(admin.ModelAdmin):
        list_display = ['grupo']
        search_fields = ['grupo']


class ProdutoSubGrupo(models.Model):
    grupo = models.ForeignKey(ProdutoGrupo)
    subgrupo = models.CharField(max_length=100)

    def __unicode__(self):
        return u"{}".format(self.subgrupo)

    class Meta:
        verbose_name = u"SubGrupo".encode('utf-8')
        verbose_name_plural = u"Produtos - SubGrupos".encode('utf-8')
        ordering = ['grupo__grupo', 'subgrupo']

    class Admin(admin.ModelAdmin):
        list_display = ['grupo', 'subgrupo']
        search_fields = ['grupo__grupo', 'subgrupo']
        list_filter = ['grupo']


class ProdutoUnidade(models.Model):
    unidade = models.CharField(max_length=2)

    def __unicode__(self):
        return u"{}".format(self.unidade)

    class Meta:
        verbose_name = u"Unidade".encode('utf-8')
        verbose_name_plural = u"Produtos - Unidades".encode('utf-8')
        ordering = ['unidade']

    class Admin(admin.ModelAdmin):
        list_display = ['unidade']
        search_fields = ['unidade']


class ProdutoEstoque(models.Model):
    estoque = models.CharField(max_length=100)
    saida = models.BooleanField(default=False)

    def __unicode__(self):
        return u"{}".format(self.estoque)

    class Meta:
        verbose_name = u"Estoque".encode('utf-8')
        verbose_name_plural = u"Produtos - Estoques".encode('utf-8')
        ordering = ['estoque']

    class Admin(admin.ModelAdmin):
        list_display = ['estoque', 'saida']
        search_fields = ['estoque']
        list_filter = ['saida']


class Produto(models.Model):
    codigo_sistema = models.CharField(max_length=30, blank=True, null=True)
    produto = models.CharField(max_length=100)
    subgrupo = models.ForeignKey(ProdutoSubGrupo, blank=True, null=True)
    unidade = models.ForeignKey(ProdutoUnidade, blank=True, null=True)
    estoque_venda = models.ForeignKey(ProdutoEstoque, blank=True, null=True)
    controle_estoque = models.BooleanField(default=True)

    @staticmethod
    def autocomplete_search_fields():
        return ["codigo_sistema__icontains", "produto__icontains", ]

    def grupo(self):
        return self.subgrupo.grupo if self.subgrupo else None

    def __unicode__(self):
        return u"{} - {} ({})".format(self.codigo_sistema or self.id, self.produto, self.unidade)

    class Meta:
        verbose_name = u"Produto".encode('utf-8')
        verbose_name_plural = u"Produtos".encode('utf-8')
        ordering = ['subgrupo__grupo__grupo', 'subgrupo__subgrupo', 'produto']

    class Admin(admin.ModelAdmin):
        list_display = ['__unicode__', 'grupo', 'subgrupo']
        search_fields = ['codigo_sistema', 'produto']
        list_filter = ['subgrupo__grupo', 'subgrupo', 'unidade', 'estoque_venda', 'controle_estoque']


class CompraItem(models.Model):
    compra = models.ForeignKey(Compra)
    produto = models.ForeignKey(Produto)
    qtd = models.DecimalField(decimal_places=2, max_digits=18)
    preco = models.DecimalField(decimal_places=2, max_digits=18)
    total = models.DecimalField(decimal_places=2, max_digits=18, default=0)
    estoque = models.ForeignKey(ProdutoEstoque, default=1)

    def __unicode__(self):
        return u"{} - {} - Qtd: {} {} Total: {}".format(self.compra, self.produto, self.qtd, valor(self.preco),
                                                        valor(self.total))

    class Meta:
        verbose_name = u"Item".encode('utf-8')
        verbose_name_plural = u"Compras - Itens".encode('utf-8')
        ordering = ['-compra__data_recebimento', 'compra__fornecedor', 'compra__nf', 'id']

    class Admin(admin.ModelAdmin):
        fields = ['compra',
                  'produto',
                  ('qtd', 'preco', 'total'),
                  'estoque', ]
        raw_id_fields = ['produto', 'compra']
        autocomplete_lookup_fields = {
            'fk': ['produto', 'compra'],
        }
        readonly_fields = ['total']
        list_display = ['compra', 'produto', 'qtd', 'preco', 'total', 'estoque', ]
        search_fields = ['compra__nf', 'produto__produto', ]
        list_filter = ['compra__fornecedor', 'estoque', ]

    def save(self, *args, **kwargs):
        self.total = self.qtd * self.preco
        super(CompraItem, self).save(*args, **kwargs)


class CupomItem(models.Model):
    cupom = models.ForeignKey(Cupom)
    sequencial = models.IntegerField()
    produto = models.ForeignKey(Produto)
    qtd = models.DecimalField(decimal_places=2, max_digits=18)
    preco = models.DecimalField(decimal_places=2, max_digits=18)
    total = models.DecimalField(decimal_places=2, max_digits=18, default=0)

    def __unicode__(self):
        return u"{} - {} - {} - Qtd: {} {} Total: {}".format(self.cupom, self.sequencial, self.produto, self.qtd,
                                                             valor(self.preco),
                                                             valor(self.total))

    class Meta:
        verbose_name = u"Item".encode('utf-8')
        verbose_name_plural = u"Cupons - Itens".encode('utf-8')
        ordering = ['-cupom__ccf', 'sequencial', 'produto__produto', ]

    class Admin(admin.ModelAdmin):
        list_display = ['cupom', 'sequencial', 'produto', 'qtd', 'preco', 'total', ]
        readonly_fields = list_display[:]
        search_fields = ['cupom__ccf', 'produto__produto', ]
        list_filter = ['produto', ]

        # def save(self, *args, **kwargs):
        # self.total = self.qtd * self.preco
        # super(CompraItem, self).save(*args, **kwargs)


class CupomImportacao(models.Model):
    data = models.DateTimeField(auto_now_add=True)
    data_alteracao = models.DateTimeField(auto_now=True)
    arquivo = models.FileField(upload_to='cupons_importacao/', verbose_name=u"Arquivo", blank=True, null=True)

    def __unicode__(self):
        return u"{:%d/%m/%y %H:%M} {}".format(self.data, self.arquivo)

    class Meta:
        verbose_name = u"Arquivo".encode('utf-8')
        verbose_name_plural = u"Cupons - Importação".encode('utf-8')
        ordering = ['-data']

    class Admin(admin.ModelAdmin):
        list_display = ['data', 'data_alteracao', 'arquivo', ]
        date_hierarchy = 'data'

    def save(self, *args, **kwargs):
        # criado = (True if self.id else False)
        super(CupomImportacao, self).save(*args, **kwargs)
        linha = 0
        linha_geral = 0
        parte_produtos = False
        item_id = None
        item_cod = None
        item_total = None
        item_preco = None
        item_qtd = None
        item_produto = None
        check = None
        for l in self.arquivo.readlines():
            linha_geral += 1
            linha += 1
            if l == '                      OSTERIA LTDA                      \n':
                linha = 1
            if linha == 11:
                data_dia = int(l[:2])
                data_mes = int(l[3:5])
                data_ano = int(l[6:10])
                data_hora = int(l[11:13])
                data_minuto = int(l[14:16])
                data_segundo = int(l[17:19])
                cupom_ccf = int(l[25:31])
                cupom_coo = int(l[50:56])
                try:
                    c = Cupom.objects.get(ccf=cupom_ccf)
                    c.coo = cupom_coo
                    c.data = local_timezone.localize(datetime.datetime(day=data_dia,
                                                                       month=data_mes,
                                                                       year=data_ano,
                                                                       hour=data_hora,
                                                                       minute=data_minuto,
                                                                       second=data_segundo))
                    c.importado = True
                    c.save()

                except Cupom.DoesNotExist:
                    # TODO MANDAR EMAIL - NOTIFICAR
                    c = Cupom(ccf=cupom_ccf,
                              coo=cupom_coo,
                              importado=True,
                              data=local_timezone.localize(datetime.datetime(day=data_dia,
                                                                             month=data_mes,
                                                                             year=data_ano,
                                                                             hour=data_hora,
                                                                             minute=data_minuto,
                                                                             second=data_segundo))
                              )
                    c.save()
                c.cupomitem_set.all().delete()
            if l[:6] == 'Mesa :':
                c.mesa = int(str(l[7:]).replace('\n', ''))
                c.save()
            if l[:11] == 'SUBTOTAL R$':
                c.subtotal = Decimal(str(l[12:]).replace(',', '.').replace('\n', ''))
                c.save()
            if l[:10] == '  DESCONTO':
                c.desconto = Decimal(str(l[11:]).replace(',', '.').replace('\n', ''))
                c.save()
            if l[:8] == 'TOTAL R$':
                c.total = Decimal(str(l[9:]).replace(',', '.').replace('\n', ''))
                c.save()
            if l == '                 CUPOM FISCAL CANCELADO                 \n':
                c.cancelado = True
                c.save()
            if linha == 16:
                parte_produtos = True
            if l == '                                          --------------\n':
                parte_produtos = False
            if parte_produtos:
                pos_x = str(l[::-1]).find('X')
                pos_ta = str(l[::-1]).find('aT')
                pos_ta = None if pos_ta == -1 else pos_ta
                pos_l1 = str(l[::-1]).find('1I')
                pos_l1 = None if pos_l1 == -1 else pos_l1
                pos_div = pos_ta or pos_l1
                pos_cod = str(l[4:]).find(' ')
                item_id = item_id
                item_cod = item_cod
                item_total = item_total
                item_preco = item_preco
                item_qtd = item_qtd
                item_produto = item_produto
                check = check
                if l[:3] != '   ':
                    item_id = int(l[:3])
                    item_cod = l[4:pos_cod + 4]
                    if pos_x != -1:
                        item_produto = str(l[pos_cod + 4:57 - pos_x - 5]).strip().replace('\xe2\x82\xac', 'C')
                    else:
                        item_produto = str(l[pos_cod + 4:len(l) - 1]).strip().replace('\xe2\x82\xac', 'C')
                    if l[-2:] == '#\n':
                        item_qtd = int(re.sub('[a-z;A-Z; ]', '', l[-pos_x - 6:-pos_x]))
                        item_preco = Decimal(re.sub('[a-z;A-Z; ]', '', l[-pos_x:-pos_div - 2]).replace(',', '.'))
                        item_total = Decimal(str(l[-pos_div:]).replace('#\n', '').replace(' ', '').replace(',', '.'))
                        check = True if (item_qtd * item_preco) == item_total else False
                        print "{:2} - {:6} - {:2} - {:7} - {:7} - {}".format(item_id, item_cod, item_qtd, item_preco,
                                                                             item_total, check)
                        p = None
                        try:
                            p = Produto.objects.get(codigo_sistema=item_cod)
                        except Produto.DoesNotExist:
                            p = Produto(codigo_sistema=item_cod,
                                        produto=item_produto,
                                        unidade=ProdutoUnidade.objects.get(unidade='Un'),
                                        controle_estoque=False)
                            with transaction.atomic():
                                p.save()
                        finally:
                            i = CupomItem(cupom=c,
                                          sequencial=item_id,
                                          produto=p,
                                          qtd=item_qtd,
                                          preco=item_preco,
                                          total=item_total)
                            with transaction.atomic():
                                i.save()
                        item_id = None
                        item_cod = None
                        item_qtd = None
                        item_preco = None
                        item_total = None
                        check = None
                else:
                    item_qtd = int(l[:5])
                    item_preco = Decimal(re.sub('[a-z;A-Z; ]', '', l[-pos_x:-pos_div - 2]).replace(',', '.'))
                    item_total = Decimal(str(l[-pos_div:]).replace('#\n', '').replace(' ', '').replace(',', '.'))
                    check = True if (item_qtd * item_preco) == item_total else False
                    print "{:2} - {:6} - {:2} - {:7} - {:7} - {}".format(item_id, item_cod, item_qtd, item_preco,
                                                                         item_total, check)
                    p = None
                    try:
                        p = Produto.objects.get(codigo_sistema=item_cod)
                    except Produto.DoesNotExist:
                        p = Produto(codigo_sistema=item_cod,
                                    produto=item_produto,
                                    unidade=ProdutoUnidade.objects.get(unidade='Un'),
                                    controle_estoque=False)
                        with transaction.atomic():
                            p.save()
                    finally:
                        i = CupomItem(cupom=c,
                                      sequencial=item_id,
                                      produto=p,
                                      qtd=item_qtd,
                                      preco=item_preco,
                                      total=item_total)
                        with transaction.atomic():
                            i.save()
                    item_id = None
                    item_cod = None
                    item_qtd = None
                    item_preco = None
                    item_total = None
                    check = None