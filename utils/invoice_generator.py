"""
AMG Enterprise Analytics & Data Command Center
Module: utils/invoice_generator.py
===================================================================================
HTML Invoice & Audit Report Generator Engine.
Generates printable, executive-ready HTML invoices with 100% exact numerical math.
"""

import datetime


def generate_invoice_html(
    invoice_id: str,
    client_name: str,
    client_email: str,
    items: list,
    currency: str = "₹",
    tax_rate: float = 0.0,
    discount: float = 0.0
) -> str:
    """
    Calculates subtotal, tax, discount, and final amount with 100% mathematical precision.
    Returns printable HTML string for PDF export or web rendering.
    
    items format: [{'description': 'Data Cleaning 10k rows', 'amount': 1500.0}]
    """
    subtotal = sum(float(item.get('amount', 0.0)) for item in items)
    tax_amount = (subtotal * tax_rate) / 100.0
    discount_amount = (subtotal * discount) / 100.0
    final_total = max(0.0, subtotal + tax_amount - discount_amount)

    today_str = datetime.date.today().strftime("%d %b, %Y")
    due_str = (datetime.date.today() + datetime.timedelta(days=7)).strftime("%d %b, %Y")

    items_rows_html = ""
    for idx, item in enumerate(items, 1):
        desc = item.get('description', 'Data Processing Service')
        amt = float(item.get('amount', 0.0))
        items_rows_html += f"""
        <tr>
            <td style="padding: 12px; border-bottom: 1px solid #e2e8f0; text-align: center; color: #64748b;">{idx}</td>
            <td style="padding: 12px; border-bottom: 1px solid #e2e8f0; font-weight: 500; color: #1e293b;">{desc}</td>
            <td style="padding: 12px; border-bottom: 1px solid #e2e8f0; text-align: right; font-weight: 600; color: #0f172a;">{currency}{amt:,.2f}</td>
        </tr>
        """

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Invoice {invoice_id} - AMG Marketing Global</title>
        <style>
            body {{ font-family: 'Inter', system-ui, -apple-system, sans-serif; background-color: #f8fafc; margin: 0; padding: 20px; color: #334155; }}
            .invoice-card {{ max-width: 800px; margin: 0 auto; background: #ffffff; border-radius: 12px; border: 1px solid #e2e8f0; padding: 40px; box-shadow: 0 10px 25px -5px rgba(0,0,0,0.05); }}
            .header {{ display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #0f172a; padding-bottom: 20px; margin-bottom: 30px; }}
            .brand-title {{ font-size: 24px; font-weight: 800; color: #0f172a; letter-spacing: -0.5px; }}
            .brand-subtitle {{ font-size: 12px; color: #64748b; text-transform: uppercase; letter-spacing: 1px; margin-top: 4px; }}
            .invoice-badge {{ background: #eff6ff; color: #2563eb; font-weight: 700; padding: 6px 16px; border-radius: 20px; font-size: 14px; border: 1px solid #bfdbfe; }}
            .details-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 30px; }}
            .meta-box {{ background: #f8fafc; padding: 16px; border-radius: 8px; border: 1px solid #f1f5f9; }}
            .meta-label {{ font-size: 11px; text-transform: uppercase; color: #94a3b8; font-weight: 700; margin-bottom: 4px; }}
            .meta-val {{ font-size: 14px; font-weight: 600; color: #1e293b; }}
            table {{ width: 100%; border-collapse: collapse; margin-bottom: 30px; }}
            th {{ background: #f1f5f9; padding: 12px; text-align: left; font-size: 12px; font-weight: 700; color: #475569; text-transform: uppercase; }}
            .totals-table {{ width: 300px; margin-left: auto; border: none; }}
            .totals-table td {{ padding: 8px 12px; text-align: right; }}
            .grand-total {{ font-size: 18px; font-weight: 800; color: #2563eb; border-top: 2px solid #2563eb; padding-top: 12px !important; }}
            .footer {{ text-align: center; margin-top: 40px; font-size: 12px; color: #94a3b8; border-top: 1px solid #f1f5f9; padding-top: 20px; }}
        </style>
    </head>
    <body>
        <div class="invoice-card">
            <div class="header">
                <div>
                    <div class="brand-title">AMG MARKETING GLOBAL</div>
                    <div class="brand-subtitle">Enterprise Data Infrastructure & Analytics</div>
                </div>
                <div class="invoice-badge">INVOICE #{invoice_id}</div>
            </div>

            <div class="details-grid">
                <div class="meta-box">
                    <div class="meta-label">Billed To</div>
                    <div class="meta-val">{client_name}</div>
                    <div style="font-size: 13px; color: #64748b; margin-top: 2px;">{client_email}</div>
                </div>
                <div class="meta-box">
                    <div class="meta-label">Invoice Details</div>
                    <div class="meta-val">Issue Date: {today_str}</div>
                    <div style="font-size: 13px; color: #ef4444; margin-top: 2px; font-weight: 600;">Due Date: {due_str}</div>
                </div>
            </div>

            <table>
                <thead>
                    <tr>
                        <th style="width: 50px; text-align: center;">#</th>
                        <th>Description / Service Breakdown</th>
                        <th style="text-align: right; width: 150px;">Amount</th>
                    </tr>
                </thead>
                <tbody>
                    {items_rows_html}
                </tbody>
            </table>

            <table class="totals-table">
                <tr>
                    <td style="color: #64748b;">Subtotal:</td>
                    <td style="font-weight: 600; color: #1e293b;">{currency}{subtotal:,.2f}</td>
                </tr>
                {"<tr><td style='color: #64748b;'>Tax (" + str(tax_rate) + "%):</td><td style='font-weight: 600; color: #1e293b;'>" + currency + f"{tax_amount:,.2f}" + "</td></tr>" if tax_rate > 0 else ""}
                {"<tr><td style='color: #16a34a;'>Discount (" + str(discount) + "%):</td><td style='font-weight: 600; color: #16a34a;'>-" + currency + f"{discount_amount:,.2f}" + "</td></tr>" if discount > 0 else ""}
                <tr>
                    <td class="grand-total">Total Due:</td>
                    <td class="grand-total">{currency}{final_total:,.2f}</td>
                </tr>
            </table>

            <div class="footer">
                Thank you for your business! For payment queries, contact <strong>billing@amgmarketing.com</strong><br>
                This is a system-generated official invoice powered by AMG Data Command Center.
            </div>
        </div>
    </body>
    </html>
    """
    return html_content
