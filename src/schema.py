# -*- coding: utf-8 -*-
import graphene
import graphene.relay

import timelapse_manager.schema


class Query(
    timelapse_manager.schema.Query,
):
    # This class will inherit from multiple Queries
    # as we begin to add more apps to our project
    node = graphene.relay.NodeField()


schema = graphene.Schema(
    name='Schema',
    query=Query,
)
