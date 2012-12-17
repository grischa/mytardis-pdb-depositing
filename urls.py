# -*- coding: utf-8 -*-
#
"""
urls.py

.. moduleauthor:: Grischa Meyer <grischa.meyer@monash.edu>

"""
from django.conf.urls.defaults import patterns

urlpatterns = patterns(
    'tardis.apps.pdb_depositing.views',
    (r'^view/(?P<dataset_file_id>\d+)/$', 'view'),
    (r'^download/(?P<dataset_file_id>\d+)/$', 'download'),
)
