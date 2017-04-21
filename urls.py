# -*- coding: utf-8 -*-
from django.conf.urls import url, include
from aldryn_django.utils import i18n_patterns
import aldryn_addons.urls
from django.views.decorators.csrf import csrf_exempt

from schema import schema
import graphene_django.views
import views
# from views import GraphQLView

urlpatterns = [
    # add your own patterns here
    url(r'^api/', include('timelapse_manager.api_urls')),
    # FIXME: should not be csrf_exempt.
    # see http://stackoverflow.com/questions/32618424/where-do-you-put-the-csrf-token-in-relay-graphql
    # for instructions on how to pass the token from relay

    # url(r'^graphql', csrf_exempt(views.GraphQLView.as_view(schema=schema))),
    url(r'^graphql', graphene_django.views.GraphQLView.as_view(graphiql=True)),
] + aldryn_addons.urls.patterns() + i18n_patterns(
    # add your own i18n patterns here
    *aldryn_addons.urls.i18n_patterns()  # MUST be the last entry!
)
