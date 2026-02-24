"""
Supply Chain Fraud Detection - Phase 1 Data Generation
Complete synthetic dataset generation with embedded fraud patterns
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_generator import SupplyChainDataGenerator
from fraud_injector import FraudInjector

def main():
    print("=" * 60)
    print("🏭 SUPPLY CHAIN FRAUD DETECTION - PHASE 1")
    print("=" * 60)
    print("📋 Task: Generate synthetic multi-tier supply chain data")
    print("💀 Task: Inject realistic fraud patterns")
    print("=" * 60)
    
    # Step 1: Generate base dataset
    print("\n🚀 Step 1: Generating base dataset...")
    generator = SupplyChainDataGenerator()
    generator.generate_dataset()
    
    # Step 2: Inject fraud patterns
    print("\n💀 Step 2: Injecting fraud patterns...")
    fraud_injector = FraudInjector(generator)
    total_fraud = fraud_injector.inject_all_fraud_patterns()
    
    # Step 3: Save complete dataset
    print("\n💾 Step 3: Saving complete dataset...")
    generator.save_data_to_files()
    
    # Generate final statistics
    legitimate_invoices = len([inv for inv in generator.invoices if not inv['is_fraudulent']])
    fraudulent_invoices = len([inv for inv in generator.invoices if inv['is_fraudulent']])
    fraud_rate = (fraudulent_invoices / len(generator.invoices)) * 100
    
    print("\n" + "=" * 60)
    print("📊 FINAL DATASET STATISTICS")
    print("=" * 60)
    print(f"🏢 Companies: {len(generator.companies)}")
    print(f"   - Buyers (Tier 0): {len([c for c in generator.companies if c['tier'] == 0])}")
    print(f"   - Tier 1 Suppliers: {len([c for c in generator.companies if c['tier'] == 1])}")
    print(f"   - Tier 2 Suppliers: {len([c for c in generator.companies if c['tier'] == 2])}")
    print(f"   - Tier 3 Suppliers: {len([c for c in generator.companies if c['tier'] == 3])}")
    print(f"🏦 Lenders: {len(generator.lenders)}")
    print(f"🔗 Relationships: {len(generator.relationships)}")
    print(f"📋 Purchase Orders: {len(generator.purchase_orders)}")
    print(f"📦 Good Receipt Notes: {len(generator.grns)}")
    print(f"🧾 Total Invoices: {len(generator.invoices)}")
    print(f"   - Legitimate: {legitimate_invoices}")
    print(f"   - Fraudulent: {fraudulent_invoices} ({fraud_rate:.1f}%)")
    print(f"💸 Payments: {len(generator.payments)}")
    print(f"🚨 Alerts: {len(generator.alerts)}")
    
    print("\n" + "=" * 60)
    print("🎭 FRAUD PATTERN BREAKDOWN")
    print("=" * 60)
    fraud_types = {}
    for invoice in generator.invoices:
        if invoice['is_fraudulent']:
            fraud_type = invoice['fraud_type']
            fraud_types[fraud_type] = fraud_types.get(fraud_type, 0) + 1
    
    for fraud_type, count in fraud_types.items():
        print(f"👻 {fraud_type.replace('_', ' ').title()}: {count}")
    
    print("\n" + "=" * 60)
    print("🎯 DETECTION CHALLENGES EMBEDDED")
    print("=" * 60)
    print("✅ Phantom invoices without corresponding PO/GRN")
    print("✅ Cross-lender duplicate invoices with variations")
    print("✅ Over-invoiced amounts exceeding PO values")
    print("✅ Circular carousel trade patterns")
    print("✅ Dilution fraud with poor collection rates")
    print("✅ Network topology gaps and anomalies")
    print("✅ Velocity and sequencing anomalies")
    print("✅ Revenue vs. invoice volume mismatches")
    
    print("\n" + "=" * 60)
    print("📁 FILES GENERATED")
    print("=" * 60)
    print("📄 data/companies.csv")
    print("📄 data/lenders.csv")
    print("📄 data/relationships.csv")
    print("📄 data/purchase_orders.csv")
    print("📄 data/grns.csv")
    print("📄 data/invoices.csv")
    print("📄 data/payments.csv")
    print("📄 data/alerts.csv")
    
    print("\n🎉 PHASE 1 COMPLETE!")
    print("✅ Synthetic multi-tier supply chain dataset generated")
    print("✅ Realistic fraud patterns injected")
    print("✅ Ready for Phase 2: Core Detection Engine Development")
    print("=" * 60)

if __name__ == "__main__":
    main()