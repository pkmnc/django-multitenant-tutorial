class TenantRouter:
    def db_for_read(self, model, **hints):
        # GIS 관련 모델만 default DB 사용
        if hasattr(model, '_meta') and hasattr(model._meta, 'required_db_features'):
            if 'gis' in model._meta.required_db_features:
                return 'default'
        return 'tenant_db'

    def db_for_write(self, model, **hints):
        # GIS 관련 모델만 default DB 사용
        if hasattr(model, '_meta') and hasattr(model._meta, 'required_db_features'):
            if 'gis' in model._meta.required_db_features:
                return 'default'
        return 'tenant_db'

    def allow_relation(self, obj1, obj2, **hints):
        # 모든 관계 허용 (cross-database relations 가능)
        return True

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        # GIS 관련 모델만 default DB에 마이그레이션
        if 'gis' in hints.get('required_db_features', []):
            return db == 'default'
        return db == 'tenant_db' 