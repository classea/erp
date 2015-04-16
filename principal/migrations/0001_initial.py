# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings

import funcoes


# noinspection PySetFunctionToLiteral
class Migration(migrations.Migration):
    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Compra',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nf', models.CharField(max_length=30)),
                ('data_emissao', models.DateField(default=funcoes.hoje)),
                ('data_recebimento', models.DateField(default=funcoes.hoje)),
                ('desconto', models.DecimalField(default=0, max_digits=18, decimal_places=2)),
                ('valor_extra', models.DecimalField(default=0, max_digits=18, decimal_places=2)),
            ],
            options={
                'ordering': ['-data_recebimento', 'fornecedor', 'nf'],
                'verbose_name': 'Compra',
                'verbose_name_plural': 'Compras',
            },
        ),
        migrations.CreateModel(
            name='CompraItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('qtd', models.DecimalField(max_digits=18, decimal_places=2)),
                ('preco', models.DecimalField(max_digits=18, decimal_places=2)),
                ('total', models.DecimalField(default=0, max_digits=18, decimal_places=2)),
                ('compra', models.ForeignKey(to='principal.Compra')),
            ],
            options={
                'ordering': ['-compra__data_recebimento', 'compra__fornecedor', 'compra__nf', 'id'],
                'verbose_name': 'Item',
                'verbose_name_plural': 'Compras - Itens',
            },
        ),
        migrations.CreateModel(
            name='CompraParcela',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('data_vencimento', models.DateField()),
                ('valor', models.DecimalField(max_digits=18, decimal_places=2)),
                ('compra', models.ForeignKey(to='principal.Compra')),
            ],
            options={
                'ordering': ['-data_vencimento'],
                'verbose_name': 'Parcela',
                'verbose_name_plural': 'Compras - Parcelas',
            },
        ),
        migrations.CreateModel(
            name='Conta',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('data_criacao', models.DateTimeField(auto_now_add=True, verbose_name='Data Cria\xe7\xe3o')),
                ('data_alteracao', models.DateTimeField(auto_now=True, verbose_name='Data Altera\xe7\xe3o')),
                ('conta', models.CharField(max_length=100)),
                ('cartao', models.BooleanField(default=False)),
                ('abr', models.CharField(max_length=3)),
            ],
            options={
                'ordering': ['conta'],
                'verbose_name': 'Conta Financeira',
                'verbose_name_plural': 'Contas Financeiras',
            },
        ),
        migrations.CreateModel(
            name='Cupom',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ccf', models.BigIntegerField(unique=True)),
                ('coo', models.BigIntegerField(unique=True, null=True, blank=True)),
                ('data', models.DateTimeField(null=True, blank=True)),
                ('mesa', models.IntegerField(null=True, blank=True)),
                ('subtotal', models.DecimalField(default=0, max_digits=18, decimal_places=2)),
                ('desconto', models.DecimalField(default=0, max_digits=18, decimal_places=2)),
                ('total', models.DecimalField(default=0, max_digits=18, decimal_places=2)),
                ('cancelado', models.BooleanField(default=False)),
                ('qtd_belvitur', models.IntegerField(default=0)),
                ('importado', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ['cupomnovo__turno', 'ccf'],
                'verbose_name': 'Cupom',
                'verbose_name_plural': 'Cupons',
            },
        ),
        migrations.CreateModel(
            name='CupomImportacao',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('data', models.DateTimeField(auto_now_add=True)),
                ('data_alteracao', models.DateTimeField(auto_now=True)),
                ('arquivo',
                 models.FileField(upload_to=b'cupons_importacao/', null=True, verbose_name='Arquivo', blank=True)),
            ],
            options={
                'ordering': ['-data'],
                'verbose_name': 'Arquivo',
                'verbose_name_plural': 'Cupons - Importa\xe7\xe3o',
            },
        ),
        migrations.CreateModel(
            name='CupomItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sequencial', models.IntegerField()),
                ('qtd', models.DecimalField(max_digits=18, decimal_places=2)),
                ('preco', models.DecimalField(max_digits=18, decimal_places=2)),
                ('total', models.DecimalField(default=0, max_digits=18, decimal_places=2)),
            ],
            options={
                'ordering': ['-cupom__ccf', 'sequencial', 'produto__produto'],
                'verbose_name': 'Item',
                'verbose_name_plural': 'Cupons - Itens',
            },
        ),
        migrations.CreateModel(
            name='CupomUnimed',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('codigo', models.CharField(max_length=100)),
            ],
            options={
                'verbose_name': 'Cupom Unimed',
                'verbose_name_plural': 'Cupons Unimed',
            },
        ),
        migrations.CreateModel(
            name='Diretoria',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nome', models.CharField(max_length=100)),
                ('conta', models.ForeignKey(to='principal.Conta')),
            ],
            options={
                'ordering': ['nome'],
                'verbose_name': 'Diretor',
                'verbose_name_plural': 'Diretoria',
            },
        ),
        migrations.CreateModel(
            name='Empresa',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('data_criacao', models.DateTimeField(auto_now_add=True, verbose_name='Data Cria\xe7\xe3o')),
                ('data_alteracao', models.DateTimeField(auto_now=True, verbose_name='Data Altera\xe7\xe3o')),
                ('empresa', models.EmailField(max_length=100)),
                ('abr', models.CharField(max_length=3)),
                ('conta_caixa',
                 models.ForeignKey(related_name='empresa_conta_caixa', blank=True, to='principal.Conta', null=True)),
                ('operador_caixa',
                 models.OneToOneField(related_name='empresa_operador_caixa', to=settings.AUTH_USER_MODEL)),
                ('usuarios', models.ManyToManyField(related_name='empresa_ususarios', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['empresa'],
                'verbose_name': 'Empresa',
                'verbose_name_plural': 'Empresas',
            },
        ),
        migrations.CreateModel(
            name='FinanceiroGrupo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('data_criacao', models.DateTimeField(auto_now_add=True, verbose_name='Data Cria\xe7\xe3o')),
                ('data_alteracao', models.DateTimeField(auto_now=True, verbose_name='Data Altera\xe7\xe3o')),
                ('grupo', models.CharField(max_length=50)),
                ('abr', models.CharField(max_length=10)),
                ('empresas', models.ManyToManyField(to='principal.Empresa')),
            ],
            options={
                'ordering': ['grupo'],
                'verbose_name': 'Grupo Financeiro',
                'verbose_name_plural': 'Grupos Financeiros',
            },
        ),
        migrations.CreateModel(
            name='FinanceiroSubGrupo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('data_criacao', models.DateTimeField(auto_now_add=True, verbose_name='Data Cria\xe7\xe3o')),
                ('data_alteracao', models.DateTimeField(auto_now=True, verbose_name='Data Altera\xe7\xe3o')),
                ('subgrupo', models.CharField(max_length=50, verbose_name='SubGrupo')),
                ('abr', models.CharField(max_length=10, verbose_name='Abrevia\xe7\xe3o')),
                ('classes', models.ManyToManyField(to='contenttypes.ContentType', verbose_name='Classes')),
                ('empresas', models.ManyToManyField(to='principal.Empresa', verbose_name='Empresas')),
                ('grupo', models.ForeignKey(verbose_name='Grupo', to='principal.FinanceiroGrupo')),
            ],
            options={
                'ordering': ['grupo__grupo', 'subgrupo'],
                'verbose_name': 'SubGrupo Financeiro',
                'verbose_name_plural': 'SubGrupos Financeiros',
            },
        ),
        migrations.CreateModel(
            name='Fornecedor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('fornecedor', models.CharField(max_length=100)),
                ('razao_social', models.CharField(max_length=200)),
                ('cnpj', models.CharField(help_text='Sem pontos ou tra\xe7os.', max_length=14)),
                ('contato', models.CharField(max_length=100, null=True, blank=True)),
                ('telefone_ddd', models.DecimalField(null=True, max_digits=2, decimal_places=0, blank=True)),
                ('telefone', models.DecimalField(null=True, max_digits=9, decimal_places=0, blank=True)),
                ('endereco', models.TextField(null=True, blank=True)),
            ],
            options={
                'ordering': ['fornecedor'],
                'verbose_name': 'Fornecedor',
                'verbose_name_plural': 'Fornecedores',
            },
        ),
        migrations.CreateModel(
            name='Funcionario',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('data_admissao', models.DateField()),
                ('data_demissao', models.DateField(null=True, blank=True)),
                ('nome', models.CharField(max_length=100)),
                ('segundo_nome', models.CharField(max_length=150)),
                ('sobrenome', models.CharField(max_length=150)),
                ('nome_pai', models.CharField(max_length=100)),
            ],
            options={
                'ordering': ['nome'],
                'verbose_name': 'Funcion\xe1rio',
                'verbose_name_plural': 'Funcion\xe1rios',
            },
        ),
        migrations.CreateModel(
            name='Lancamento',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('data_criacao', models.DateTimeField(auto_now_add=True, verbose_name='Data Cria\xe7\xe3o')),
                ('data_alteracao', models.DateTimeField(auto_now=True, verbose_name='Data Altera\xe7\xe3o')),
                ('data', models.DateField(default=funcoes.hoje, verbose_name='Data')),
                ('descricao', models.CharField(max_length=150, verbose_name='Descri\xe7\xe3o')),
                ('valor', models.DecimalField(verbose_name='Valor', editable=False, max_digits=18, decimal_places=2)),
                ('total', models.DecimalField(verbose_name='Valor', max_digits=18, decimal_places=2)),
            ],
            options={
                'ordering': ['-data', 'conta__conta', 'subgrupo__grupo__grupo', 'subgrupo__subgrupo', 'total'],
                'verbose_name': 'Lancamento Financeiro',
                'verbose_name_plural': 'Lancamentos Financeiros',
            },
        ),
        migrations.CreateModel(
            name='Produto',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('codigo_sistema', models.CharField(max_length=30, null=True, blank=True)),
                ('produto', models.CharField(max_length=100)),
                ('controle_estoque', models.BooleanField(default=True)),
            ],
            options={
                'ordering': ['subgrupo__grupo__grupo', 'subgrupo__subgrupo', 'produto'],
                'verbose_name': 'Produto',
                'verbose_name_plural': 'Produtos',
            },
        ),
        migrations.CreateModel(
            name='ProdutoEstoque',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('estoque', models.CharField(max_length=100)),
                ('saida', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ['estoque'],
                'verbose_name': 'Estoque',
                'verbose_name_plural': 'Produtos - Estoques',
            },
        ),
        migrations.CreateModel(
            name='ProdutoGrupo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('grupo', models.CharField(max_length=100)),
            ],
            options={
                'ordering': ['grupo'],
                'verbose_name': 'Grupo',
                'verbose_name_plural': 'Produtos - Grupos',
            },
        ),
        migrations.CreateModel(
            name='ProdutoSubGrupo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('subgrupo', models.CharField(max_length=100)),
                ('grupo', models.ForeignKey(to='principal.ProdutoGrupo')),
            ],
            options={
                'ordering': ['grupo__grupo', 'subgrupo'],
                'verbose_name': 'SubGrupo',
                'verbose_name_plural': 'Produtos - SubGrupos',
            },
        ),
        migrations.CreateModel(
            name='ProdutoUnidade',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('unidade', models.CharField(max_length=2)),
            ],
            options={
                'ordering': ['unidade'],
                'verbose_name': 'Unidade',
                'verbose_name_plural': 'Produtos - Unidades',
            },
        ),
        migrations.CreateModel(
            name='Recorrencia',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('data_criacao', models.DateTimeField(auto_now_add=True, verbose_name='Data Cria\xe7\xe3o')),
                ('data_alteracao', models.DateTimeField(auto_now=True, verbose_name='Data Altera\xe7\xe3o')),
                ('descricao', models.CharField(max_length=100, verbose_name='Descri\xe7\xe3o')),
                ('tipo', models.IntegerField(default=2, verbose_name='Tempo',
                                             choices=[(0, 'Diariamente'), (1, 'Semanalmente'), (2, 'Mensalmente'),
                                                      (3, 'Anualmente'), (4, 'Dia do M\xeas'), (5, 'Dia do Ano')])),
                ('qtd', models.IntegerField(default=1, verbose_name='A cada / Dia do M\xeas')),
                ('dia_ano', models.IntegerField(null=True, verbose_name='Dia Ano', blank=True)),
                ('mes_ano', models.IntegerField(blank=True, null=True, verbose_name='M\xeas Ano',
                                                choices=[(1, 'Janeiro'), (2, 'Fevereiro'), (3, 'Mar\xe7o'),
                                                         (4, 'Abril'), (5, 'Maio'), (6, 'Junho'), (7, 'Julho'),
                                                         (8, 'Agosto'), (9, 'Setembro'), (10, 'Outubro'),
                                                         (11, 'Novembro'), (12, 'Dezembro')])),
                ('segunda', models.BooleanField(default=True)),
                ('terca', models.BooleanField(default=True)),
                ('quarta', models.BooleanField(default=True)),
                ('quinta', models.BooleanField(default=True)),
                ('sexta', models.BooleanField(default=True)),
                ('sabado', models.BooleanField(default=True)),
                ('domingo', models.BooleanField(default=True)),
            ],
            options={
                'ordering': ['descricao'],
                'verbose_name': 'Recorr\xeancia',
                'verbose_name_plural': 'Recorr\xeancias',
            },
        ),
        migrations.CreateModel(
            name='Setor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('setor', models.CharField(max_length=100)),
            ],
            options={
                'ordering': ['setor'],
                'verbose_name': 'Setor',
                'verbose_name_plural': 'Setores',
            },
        ),
        migrations.CreateModel(
            name='TesteRecorrencia',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('data_criacao', models.DateTimeField(auto_now_add=True, verbose_name='Data Cria\xe7\xe3o')),
                ('data_alteracao', models.DateTimeField(auto_now=True, verbose_name='Data Altera\xe7\xe3o')),
                ('inicio', models.DateField()),
                ('numero', models.IntegerField(default=20)),
                ('recorrencia', models.ForeignKey(to='principal.Recorrencia')),
            ],
            options={
                'ordering': ['inicio'],
                'verbose_name': 'Teste Recorr\xeancia',
                'verbose_name_plural': 'Recorr\xeancias - Teste',
            },
        ),
        migrations.CreateModel(
            name='TesteRecorrenciaItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('data_criacao', models.DateTimeField(auto_now_add=True, verbose_name='Data Cria\xe7\xe3o')),
                ('data_alteracao', models.DateTimeField(auto_now=True, verbose_name='Data Altera\xe7\xe3o')),
                ('item', models.IntegerField()),
                ('data', models.DateField()),
                ('teste', models.ForeignKey(to='principal.TesteRecorrencia')),
            ],
            options={
                'ordering': ['teste', 'item', 'data'],
                'verbose_name': 'Item Teste Recorr\xeancia',
                'verbose_name_plural': 'Recorr\xeancias - Teste - Item',
            },
        ),
        migrations.CreateModel(
            name='Transferencia',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('data_criacao', models.DateTimeField(auto_now_add=True, verbose_name='Data Cria\xe7\xe3o')),
                ('data_alteracao', models.DateTimeField(auto_now=True, verbose_name='Data Altera\xe7\xe3o')),
                ('data', models.DateField(default=funcoes.hoje, verbose_name='Data')),
                ('descricao', models.CharField(max_length=150, verbose_name='Descri\xe7\xe3o')),
                ('total', models.DecimalField(verbose_name='Valor', max_digits=18, decimal_places=2)),
                ('conta_de', models.ForeignKey(related_name='transferencia_conta_de', verbose_name='Conta Sa\xedda',
                                               to='principal.Conta')),
                ('conta_para', models.ForeignKey(related_name='transferencia_conta_para', verbose_name='Conta Entrada',
                                                 to='principal.Conta')),
            ],
            options={
                'ordering': ['-data', 'conta_de__conta', 'conta_para__conta', 'total'],
                'verbose_name': 'Transfer\xeancia Financeira',
                'verbose_name_plural': 'Transfer\xeancias Financeiras',
            },
        ),
        migrations.CreateModel(
            name='Turno',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('data', models.DateField(default=funcoes.hoje)),
                ('turno', models.IntegerField(choices=[(0, 'Jantar'), (1, 'Almo\xe7o'), (2, 'Extra')])),
                ('aberto', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ['-data', '-turno'],
                'verbose_name': 'Turno',
                'verbose_name_plural': 'Turnos',
            },
        ),
        migrations.CreateModel(
            name='CupomNovo',
            fields=[
                ('cupom_ptr',
                 models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False,
                                      to='principal.Cupom')),
            ],
            options={
                'ordering': ['turno', 'ccf'],
                'verbose_name': 'Cupom',
                'verbose_name_plural': 'Caixa - Cupons',
            },
            bases=('principal.cupom',),
        ),
        migrations.CreateModel(
            name='Despesa',
            fields=[
                ('lancamento_ptr',
                 models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False,
                                      to='principal.Lancamento')),
            ],
            options={
                'ordering': ['-data', 'conta', '-valor'],
                'verbose_name': 'Despesa',
                'verbose_name_plural': 'Despesas',
            },
            bases=('principal.lancamento',),
        ),
        migrations.CreateModel(
            name='PagamentoCompra',
            fields=[
                ('lancamento_ptr',
                 models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False,
                                      to='principal.Lancamento')),
                ('parcela', models.ForeignKey(to='principal.CompraParcela')),
            ],
            options={
                'ordering': ['-data', 'parcela__valor'],
                'verbose_name': 'Pagamento',
                'verbose_name_plural': 'Compras - Pagamentos',
            },
            bases=('principal.lancamento',),
        ),
        migrations.CreateModel(
            name='PagamentoFuncionario',
            fields=[
                ('lancamento_ptr',
                 models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False,
                                      to='principal.Lancamento')),
            ],
            options={
                'ordering': ['-data', 'conta', 'funcionario__nome'],
                'verbose_name': 'Pagamento Funcion\xe1rio',
                'verbose_name_plural': 'Funcion\xe1rios - Pagamentos',
            },
            bases=('principal.lancamento',),
        ),
        migrations.CreateModel(
            name='Recebimento',
            fields=[
                ('lancamento_ptr',
                 models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False,
                                      to='principal.Lancamento')),
                ('tipo', models.IntegerField(default=0, choices=[(0, 'Cart\xe3o'), (1, 'Dinheiro'), (2, 'Cheque'),
                                                                 (3, 'Outros')])),
            ],
            options={
                'ordering': ['-cupom__cupomnovo__turno__data', '-cupom__cupomnovo__turno', 'cupom__ccf', 'tipo',
                             'total'],
                'verbose_name': 'Recebimento',
                'verbose_name_plural': 'Recebimentos',
            },
            bases=('principal.lancamento',),
        ),
        migrations.AlterUniqueTogether(
            name='turno',
            unique_together=set([('data', 'turno')]),
        ),
        migrations.AddField(
            model_name='produto',
            name='estoque_venda',
            field=models.ForeignKey(blank=True, to='principal.ProdutoEstoque', null=True),
        ),
        migrations.AddField(
            model_name='produto',
            name='subgrupo',
            field=models.ForeignKey(blank=True, to='principal.ProdutoSubGrupo', null=True),
        ),
        migrations.AddField(
            model_name='produto',
            name='unidade',
            field=models.ForeignKey(blank=True, to='principal.ProdutoUnidade', null=True),
        ),
        migrations.AddField(
            model_name='lancamento',
            name='conta',
            field=models.ForeignKey(verbose_name='Conta', to='principal.Conta'),
        ),
        migrations.AddField(
            model_name='lancamento',
            name='subgrupo',
            field=models.ForeignKey(verbose_name='SubGrupo', to='principal.FinanceiroSubGrupo'),
        ),
        migrations.AddField(
            model_name='funcionario',
            name='setor',
            field=models.ForeignKey(to='principal.Setor'),
        ),
        migrations.AddField(
            model_name='cupomunimed',
            name='cupom',
            field=models.ForeignKey(to='principal.Cupom'),
        ),
        migrations.AddField(
            model_name='cupomitem',
            name='cupom',
            field=models.ForeignKey(to='principal.Cupom'),
        ),
        migrations.AddField(
            model_name='cupomitem',
            name='produto',
            field=models.ForeignKey(to='principal.Produto'),
        ),
        migrations.AddField(
            model_name='cupom',
            name='diretoria',
            field=models.ForeignKey(blank=True, to='principal.Diretoria', null=True),
        ),
        migrations.AddField(
            model_name='cupom',
            name='funcionario',
            field=models.ForeignKey(blank=True, to='principal.Funcionario', null=True),
        ),
        migrations.AddField(
            model_name='conta',
            name='empresa',
            field=models.ForeignKey(to='principal.Empresa'),
        ),
        migrations.AddField(
            model_name='compraitem',
            name='estoque',
            field=models.ForeignKey(default=1, to='principal.ProdutoEstoque'),
        ),
        migrations.AddField(
            model_name='compraitem',
            name='produto',
            field=models.ForeignKey(to='principal.Produto'),
        ),
        migrations.AddField(
            model_name='compra',
            name='fornecedor',
            field=models.ForeignKey(to='principal.Fornecedor'),
        ),
        migrations.CreateModel(
            name='DespesaCaixa',
            fields=[
                ('despesa_ptr',
                 models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False,
                                      to='principal.Despesa')),
                ('funcionario', models.ForeignKey(blank=True, to='principal.Funcionario', null=True)),
            ],
            options={
                'ordering': ['-data'],
                'verbose_name': 'Despesa',
                'verbose_name_plural': 'Caixa - Despesas',
            },
            bases=('principal.despesa',),
        ),
        migrations.CreateModel(
            name='RecebimentoCartao',
            fields=[
                ('recebimento_ptr',
                 models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False,
                                      to='principal.Recebimento')),
                ('digitos', models.CharField(max_length=4)),
                ('doc', models.CharField(max_length=100)),
                ('autorizacao', models.CharField(max_length=100)),
                ('cartao', models.ForeignKey(default=1, to='principal.Conta')),
            ],
            options={
                'ordering': ['-cupom__cupomnovo__turno__data', '-cupom__cupomnovo__turno', 'cupom__ccf',
                             'cartao__cartao', 'total'],
                'verbose_name': 'Recebimento Cart\xe3o',
                'verbose_name_plural': 'Recebimentos - Cart\xe3o',
            },
            bases=('principal.recebimento',),
        ),
        migrations.CreateModel(
            name='RecebimentoCheque',
            fields=[
                ('recebimento_ptr',
                 models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False,
                                      to='principal.Recebimento')),
                ('banco', models.CharField(max_length=3)),
                ('agencia', models.CharField(max_length=4)),
                ('dv_agencia', models.CharField(max_length=1)),
                ('cc', models.CharField(max_length=15)),
                ('dv_cc', models.CharField(max_length=1)),
            ],
            options={
                'ordering': ['-cupom__cupomnovo__turno__data', '-cupom__cupomnovo__turno', 'cupom__ccf', 'total'],
                'verbose_name': 'Recebimento Cheque',
                'verbose_name_plural': 'Recebimentos - Cheque',
            },
            bases=('principal.recebimento',),
        ),
        migrations.CreateModel(
            name='RecebimentoDinheiro',
            fields=[
                ('recebimento_ptr',
                 models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False,
                                      to='principal.Recebimento')),
            ],
            options={
                'ordering': ['-cupom__cupomnovo__turno__data', '-cupom__cupomnovo__turno', 'cupom__ccf', 'total'],
                'verbose_name': 'Recebimento Dinheiro',
                'verbose_name_plural': 'Recebimentos - Dinheiro',
            },
            bases=('principal.recebimento',),
        ),
        migrations.CreateModel(
            name='RecebimentoOutros',
            fields=[
                ('recebimento_ptr',
                 models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False,
                                      to='principal.Recebimento')),
                ('obs', models.TextField()),
            ],
            options={
                'ordering': ['-cupom__cupomnovo__turno__data', '-cupom__cupomnovo__turno', 'cupom__ccf', 'total'],
                'verbose_name': 'Recebimento Outro',
                'verbose_name_plural': 'Recebimentos - Outros',
            },
            bases=('principal.recebimento',),
        ),
        migrations.AddField(
            model_name='recebimento',
            name='cupom',
            field=models.ForeignKey(to='principal.Cupom'),
        ),
        migrations.AddField(
            model_name='pagamentofuncionario',
            name='funcionario',
            field=models.ForeignKey(to='principal.Funcionario'),
        ),
        migrations.AddField(
            model_name='cupomnovo',
            name='turno',
            field=models.ForeignKey(default=1, to='principal.Turno'),
        ),
    ]
