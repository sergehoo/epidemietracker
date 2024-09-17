from rolepermissions.roles import AbstractUserRole


class NationalRole(AbstractUserRole):
    available_permissions = {
        'view_all_data': True,
    }


class RegionalRole(AbstractUserRole):
    available_permissions = {
        'view_regional_data': True,
    }


class DistrictRole(AbstractUserRole):
    available_permissions = {
        'view_district_data': True,
    }
