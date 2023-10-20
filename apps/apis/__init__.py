# -*- coding: utf-8 -*-


from apps.apis import apis, api_scheduler, api_index

apis = [
    {
        "blueprint": api_index.index, "url_prefix": '/'
    },
    {
        "blueprint": apis.apis, "url_prefix": '/'
    },
    {
        "blueprint": api_scheduler.api_scheduler, "url_prefix": '/api/scheduler'
    },
]
