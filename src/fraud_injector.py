import random
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import hashlib
from faker import Faker

fake = Faker()
random.seed(42)

class FraudInjector:
    def __init__(self, generator):
        self.generator = generator
        self.companies = generator.companies
        self.lenders = generator.lenders
        self.relationships = generator.relationships
        self.purchase_orders = generator.purchase_orders
        self.invoices = generator.invoices
        self.next_invoice_id = len(self.invoices) + 1
        
        print("💀 Initializing Fraud Injection Module")
    
    def inject_phantom_invoices(self, count_range=(50, 100)):
        """Inject phantom invoices (no corresponding PO/GRN)"""
        print(f"👻 Injecting phantom invoices...")
        
        suppliers = [c for c in self.companies if c['tier'] > 0]
        phantom_count = random.randint(*count_range)
        
        for _ in range(phantom_count):
            supplier = random.choice(suppliers)
            lender = random.choice(self.lenders)
            
            # Phantom invoices often have suspicious characteristics
            invoice_date = fake.date_between(start_date='-6m', end_date='-1m')
            
            # Amount often doesn't align with supplier capacity
            if supplier['annual_revenue'] > 0:
                # Sometimes way too high for supplier capacity
                if random.random() < 0.3:  # 30% are obviously too large
                    amount = supplier['annual_revenue'] * random.uniform(0.5, 2.0)  # 50-200% of annual revenue
                else:
                    amount = random.uniform(50_000, supplier['annual_revenue'] * 0.1)
            else:
                amount = random.uniform(10_000, 1_000_000)
            
            description = fake.catch_phrase() + " [PHANTOM]"
            fingerprint = self.generator.generate_invoice_fingerprint(
                amount, invoice_date, supplier['id'], description
            )
            
            phantom_invoice = {
                'id': self.next_invoice_id,
                'invoice_number': f"PHANTOM-{invoice_date.strftime('%Y%m')}-{self.next_invoice_id:06d}",
                'po_id': None,  # Key indicator - no corresponding PO
                'supplier_id': supplier['id'],
                'lender_id': lender['id'],
                'amount': round(amount, 2),
                'invoice_date': invoice_date,
                'due_date': invoice_date + timedelta(days=30),
                'description': description,
                'invoice_fingerprint': fingerprint,
                'status': random.choice(['pending'] * 6 + ['approved'] * 4),  # Some slip through
                'is_fraudulent': True,
                'fraud_type': 'phantom'
            }
            
            self.invoices.append(phantom_invoice)
            self.next_invoice_id += 1
        
        print(f"✅ Injected {phantom_count} phantom invoices")
        return phantom_count
    
    def inject_duplicate_invoices(self, count_range=(30, 50)):
        """Inject duplicate invoices across different lenders"""
        print(f"👥 Injecting duplicate invoices...")
        
        legitimate_invoices = [inv for inv in self.invoices if not inv['is_fraudulent']]
        duplicate_count = min(random.randint(*count_range), len(legitimate_invoices))
        
        selected_originals = random.sample(legitimate_invoices, duplicate_count)
        
        for original in selected_originals:
            # Create duplicate with different lender
            available_lenders = [l for l in self.lenders if l['id'] != original['lender_id']]
            duplicate_lender = random.choice(available_lenders)
            
            # Date might be slightly different
            date_variance = random.randint(-7, 7)
            new_date = original['invoice_date'] + timedelta(days=date_variance)
            
            # Amount might have small variance to avoid exact detection
            amount_variance = random.uniform(0.98, 1.02)  # ±2% variance
            new_amount = original['amount'] * amount_variance
            
            # Description might be slightly modified
            description_variants = [
                original['description'],
                original['description'] + " [COPY]",
                original['description'].replace(' ', '_'),
                "DUPLICATE: " + original['description']
            ]
            new_description = random.choice(description_variants)
            
            # Generate fingerprint - some might match, some might not due to variance
            fingerprint = self.generator.generate_invoice_fingerprint(
                new_amount, new_date, original['supplier_id'], new_description
            )
            
            duplicate_invoice = {
                'id': self.next_invoice_id,
                'invoice_number': f"DUP-{new_date.strftime('%Y%m')}-{self.next_invoice_id:06d}",
                'po_id': original['po_id'],  # Same PO - red flag
                'supplier_id': original['supplier_id'],
                'lender_id': duplicate_lender['id'],  # Different lender
                'amount': round(new_amount, 2),
                'invoice_date': new_date,
                'due_date': new_date + timedelta(days=30),
                'description': new_description,
                'invoice_fingerprint': fingerprint,
                'status': random.choice(['pending'] * 7 + ['approved'] * 3),
                'is_fraudulent': True,
                'fraud_type': 'duplicate'
            }
            
            self.invoices.append(duplicate_invoice)
            self.next_invoice_id += 1
        
        print(f"✅ Injected {duplicate_count} duplicate invoices")
        return duplicate_count
    
    def inject_over_invoices(self, count_range=(20, 30)):
        """Inject over-invoiced amounts (>120% of PO value)"""
        print(f"📈 Injecting over-invoices...")
        
        legitimate_invoices = [inv for inv in self.invoices if not inv['is_fraudulent'] and inv['po_id']]
        over_invoice_count = min(random.randint(*count_range), len(legitimate_invoices))
        
        selected_invoices = random.sample(legitimate_invoices, over_invoice_count)
        
        for original in selected_invoices:
            # Find the corresponding PO
            po = next((po for po in self.purchase_orders if po['id'] == original['po_id']), None)
            if not po:
                continue
            
            # Create over-invoice (125% to 300% of original PO amount)
            inflation_factor = random.uniform(1.25, 3.0)
            new_amount = po['amount'] * inflation_factor
            
            # Date slightly after original
            new_date = original['invoice_date'] + timedelta(days=random.randint(1, 15))
            
            description = f"REVISED: {original['description']} [OVER-INVOICED]"
            fingerprint = self.generator.generate_invoice_fingerprint(
                new_amount, new_date, original['supplier_id'], description
            )
            
            over_invoice = {
                'id': self.next_invoice_id,
                'invoice_number': f"OVR-{new_date.strftime('%Y%m')}-{self.next_invoice_id:06d}",
                'po_id': original['po_id'],  # Same PO but inflated amount
                'supplier_id': original['supplier_id'],
                'lender_id': random.choice(self.lenders)['id'],
                'amount': round(new_amount, 2),
                'invoice_date': new_date,
                'due_date': new_date + timedelta(days=30),
                'description': description,
                'invoice_fingerprint': fingerprint,
                'status': random.choice(['pending'] * 8 + ['approved'] * 2),
                'is_fraudulent': True,
                'fraud_type': 'over_invoice'
            }
            
            self.invoices.append(over_invoice)
            self.next_invoice_id += 1
        
        print(f"✅ Injected {over_invoice_count} over-invoices")
        return over_invoice_count
    
    def inject_carousel_trades(self, pattern_count_range=(15, 20)):
        """Inject carousel trade patterns"""
        print(f"🎠 Injecting carousel trade patterns...")
        
        pattern_count = random.randint(*pattern_count_range)
        carousel_invoices = 0
        
        for pattern_id in range(pattern_count):
            # Create circular trade pattern with 3-5 companies
            circle_size = random.randint(3, 5)
            
            # Select companies from same tier to create circular flow
            tier = random.randint(1, 3)
            tier_companies = [c for c in self.companies if c['tier'] == tier]
            
            if len(tier_companies) < circle_size:
                continue
                
            circle_companies = random.sample(tier_companies, circle_size)
            
            # Create circular transaction flow
            circle_amount = random.uniform(100_000, 2_000_000)
            base_date = fake.date_between(start_date='-4m', end_date='-1m')
            
            for i in range(circle_size):
                from_company = circle_companies[i]
                to_company = circle_companies[(i + 1) % circle_size]
                
                # Each transaction in the circle
                transaction_date = base_date + timedelta(days=i * random.randint(1, 7))
                
                description = f"CAROUSEL-P{pattern_id+1}: {from_company['name']} -> {to_company['name']}"
                fingerprint = self.generator.generate_invoice_fingerprint(
                    circle_amount, transaction_date, from_company['id'], description
                )
                
                carousel_invoice = {
                    'id': self.next_invoice_id,
                    'invoice_number': f"CAR-{transaction_date.strftime('%Y%m')}-{self.next_invoice_id:06d}",
                    'po_id': None,  # Usually no legitimate PO
                    'supplier_id': from_company['id'],
                    'lender_id': random.choice(self.lenders)['id'],
                    'amount': round(circle_amount * random.uniform(0.95, 1.05), 2),  # Slight variance
                    'invoice_date': transaction_date,
                    'due_date': transaction_date + timedelta(days=30),
                    'description': description,
                    'invoice_fingerprint': fingerprint,
                    'status': random.choice(['pending'] * 6 + ['approved'] * 4),
                    'is_fraudulent': True,
                    'fraud_type': 'carousel'
                }
                
                self.invoices.append(carousel_invoice)
                self.next_invoice_id += 1
                carousel_invoices += 1
        
        print(f"✅ Injected {carousel_invoices} carousel trade invoices in {pattern_count} patterns")
        return carousel_invoices
    
    def inject_dilution_fraud(self, count_range=(25, 40)):
        """Inject dilution fraud cases (invoices with poor collection)"""
        print(f"💧 Injecting dilution fraud cases...")
        
        # Select legitimate invoices to turn into dilution fraud
        legitimate_invoices = [inv for inv in self.invoices if not inv['is_fraudulent']]
        dilution_count = min(random.randint(*count_range), len(legitimate_invoices))
        
        selected_invoices = random.sample(legitimate_invoices, dilution_count)
        
        for invoice in selected_invoices:
            # Mark as dilution fraud
            invoice['is_fraudulent'] = True
            invoice['fraud_type'] = 'dilution'
            
            # Create poor payment collection pattern
            payment_date = invoice['due_date'] + timedelta(days=random.randint(30, 180))
            collection_rate = random.uniform(0.0, 0.6)  # Poor collection: 0-60%
            payment_amount = invoice['amount'] * collection_rate
            
            if payment_amount > 0:
                payment = {
                    'id': len(self.generator.payments) + 1,
                    'payment_number': f"PAY-{payment_date.strftime('%Y%m')}-{len(self.generator.payments) + 1:06d}",
                    'invoice_id': invoice['id'],
                    'amount': round(payment_amount, 2),
                    'payment_date': payment_date,
                    'payment_method': random.choice(['wire', 'check', 'ach']),
                    'collection_rate': round(collection_rate, 4),
                    'days_overdue': (payment_date - invoice['due_date']).days
                }
                self.generator.payments.append(payment)
        
        print(f"✅ Injected {dilution_count} dilution fraud cases")
        return dilution_count
    
    def generate_fraud_alerts(self):
        """Generate alerts for detected fraud patterns"""
        print(f"🚨 Generating fraud detection alerts...")
        
        alert_id = 1
        
        for invoice in self.invoices:
            if invoice['is_fraudulent']:
                # Not all fraud generates immediate alerts (some slip through)
                if random.random() < 0.75:  # 75% of fraud generates alerts
                    
                    severity_mapping = {
                        'phantom': random.choice(['high'] * 6 + ['critical'] * 4),
                        'duplicate': random.choice(['medium'] * 5 + ['high'] * 5),
                        'over_invoice': random.choice(['medium'] * 7 + ['high'] * 3),
                        'carousel': random.choice(['high'] * 7 + ['critical'] * 3),
                        'dilution': random.choice(['low'] * 3 + ['medium'] * 7)
                    }
                    
                    fraud_scores = {
                        'phantom': random.uniform(0.7, 0.95),
                        'duplicate': random.uniform(0.6, 0.9),
                        'over_invoice': random.uniform(0.5, 0.8),
                        'carousel': random.uniform(0.7, 0.9),
                        'dilution': random.uniform(0.4, 0.7)
                    }
                    
                    alert = {
                        'id': alert_id,
                        'alert_type': invoice['fraud_type'],
                        'severity': severity_mapping[invoice['fraud_type']],
                        'entity_type': 'invoice',
                        'entity_id': invoice['id'],
                        'description': f"{invoice['fraud_type'].replace('_', ' ').title()} detected for invoice {invoice['invoice_number']}",
                        'fraud_score': round(fraud_scores[invoice['fraud_type']], 4),
                        'investigation_status': random.choice(['open'] * 6 + ['investigating'] * 3 + ['confirmed'] * 1),
                        'created_at': invoice['invoice_date'] + timedelta(days=random.randint(0, 7))
                    }
                    self.generator.alerts.append(alert)
                    alert_id += 1
        
        # Generate some false positive alerts
        legitimate_invoices = [inv for inv in self.invoices if not inv['is_fraudulent']]
        false_positives = random.sample(legitimate_invoices, min(20, len(legitimate_invoices)))
        
        for invoice in false_positives:
            alert = {
                'id': alert_id,
                'alert_type': random.choice(['phantom', 'duplicate', 'velocity']),
                'severity': random.choice(['low'] * 7 + ['medium'] * 3),
                'entity_type': 'invoice',
                'entity_id': invoice['id'],
                'description': f"Potential fraud detected for invoice {invoice['invoice_number']} (False Positive)",
                'fraud_score': round(random.uniform(0.3, 0.6), 4),
                'investigation_status': 'false_positive',
                'created_at': invoice['invoice_date'] + timedelta(days=random.randint(0, 7))
            }
            self.generator.alerts.append(alert)
            alert_id += 1
        
        print(f"✅ Generated {len(self.generator.alerts)} fraud alerts")
    
    def inject_all_fraud_patterns(self):
        """Main method to inject all types of fraud"""
        print("🎯 Starting fraud injection process...")
        
        phantom_count = self.inject_phantom_invoices()
        duplicate_count = self.inject_duplicate_invoices()
        over_invoice_count = self.inject_over_invoices()
        carousel_count = self.inject_carousel_trades()
        dilution_count = self.inject_dilution_fraud()
        
        self.generate_fraud_alerts()
        
        total_fraud = phantom_count + duplicate_count + over_invoice_count + carousel_count + dilution_count
        
        print(f"\n📊 Fraud Injection Summary:")
        print(f"   - Phantom invoices: {phantom_count}")
        print(f"   - Duplicate invoices: {duplicate_count}")
        print(f"   - Over-invoices: {over_invoice_count}")
        print(f"   - Carousel trades: {carousel_count}")
        print(f"   - Dilution fraud: {dilution_count}")
        print(f"   - Total fraudulent transactions: {total_fraud}")
        print(f"   - Total alerts generated: {len(self.generator.alerts)}")
        
        return total_fraud

if __name__ == "__main__":
    # This would be run after the main data generator
    print("❗ This module should be run after data_generator.py")
    print("   Use: python fraud_injector.py")