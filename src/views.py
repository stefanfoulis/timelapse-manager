# -*- coding: utf-8 -*-
import django.core.exceptions
import graphql.error
import graphql_django_view
import rest_framework.exceptions
import six
from django.conf import settings
from graphene.contrib.django.views import GraphQLView as BaseGraphQLView
from graphene.utils import to_camel_case


def dict_keys_to_camel_case(data):
    return {to_camel_case(key): value for key, value in data.items()}


class GraphQLView(BaseGraphQLView):
    @staticmethod
    def format_error(error):
        # based on https://github.com/graphql-python/graphene/issues/143#issuecomment-222075241
        data = {
            'message': six.text_type(error),
        }
        if isinstance(error, graphql.error.GraphQLLocatedError):
            data.update(graphql.error.format_error(error))
            if isinstance(error.original_error, Exception):
                error = error.original_error
            else:
                return data

        if isinstance(error, rest_framework.exceptions.APIException):
            if isinstance(error, rest_framework.exceptions.ValidationError):
                data.update({
                    'message': 'Validation error',
                    'code': 'validation_error',
                    'fields': dict_keys_to_camel_case(error.detail)
                })
            else:
                if getattr(error, 'error_code', None):
                    data['code'] = error.error_code

                if getattr(error, 'extra', None):
                    data.update(error.extra)
        elif isinstance(error, django.core.exceptions.PermissionDenied):
            data.update({
                'message': 'Permission denied',
                'code': 'permission_denied'
            })
        elif isinstance(error, django.core.exceptions.ValidationError):
            data['code'] = getattr(error, 'code', 'validation_error')
            data['message'] = 'Validation error',
            if hasattr(error, 'error_dict'):
                data['fields'] = dict_keys_to_camel_case(error.message_dict)
            else:
                data['fields'] = {'nonFieldErrors': error.messages}
        elif isinstance(error, graphql.error.GraphQLError):
            data = graphql.error.format_error(error)
            if error.nodes is not None:
                data['nodes'] = [
                    six.text_type(node) for node in error.nodes
                ]
        elif isinstance(error, graphql_django_view.HttpError):
            pass
        else:
            data['code'] = 'unhandled_exception'
            if not settings.DEBUG:
                data['message'] = 'Server error'
            else:
                data['message'] = '{}: {}'.format(error.__class__.__name__, error)
        return data
