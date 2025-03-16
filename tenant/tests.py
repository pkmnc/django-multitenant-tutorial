from decimal import Decimal
from django.test import TestCase
from django_multitenant.utils import set_current_tenant, unset_current_tenant
from .models import Company, Product

class MultiTenantTest(TestCase):
    databases = {'default', 'tenant_db'}

    def setUp(self):
        # 각 테스트 시작 전에 현재 테넌트 초기화
        unset_current_tenant()

    def test_basic_crud(self):
        """기본적인 CRUD 작업 테스트"""
        # 테스트용 회사 생성
        company = Company.objects.create(name='테스트회사')
        set_current_tenant(company)
        
        # Create
        new_product = Product.objects.create(
            name='새제품',
            price=Decimal('15000.00'),
            company=company
        )
        self.assertEqual(Product.objects.filter(company=company).count(), 1)

        # Read
        product = Product.objects.get(id=new_product.id)
        self.assertEqual(product.name, '새제품')
        self.assertEqual(product.price, Decimal('15000.00'))

        # Update
        product.price = Decimal('25000.00')
        product.save()
        updated_product = Product.objects.get(id=product.id)
        self.assertEqual(updated_product.price, Decimal('25000.00'))

        # Delete
        product.delete()
        self.assertEqual(Product.objects.filter(company=company).count(), 0)

    def test_tenant_isolation(self):
        """멀티테넌트 데이터 분리 테스트"""
        # 테스트용 회사 생성
        company1 = Company.objects.create(name='테스트회사1')
        company2 = Company.objects.create(name='테스트회사2')

        # 회사1의 제품 생성
        set_current_tenant(company1)
        Product.objects.create(
            name='제품1',
            price=Decimal('10000.00'),
            company=company1
        )
        Product.objects.create(
            name='제품2',
            price=Decimal('20000.00'),
            company=company1
        )

        # 회사2의 제품 생성
        set_current_tenant(company2)
        Product.objects.create(
            name='제품3',
            price=Decimal('30000.00'),
            company=company2
        )

        # 회사1의 컨텍스트에서 조회
        set_current_tenant(company1)
        company1_products = Product.objects.all()
        self.assertEqual(company1_products.count(), 2)
        self.assertTrue(all(p.company_id == company1.id for p in company1_products))

        # 회사2의 컨텍스트에서 조회
        set_current_tenant(company2)
        company2_products = Product.objects.all()
        self.assertEqual(company2_products.count(), 1)
        self.assertTrue(all(p.company_id == company2.id for p in company2_products))

    def test_cross_tenant_access(self):
        """테넌트 간 데이터 접근 제한 테스트"""
        # 테스트용 회사 생성
        company1 = Company.objects.create(name='테스트회사1')
        company2 = Company.objects.create(name='테스트회사2')

        # 회사1의 제품 생성
        set_current_tenant(company1)
        product1 = Product.objects.create(
            name='제품1',
            price=Decimal('10000.00'),
            company=company1
        )

        # 회사2의 제품 생성
        set_current_tenant(company2)
        product2 = Product.objects.create(
            name='제품2',
            price=Decimal('20000.00'),
            company=company2
        )

        # 회사1의 컨텍스트에서 회사2의 제품에 접근 시도
        set_current_tenant(company1)
        company1_products = Product.objects.all()
        self.assertNotIn(product2, company1_products)

        # 회사2의 컨텍스트에서 회사1의 제품에 접근 시도
        set_current_tenant(company2)
        company2_products = Product.objects.all()
        self.assertNotIn(product1, company2_products)

    def test_tenant_required(self):
        """현재 테넌트 설정 없이 쿼리 시도 시 예외 발생 테스트"""
        # 테스트용 회사 생성
        company = Company.objects.create(name='테스트회사')
        
        # 현재 테넌트를 설정하지 않고 쿼리 시도
        unset_current_tenant()
        with self.assertRaises(Exception):
            list(Product.objects.all())  # 실제 쿼리 실행을 위해 list() 사용

    def tearDown(self):
        # 각 테스트 종료 후 현재 테넌트 초기화
        unset_current_tenant()