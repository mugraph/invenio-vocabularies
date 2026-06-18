# -*- coding: utf-8 -*-
#
# Copyright (C) 2021-2025 CERN.
# Copyright (C) 2021 Northwestern University.
# Copyright (C) 2024 University of Münster.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Subjects configuration."""

from flask import current_app
from invenio_i18n import get_locale
from invenio_i18n import lazy_gettext as _
from invenio_records_resources.services import SearchOptions
from invenio_records_resources.services.records.components import DataComponent
from invenio_records_resources.services.records.queryparser import (
    NamedSuggestQueryParser
)
from werkzeug.local import LocalProxy

from ...services.components import PIDComponent

from invenio_search.api import PrefixedSearchMixin, BaseRecordsSearchV2, PrefixedIndexList

subject_schemes = LocalProxy(
    lambda: current_app.config["VOCABULARIES_SUBJECTS_SCHEMES"]
)
localized_title = LocalProxy(lambda: f"title.{get_locale()}^20")


gemet_file_url = LocalProxy(
    lambda: current_app.config["VOCABULARIES_SUBJECTS_GEMET_FILE_URL"]
)

euroscivoc_file_url = LocalProxy(
    lambda: current_app.config["VOCABULARIES_SUBJECTS_EUROSCIVOC_FILE_URL"]
)

nvs_file_url = LocalProxy(
    lambda: current_app.config["VOCABULARIES_SUBJECTS_NVS_FILE_URL"]
)

class RecordsSearchV3(PrefixedSearchMixin, BaseRecordsSearchV2):
    """Prefixed record search class.

    Enhanced version of RecordsSearch class to be able to inject configuration
    via kwargs, instead of using a Meta class.

    The class adds the `synonyms` field to the highlight fields.
    """

    def __init__(self, **kwargs):
        """Constructor."""
        _index = self.prefix_index(index=kwargs.get("index", "*"))
        kwargs.update({"index": _index})

        fields = (
            kwargs.setdefault("extra", {})
                  .setdefault("highlight", {})
                  .setdefault("fields", {})
        )

        fields.setdefault("synonyms", {})

        super(RecordsSearchV3, self).__init__(**kwargs)
        if self._index:
            self._index = PrefixedIndexList(self._index)


class SubjectsSearchOptions(SearchOptions):
    """Search options."""

    search_cls = RecordsSearchV3
    suggest_parser_cls = NamedSuggestQueryParser.factory(
        filter_field="scheme",
        named_fields = {
            "subject": ["subject^100"],
            "scheme": ["scheme^20"],
            "synonyms": ["synonyms^20"],
            "localized": [localized_title],
        }
    )

    sort_default = "bestmatch"

    sort_default_no_query = "subject"

    sort_options = {
        "bestmatch": dict(
            title=_("Best match"),
            fields=["_score"],  # ES defaults to desc on `_score` field
        ),
        "subject": dict(
            title=_("Name"),
            fields=["subject_sort"],
        ),
        "newest": dict(
            title=_("Newest"),
            fields=["-created"],
        ),
        "oldest": dict(
            title=_("Oldest"),
            fields=["created"],
        ),
    }


service_components = [
    # Order of components are important!
    DataComponent,
    PIDComponent,
]
