from django.db import models


class Proveedor(models.Model):
    cedula_juridica = models.CharField(max_length=25, unique=True)
    nombre = models.CharField(max_length=120)
    contacto = models.CharField(max_length=120)

    def __str__(self):
        return self.nombre