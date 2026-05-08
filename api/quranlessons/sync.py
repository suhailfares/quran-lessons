"""Helpers for delta-sync list endpoints and tombstone destroy semantics."""
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from rest_framework.exceptions import ValidationError


def parse_updated_since(request):
    """Return a timezone-aware datetime for ?updated_since= or None."""
    raw = request.query_params.get("updated_since")
    if raw is None:
        return None

    parsed = parse_datetime(raw)
    if parsed is None:
        raise ValidationError(
            {"updated_since": "Must be ISO-8601 (e.g. 2026-05-02T12:00:00Z)."}
        )
    if timezone.is_naive(parsed):
        parsed = timezone.make_aware(parsed, timezone.utc)
    return parsed


def apply_sync_filter(queryset, request):
    """Apply updated_since + tombstone visibility rules to a queryset.

    Without ?updated_since=: hide soft-deleted rows.
    With ?updated_since=:    include soft-deleted rows so the client can prune.
    """
    since = parse_updated_since(request)
    if since is None:
        return queryset.filter(is_deleted=False)
    return queryset.filter(updated_at__gt=since)


class SoftDeleteDestroyMixin:
    """Replace destroy() with a tombstone update."""

    def perform_destroy(self, instance):
        if getattr(instance, "is_deleted", False):
            return
        instance.is_deleted = True
        instance.save(update_fields=["is_deleted", "updated_at"])
