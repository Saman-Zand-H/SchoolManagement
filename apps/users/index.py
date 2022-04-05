from algoliasearch_django import AlgoliaIndex
from algoliasearch_django.decorators import register

from .models import CustomUser


@register(CustomUser)
class ChatPageIndex(AlgoliaIndex):
    tags = "school_name"
    fields = (
        "username",
        "name",
        "get_user_type_display",
    )
    settings = {
        "searchableAttributes": [
            "first_name",
            "last_name",
            "username",
            "name",
            "get_user_type_display",
        ],
        "hitsPerPage": 10,
        
    }
    custom_objectID = "username" 
    should_index = "is_not_principal"
    
