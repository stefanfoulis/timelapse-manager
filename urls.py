# -*- coding: utf-8 -*-
from django.conf.urls import url, include
from aldryn_django.utils import i18n_patterns
import aldryn_addons.urls
from django.views.decorators.csrf import csrf_exempt

import timelapse_manager.views

from schema import schema
from views import GraphQLView
from django_graphiql.views import GraphiQL

urlpatterns = [
    # add your own patterns here
    url(r'^api/', include('timelapse_manager.api_urls')),
    # FIXME: should not be csrf_exempt.
    # see http://stackoverflow.com/questions/32618424/where-do-you-put-the-csrf-token-in-relay-graphql
    # for instructions on how to pass the token from relay
    url(r'^graphql', csrf_exempt(GraphQLView.as_view(schema=schema))),
    url(r'^graphiql', GraphiQL.as_view()),
] + aldryn_addons.urls.patterns() + i18n_patterns(
    # add your own i18n patterns here
    *aldryn_addons.urls.i18n_patterns()  # MUST be the last entry!
)
