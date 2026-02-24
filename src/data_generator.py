import random
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import hashlib
import json
from faker import Faker
import sqlite3
import os

fake = Faker()
random.seed(42)  # For reproducible results
np.random.seed(42)

class SupplyChainDataGenerator:
    def __init__(self):
        self.companies = []
        self.lenders = []
        self.relationships = []
        self.purchase_orders = []
        self.grns = []
        self.invoices = []
        self.payments = []
        self.alerts = []
        
        # Industry types for realistic company generation
        self.industries = [
            'Manufacturing', 'Electronics', 'Automotive', 'Textiles', 'Chemicals',
            'Food & Beverage', 'Pharmaceuticals', 'Construction', 'Energy', 'Logistics'
        ]
        
        # Countries for geographic distribution
        self.countries = ['USA', 'China', 'Germany', 'Japan', 'India', 'UK', 'France', 'Italy', 'Brazil', 'Canada']
        
        print("Initializing Supply Chain Data Generator")
    
    def generate_companies(self):
        """Generate companies across all tiers"""
        print("📊 Generating companies...")
        
        # Generate buyers (Tier 0)
        buyers_count = random.randint(10, 15)
        for i in range(buyers_count):
            company = {
                'id': len(self.companies) + 1,
                'name': fake.company(),
                'tier': 0,
                'industry': random.choice(self.industries),
                'annual_revenue': random.uniform(50_000_000, 2_000_000_000),  # $50M to $2B
                'country': random.choice(self.countries),
                'city': fake.city(),
                'registration_date': fake.date_between(start_date='-10y', end_date='-1y'),
                'is_active': True
            }
            self.companies.append(company)
        
        # Generate Tier 1 suppliers
        tier1_count = random.randint(20, 30)
        for i in range(tier1_count):
            company = {
                'id': len(self.companies) + 1,
                'name': fake.company(),
                'tier': 1,
                'industry': random.choice(self.industries),
                'annual_revenue': random.uniform(10_000_000, 500_000_000),  # $10M to $500M
                'country': random.choice(self.countries),
                'city': fake.city(),
                'registration_date': fake.date_between(start_date='-8y', end_date='-1y'),
                'is_active': True
            }
            self.companies.append(company)
        
        # Generate Tier 2 suppliers
        tier2_count = random.randint(40, 60)
        for i in range(tier2_count):
            company = {
                'id': len(self.companies) + 1,
                'name': fake.company(),
                'tier': 2,
                'industry': random.choice(self.industries),
                'annual_revenue': random.uniform(1_000_000, 100_000_000),  # $1M to $100M
                'country': random.choice(self.countries),
                'city': fake.city(),
                'registration_date': fake.date_between(start_date='-6y', end_date='-1y'),
                'is_active': True
            }
            self.companies.append(company)
        
        # Generate Tier 3 suppliers
        tier3_count = random.randint(80, 100)
        for i in range(tier3_count):
            company = {
                'id': len(self.companies) + 1,
                'name': fake.company(),
                'tier': 3,
                'industry': random.choice(self.industries),
                'annual_revenue': random.uniform(100_000, 20_000_000),  # $100K to $20M
                'country': random.choice(self.countries),
                'city': fake.city(),
                'registration_date': fake.date_between(start_date='-5y', end_date='-1y'),
                'is_active': True
            }
            self.companies.append(company)
        
        print(f"Generated {len(self.companies)} companies:")
        print(f"   - {buyers_count} buyers (Tier 0)")
        print(f"   - {tier1_count} Tier 1 suppliers")
        print(f"   - {tier2_count} Tier 2 suppliers") 
        print(f"   - {tier3_count} Tier 3 suppliers")
    
    def generate_lenders(self):
        """Generate financial institutions/lenders"""
        print("🏦 Generating lenders...")
        
        lender_names = [
            'Global Finance Corp', 'Trade Capital Partners', 'Supply Chain Bank',
            'International Trade Finance', 'Commercial Lending Solutions',
            'Asia Pacific Finance', 'European Trade Bank', 'American Supply Finance'
        ]
        
        for i, name in enumerate(lender_names):
            lender = {
                'id': i + 1,
                'name': name,
                'country': random.choice(self.countries),
                'lending_capacity': random.uniform(100_000_000, 5_000_000_000),  # $100M to $5B
                'interest_rate': random.uniform(0.03, 0.12)  # 3% to 12%
            }
            self.lenders.append(lender)
        
        print(f"Generated {len(self.lenders)} lenders")
    
    def generate_relationships(self):
        """Generate buyer-supplier relationships"""
        print("🔗 Generating buyer-supplier relationships...")
        
        buyers = [c for c in self.companies if c['tier'] == 0]
        tier1_suppliers = [c for c in self.companies if c['tier'] == 1]
        tier2_suppliers = [c for c in self.companies if c['tier'] == 2]
        tier3_suppliers = [c for c in self.companies if c['tier'] == 3]
        
        relationship_id = 1
        
        # Buyers -> Tier 1 relationships
        for buyer in buyers:
            # Each buyer works with 3-8 Tier 1 suppliers
            num_suppliers = random.randint(3, 8)
            selected_suppliers = random.sample(tier1_suppliers, min(num_suppliers, len(tier1_suppliers)))
            
            for supplier in selected_suppliers:
                relationship = {
                    'id': relationship_id,
                    'buyer_id': buyer['id'],
                    'supplier_id': supplier['id'],
                    'relationship_type': random.choice(['direct', 'preferred', 'strategic']),
                    'start_date': fake.date_between(start_date='-3y', end_date='-6m'),
                    'credit_limit': random.uniform(1_000_000, 50_000_000),
                    'payment_terms': random.choice([30, 45, 60, 90]),
                    'is_active': random.choice([True] * 9 + [False])  # 90% active
                }
                self.relationships.append(relationship)
                relationship_id += 1
        
        # Tier 1 -> Tier 2 relationships
        for tier1 in tier1_suppliers:
            # Each Tier 1 works with 2-6 Tier 2 suppliers
            num_suppliers = random.randint(2, 6)
            selected_suppliers = random.sample(tier2_suppliers, min(num_suppliers, len(tier2_suppliers)))
            
            for supplier in selected_suppliers:
                relationship = {
                    'id': relationship_id,
                    'buyer_id': tier1['id'],
                    'supplier_id': supplier['id'],
                    'relationship_type': random.choice(['direct', 'indirect', 'preferred']),
                    'start_date': fake.date_between(start_date='-2y', end_date='-3m'),
                    'credit_limit': random.uniform(500_000, 20_000_000),
                    'payment_terms': random.choice([30, 45, 60]),
                    'is_active': random.choice([True] * 8 + [False, False])  # 80% active
                }
                self.relationships.append(relationship)
                relationship_id += 1
        
        # Tier 2 -> Tier 3 relationships
        for tier2 in tier2_suppliers:
            # Each Tier 2 works with 1-4 Tier 3 suppliers
            num_suppliers = random.randint(1, 4)
            selected_suppliers = random.sample(tier3_suppliers, min(num_suppliers, len(tier3_suppliers)))
            
            for supplier in selected_suppliers:
                relationship = {
                    'id': relationship_id,
                    'buyer_id': tier2['id'],
                    'supplier_id': supplier['id'],
                    'relationship_type': random.choice(['direct', 'indirect', 'spot']),
                    'start_date': fake.date_between(start_date='-18m', end_date='-1m'),
                    'credit_limit': random.uniform(100_000, 5_000_000),
                    'payment_terms': random.choice([30, 45, 60]),
                    'is_active': random.choice([True] * 7 + [False, False, False])  # 70% active
                }
                self.relationships.append(relationship)
                relationship_id += 1
        
        print(f"Generated {len(self.relationships)} buyer-supplier relationships")
    
    def generate_purchase_orders(self):
        """Generate legitimate purchase orders"""
        print("Generating purchase orders...")
        
        active_relationships = [r for r in self.relationships if r['is_active']]
        
        # Generate 3-12 months of historical POs
        start_date = datetime.now() - timedelta(days=365)
        end_date = datetime.now() - timedelta(days=30)
        
        po_id = 1
        
        for relationship in active_relationships:
            buyer_id = relationship['buyer_id']
            supplier_id = relationship['supplier_id']
            credit_limit = relationship['credit_limit']
            
            # Generate 2-15 POs per relationship over the period
            num_pos = random.randint(2, 15)
            
            for _ in range(num_pos):
                po_date = fake.date_between(start_date=start_date, end_date=end_date)
                
                # PO amount based on relationship credit limit
                max_amount = min(credit_limit * 0.3, credit_limit / num_pos * 2)
                amount = random.uniform(max_amount * 0.1, max_amount)
                
                purchase_order = {
                    'id': po_id,
                    'po_number': f"PO-{po_date.strftime('%Y%m')}-{po_id:06d}",
                    'buyer_id': buyer_id,
                    'supplier_id': supplier_id,
                    'amount': round(amount, 2),
                    'quantity': random.randint(1, 1000),
                    'description': fake.catch_phrase(),
                    'po_date': po_date,
                    'expected_delivery_date': po_date + timedelta(days=random.randint(15, 90)),
                    'status': random.choice(['confirmed'] * 8 + ['delivered'] * 2)  # 80% confirmed, 20% delivered
                }
                self.purchase_orders.append(purchase_order)
                po_id += 1
        
        print(f"Generated {len(self.purchase_orders)} purchase orders")
    
    def generate_grns(self):
        """Generate Good Receipt Notes for delivered POs"""
        print("Generating Good Receipt Notes...")
        
        delivered_pos = [po for po in self.purchase_orders if po['status'] == 'delivered']
        
        grn_id = 1
        
        for po in delivered_pos:
            # 95% of delivered POs have GRNs
            if random.random() < 0.95:
                received_date = po['expected_delivery_date'] + timedelta(days=random.randint(-5, 10))
                
                grn = {
                    'id': grn_id,
                    'grn_number': f"GRN-{received_date.strftime('%Y%m')}-{grn_id:06d}",
                    'po_id': po['id'],
                    'quantity_received': po['quantity'] + random.randint(-5, 5),  # Minor variance
                    'quality_status': random.choice(['approved'] * 9 + ['partial']),  # 90% approved
                    'received_date': received_date,
                    'received_by': fake.name(),
                    'notes': fake.sentence() if random.random() < 0.3 else None
                }
                self.grns.append(grn)
                grn_id += 1
        
        print(f"Generated {len(self.grns)} Good Receipt Notes")
    
    def generate_invoice_fingerprint(self, amount, date, supplier_id, description):
        """Generate invoice fingerprint for duplicate detection"""
        normalized_amount = f"{amount:.2f}"
        normalized_date = date.strftime('%Y-%m-%d')
        text_to_hash = f"{normalized_amount}_{normalized_date}_{supplier_id}_{description[:50]}"
        return hashlib.md5(text_to_hash.encode()).hexdigest()
    
    def generate_legitimate_invoices(self):
        """Generate legitimate invoices based on POs"""
        print("Generating legitimate invoices...")
        
        invoice_id = 1
        
        for po in self.purchase_orders:
            # 90% of POs get invoiced
            if random.random() < 0.90:
                # Invoice date between PO date and delivery date
                min_date = po['po_date'] + timedelta(days=7)
                max_date = po['expected_delivery_date'] + timedelta(days=30)
                invoice_date = fake.date_between(start_date=min_date, end_date=max_date)
                
                # Amount variance: 95% exact, 5% slight variance (legitimate)
                if random.random() < 0.95:
                    amount = po['amount']
                else:
                    variance = random.uniform(0.95, 1.05)  # ±5% variance
                    amount = po['amount'] * variance
                
                fingerprint = self.generate_invoice_fingerprint(
                    amount, invoice_date, po['supplier_id'], po['description']
                )
                
                invoice = {
                    'id': invoice_id,
                    'invoice_number': f"INV-{invoice_date.strftime('%Y%m')}-{invoice_id:06d}",
                    'po_id': po['id'],
                    'supplier_id': po['supplier_id'],
                    'lender_id': random.choice(self.lenders)['id'],
                    'amount': round(amount, 2),
                    'invoice_date': invoice_date,
                    'due_date': invoice_date + timedelta(days=30),
                    'description': po['description'],
                    'invoice_fingerprint': fingerprint,
                    'status': random.choice(['approved'] * 7 + ['paid'] * 3),
                    'is_fraudulent': False,
                    'fraud_type': None
                }
                self.invoices.append(invoice)
                invoice_id += 1
        
        return invoice_id
    
    def save_data_to_files(self):
        """Save all generated data to CSV files"""
        print("Saving data to CSV files...")
        
        data_dir = 'data'
        
        # Save companies
        df_companies = pd.DataFrame(self.companies)
        df_companies.to_csv(f'{data_dir}/companies.csv', index=False)
        
        # Save lenders
        df_lenders = pd.DataFrame(self.lenders)
        df_lenders.to_csv(f'{data_dir}/lenders.csv', index=False)
        
        # Save relationships
        df_relationships = pd.DataFrame(self.relationships)
        df_relationships.to_csv(f'{data_dir}/relationships.csv', index=False)
        
        # Save purchase orders
        df_pos = pd.DataFrame(self.purchase_orders)
        df_pos.to_csv(f'{data_dir}/purchase_orders.csv', index=False)
        
        # Save GRNs
        df_grns = pd.DataFrame(self.grns)
        df_grns.to_csv(f'{data_dir}/grns.csv', index=False)
        
        # Save invoices
        df_invoices = pd.DataFrame(self.invoices)
        df_invoices.to_csv(f'{data_dir}/invoices.csv', index=False)
        
        # Save payments
        df_payments = pd.DataFrame(self.payments)
        df_payments.to_csv(f'{data_dir}/payments.csv', index=False)
        
        # Save alerts
        df_alerts = pd.DataFrame(self.alerts)
        df_alerts.to_csv(f'{data_dir}/alerts.csv', index=False)
        
        print("Data saved to CSV files")
    
    def generate_dataset(self):
        """Main method to generate complete dataset"""
        print("🎯 Starting synthetic data generation...")
        
        self.generate_companies()
        self.generate_lenders()
        self.generate_relationships()
        self.generate_purchase_orders()
        self.generate_grns()
        
        # Generate legitimate invoices first
        next_invoice_id = self.generate_legitimate_invoices()
        
        print(f"Generated {len(self.invoices)} legitimate invoices")
        
        return next_invoice_id

if __name__ == "__main__":
    generator = SupplyChainDataGenerator()
    next_id = generator.generate_dataset()
    
    print(f"\n📊 Dataset Summary:")
    print(f"   - Companies: {len(generator.companies)}")
    print(f"   - Lenders: {len(generator.lenders)}")
    print(f"   - Relationships: {len(generator.relationships)}")
    print(f"   - Purchase Orders: {len(generator.purchase_orders)}")
    print(f"   - GRNs: {len(generator.grns)}")
    print(f"   - Legitimate Invoices: {len(generator.invoices)}")
    
    # Save to files
    generator.save_data_to_files()
    
    print(f"\n🎉 Phase 1.1 Complete - Ready for fraud injection (next_invoice_id: {next_id})")