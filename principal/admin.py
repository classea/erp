from django.db import ProgrammingError
from django.contrib.contenttypes.models import ContentType
from django.forms.models import modelform_factory, ModelForm

from models import *


class RecebimentoCartaoInline(admin.StackedInline):
    model = RecebimentoCartao
    extra = 0
    inline_classes = ('grp-collapse grp-open',)
    fields = [('cartao', 'digitos',), ('doc', 'autorizacao',), 'total']
    form = modelform_factory(RecebimentoCartao, fields=('__all__'), localized_fields=('__all__'))


class RecebimentoDinheiroInline(admin.TabularInline):
    model = RecebimentoDinheiro
    extra = 0
    fields = ['total']
    form = modelform_factory(RecebimentoDinheiro, fields=('__all__'), localized_fields=('__all__'))


class RecebimentoChequeInline(admin.StackedInline):
    model = RecebimentoCheque
    extra = 0
    inline_classes = ('grp-collapse grp-open',)
    fields = [('total', 'banco',), ('agencia', 'dv_agencia',), ('cc', 'dv_cc',), ]
    form = modelform_factory(RecebimentoCheque, fields=('__all__'), localized_fields=('__all__'))


class CupomUnimedInline(admin.TabularInline):
    model = CupomUnimed
    extra = 0
    inline_classes = ('grp-collapse grp-open',)
    fields = ['codigo']
    form = modelform_factory(CupomUnimed, fields=('__all__'), localized_fields=('__all__'))


class RecebimentoOutrosInline(admin.TabularInline):
    model = RecebimentoOutros
    extra = 0
    fields = ['obs', 'total']
    form = modelform_factory(RecebimentoOutros, fields=('__all__'), localized_fields=('__all__'))


class CupomItemInline(admin.TabularInline):
    model = CupomItem
    extra = 0
    max_num = 0
    fields = ['sequencial', 'produto', 'qtd', 'preco', 'total']
    readonly_fields = fields[:]
    form = modelform_factory(CupomItem, fields=('__all__'), localized_fields=('__all__'))


CupomNovo.Admin.inlines = [RecebimentoCartaoInline,
                           RecebimentoDinheiroInline,
                           RecebimentoChequeInline,
                           CupomUnimedInline,
                           RecebimentoOutrosInline]

Cupom.Admin.inlines = [CupomItemInline,
                       RecebimentoCartaoInline,
                       RecebimentoDinheiroInline,
                       RecebimentoChequeInline,
                       CupomUnimedInline,
                       RecebimentoOutrosInline]


class CompraItemInline(admin.TabularInline):
    model = CompraItem
    extra = 10
    raw_id_fields = ['produto']
    autocomplete_lookup_fields = {
        'fk': ['produto'],
        # 'm2m': ['pedidos'],
    }
    fields = ['produto', 'qtd', 'preco', 'estoque', 'total', ]
    readonly_fields = ['total']
    form = modelform_factory(CompraItem, fields=('__all__'), localized_fields=('__all__'))


class CompraParcelaInline(admin.TabularInline):
    model = CompraParcela
    extra = 1
    fields = ['data_vencimento', 'valor', ]
    form = modelform_factory(CompraParcela, fields=('__all__'), localized_fields=('__all__'))


Compra.Admin.inlines = [CompraParcelaInline, CompraItemInline]

try:
    for c in ContentType.objects.filter(app_label='principal').all():
        cl = c.model_class()
        # print cl
        if cl:
            exec "{0}.Admin.form = modelform_factory({0}, fields=('__all__'), exclude=(), localized_fields=('__all__'))\n" \
                .format(cl.__name__)
            exec "admin.site.register({0}, {0}.Admin)\n".format(cl.__name__)
except ProgrammingError:
    pass


class EmpresaForm(ModelForm):
    def clean(self):
        cleaned_data = super(EmpresaForm, self).clean()
        operador_caixa = cleaned_data.get("operador_caixa")
        conta_caixa = cleaned_data.get("conta_caixa")
        if operador_caixa and not conta_caixa:
            erro = u"Favor selecionar uma conta caixa caso tenha selecionado um operador."
            self.add_error('conta_caixa', erro)

    class Meta:
        model = Empresa
        fields = '__all__'
        exclude = ()
        localized_fields = '__all__'


Empresa.Admin.form = EmpresaForm
