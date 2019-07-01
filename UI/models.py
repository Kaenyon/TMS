from __future__ import unicode_literals
from django.db import models

import json

# Create your models here.
class Traffic(models.Model):
    unixtime = models.IntegerField()
    length = models.IntegerField()
    protocol = models.CharField(max_length=16)
    src_port = models.IntegerField()
    dst_port = models.IntegerField()
    src_ip = models.CharField(max_length=39)
    dst_ip = models.CharField(max_length=39)
    sni = models.CharField(max_length=64)

    def __unicode__(self):
        return u'%d %d %s %d %d %s %s %s' % (self.unixtime, self.length, self.protocol, self.src_port, self.dst_port, self.src_ip, self.dst_ip, self.sni)

class SalesRecord(models.Model):
	Region = models.CharField(max_length=100)
	Country = models.CharField(max_length=50)
	City = models.CharField(max_length=50)
	TotalSales = models.IntegerField()

	def __unicode__(self):
		return u'%s %s %s %s' % (self.Region, self.Country, self.City, self.TotalSales)
