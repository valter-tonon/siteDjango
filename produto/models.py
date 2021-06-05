from django.conf import settings
from django.db import models
from PIL import Image
import os
from django.utils.text import slugify


# Create your models here.
class Produto(models.Model):
    nome = models.CharField(max_length=255)
    descricao_curta = models.TextField(max_length=255)
    descricao_longa = models.TextField()
    imagem = models.ImageField(
        upload_to='produto_imagens/%Y/%m/', blank=True, null=True
    )
    slug = models.SlugField(unique=True, null=True, blank=True)
    preco_marketing = models.FloatField(default=0, verbose_name='Preço')
    preco_marketing_promocional = models.FloatField(default=0, verbose_name='Preço Promo')
    tipo = models.CharField(
        default='V',
        max_length=1,
        choices=(
            ('V', 'Variável'),
            ('S', 'Simples'),
        )
    )

    def get_formatted_price(self):
        return f'R$ {self.preco_marketing:.2f}'.replace('.',',')
    get_formatted_price.short_description = 'Preço'

    def get_formatted_price_promo(self):
        return f'R$ {self.preco_marketing_promocional:.2f}'.replace('.', ',')
    get_formatted_price_promo.short_description = 'Preço Promo'


    @staticmethod
    def resize_image(img, new_width=800):
        img_full_path = os.path.join(settings.MEDIA_ROOT, img.name)
        img_pil = Image.open(img_full_path)
        original_wdth, original_height = img_pil.size

        if original_wdth <= new_width:
            img_pil.close()
            return

        new_height = round((new_width * original_height) / original_wdth)

        new_img = img_pil.resize((new_width, new_height), Image.LANCZOS)
        new_img.save(
            img_full_path,
            optmize=True,
            quality=50
        )
        print(img.name)

    def save(self, *args, **kwargs):
        if not self.slug:
            slug = f'{slugify(self.nome)}'
            self.slug = slug

        super().save(*args, **kwargs)

        max_image_size = 800

        if self.imagem:
            self.resize_image(self.imagem, max_image_size)

    def __str__(self):
        return self.nome


class Variacao(models.Model):
    nome = models.CharField(max_length=255, blank=True, null=True)
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    preco = models.FloatField(default=0)
    preco_promocional = models.FloatField(default=0)
    estoque = models.IntegerField(default=1)

    def __str__(self):
        return self.nome or self.produto.nome

    class Meta:
        verbose_name = 'Variação'
        verbose_name_plural = 'Variações'
