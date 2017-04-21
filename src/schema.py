# -*- coding: utf-8 -*-
import graphene
from graphene.relay import Node
import timelapse_manager.schema

from graphene_django.debug import DjangoDebug


class Query(
    timelapse_manager.schema.Query,
    graphene.ObjectType,
):
    debug = graphene.Field(DjangoDebug, name='__debug')
    node = Node.Field()


schema = graphene.Schema(
    query=Query,
    types=[
        timelapse_manager.schema.UserNode,
        timelapse_manager.schema.DayNode,
        timelapse_manager.schema.ImageNode,
        timelapse_manager.schema.CameraNode,
    ]
)
