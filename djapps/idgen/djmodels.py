
from django.db import models
import datetime, constants

class IDGenerator(models.Model):
    """
    Generates unique IDs over a particular domain.
    """

    # Name of the Generator
    name            =   models.CharField(max_length = 32, primary_key = True)

    # Type of generator to be used.
    # different types can have different computational modes
    gen_type        =   models.CharField(max_length = 256, default = "lfsr") 

    # characters allowed in each key
    # cannot have more than 256 characters.
    allowed_chars   =   models.CharField(max_length = 256, default = constants.DIGITS)

    # Number of characters in the generated key
    # The number of bits would be ceil(log2(allowed_chars ^ key_length))
    key_length      =   models.IntegerField(default = 8)

    class Meta:
        verbose_name = "ID Generator"

class GeneratedID(models.Model):
    """
    Stores a generated ID.
    This provides an easy way to test out our generator.
    """
    generator   = models.ForeignKey(IDGenerator)
    gen_id      = models.CharField(max_length = 100)

    class Meta:
        unique_together = (("generator", "gen_id"),)
        ordering = ("generator","gen_id")
        verbose_name = "Generated ID"

class IDGeneratorSerial(models.Model):
    """
    An ID generator that simply generates serial IDs and checks the DB for
    collissions.  Not optimal but good for now.
    """
    generator   = models.ForeignKey(IDGenerator)

    def __str__(self):
        return str(generator)

    class Meta:
        verbose_name = "Serial ID Generator"

class IDGeneratorRandom(models.Model):
    """
    An ID generator that simply generates random IDs and checks the DB for
    collissions.  Not optimal but good for now.
    """
    generator   = models.ForeignKey(IDGenerator)

    def __str__(self):
        return str(generator)

    class Meta:
        verbose_name = "Random ID Generator"

class IDGeneratorLFSR(models.Model):
    """
    An ID generator that simply generates random IDs and checks the DB for
    collissions.  Not optimal but good for now.
    """
    generator   = models.ForeignKey(IDGenerator)

    def __str__(self):
        return str(generator) + ", Seed: " + self.seed

    # Rolling seed for the generator
    seed        =   models.CharField(max_length = 256)

    # Tap bits which are taken in each step to calculate the input bit for
    # the next seed
    tap_bits    = models.CharField(max_length = 256)

    class Meta:
        verbose_name = "LFSR ID Generator"
        verbose_name_plural = "LFSR ID Generators"

