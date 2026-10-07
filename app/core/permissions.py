import enum


class Permission(enum.StrEnum):
    VIEW_OPERATIONS = "view_operations"
    MANAGE_ASSETS = "manage_assets"
    MANAGE_ALERTS = "manage_alerts"
    MANAGE_WORK_ORDERS = "manage_work_orders"
    ASSIGN_WORK_ORDERS = "assign_work_orders"
    VERIFY_WORK_ORDERS = "verify_work_orders"
    MANAGE_SCHEDULE = "manage_schedule"
    RUN_MODELS = "run_models"
    MANAGE_MODELS = "manage_models"
    EXPORT_REPORTS = "export_reports"
    MANAGE_TENANT = "manage_tenant"
    MANAGE_USERS = "manage_users"


ROLE_PERMISSIONS: dict[str, frozenset[Permission]] = {
    "viewer": frozenset({Permission.VIEW_OPERATIONS, Permission.EXPORT_REPORTS}),
    "technician": frozenset(
        {
            Permission.VIEW_OPERATIONS,
            Permission.MANAGE_ALERTS,
            Permission.MANAGE_WORK_ORDERS,
            Permission.EXPORT_REPORTS,
        }
    ),
    "planner": frozenset(
        {
            Permission.VIEW_OPERATIONS,
            Permission.MANAGE_ALERTS,
            Permission.MANAGE_WORK_ORDERS,
            Permission.MANAGE_SCHEDULE,
            Permission.ASSIGN_WORK_ORDERS,
            Permission.VERIFY_WORK_ORDERS,
            Permission.RUN_MODELS,
            Permission.EXPORT_REPORTS,
        }
    ),
    "admin": frozenset(Permission),
}


def has_permission(role: str, permission: Permission) -> bool:
    return permission in ROLE_PERMISSIONS.get(role, frozenset())
