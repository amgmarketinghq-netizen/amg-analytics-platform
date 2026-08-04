"""
AMG Enterprise Analytics & Data Command Center
Invoice Generator Utility: utils/invoice_generator.py (v6.0 — Defensive XSS Sanitization)
===================================================================================
Generates Minimal HTML B2B Invoices with Full Pre-Escaped String Safety.
"""

import html


def _e(v):
    """Internal helper to escape raw string values against XSS Injection."""
    return html.escape(str(v)) if v is not None else ""


def generate_invoice_html(
    inv_id: str,
    client_name: str,
    client_email: str,
    items: list,
    currency: str = "₹",
    tax_pct: float = 0.0,
    disc_pct: float = 0.0,
    payment_terms: str = "Due Upon Receipt",
    payment_methods: list = None,
    bank_details: dict = None,
    paypal_email: str = "",
    upi_details: dict = None,
    agency_name: str = "AMG Marketing Global"
) -> str:
    if payment_methods is None:
        payment_methods = []

    # Defensive Escaping on ALL Inputs up front
    inv_id = _e(inv_id)
    client_name = _e(client_name)
    client_email = _e(client_email)
    currency = _e(currency)
    payment_terms = _e(payment_terms)
    agency_name = _e(agency_name)
    paypal_email = _e(paypal_email)

    if bank_details:
        bank_details = {k: _e(v) for k, v in bank_details.items()}
    if upi_details:
        upi_details = {k: _e(v) for k, v in upi_details.items()}

    escaped_items = []
    subtotal = 0.0
    for item in items:
        desc = _e(item.get("description", ""))
        try:
            amt = float(item.get("amount", 0.0))
        except (ValueError, TypeError):
            amt = 0.0
        subtotal += amt
        escaped_items.append({"description": desc, "amount": amt})

    disc_amount = subtotal * (disc_pct / 100.0)
    taxable_amount = subtotal - disc_amount
    tax_amount = taxable_amount * (tax_pct / 100.0)
    total_amount = taxable_amount + tax_amount

    # Build Item Rows
    items_html = ""
    for item in escaped_items:
        items_html += f"""
        <tr>
            <td style="padding: 12px; border-bottom: 1px solid #334155;">{item['description']}</td>
            <td style="padding: 12px; border-bottom: 1px solid #334155; text-align: right;">{currency}{item['amount']:,.2f}</td>
        </tr>
        """

    # Build Payment Options Block
    pay_html = ""
    if "Bank Transfer" in payment_methods and bank_details:
        pay_html += f"""
        <div style="background: #1E293B; border: 1px solid #334155; padding: 12px 16px; border-radius: 8px; margin-bottom: 10px;">
            <b style="color: #F59E0B;">🏛️ Bank Transfer:</b><br/>
            Bank: {bank_details.get('bank_name', 'N/A')} | Acc Holder: {bank_details.get('account_name', 'N/A')}<br/>
            Acc No: <code>{bank_details.get('account_no', 'N/A')}</code> | IFSC/SWIFT: <code>{bank_details.get('swift_ifsc', 'N/A')}</code>
        </div>
        """
    if "PayPal" in payment_methods and paypal_email:
        pay_html += f"""
        <div style="background: #1E293B; border: 1px solid #334155; padding: 12px 16px; border-radius: 8px; margin-bottom: 10px;">
            <b style="color: #F59E0B;">🌐 PayPal:</b><br/>
            PayPal ID: <code>{paypal_email}</code>
        </div>
        """
    if "UPI" in payment_methods and upi_details:
        pay_html += f"""
        <div style="background: #1E293B; border: 1px solid #334155; padding: 12px 16px; border-radius: 8px; margin-bottom: 10px;">
            <b style="color: #F59E0B;">⚡ UPI Payment:</b><br/>
            UPI ID: <code>{upi_details.get('upi_id', 'N/A')}</code> | Payee: {upi_details.get('payee_name', 'N/A')}
        </div>
        """

    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8"/>
        <title>Invoice {inv_id}</title>
        <style>
            body {{ font-family: 'Segoe UI', Arial, sans-serif; background-color: #0F172A; color: #F8FAFC; margin: 0; padding: 30px; }}
            .invoice-card {{ background: #1E293B; border: 1px solid #334155; border-radius: 12px; padding: 30px; max-width: 800px; margin: 0 auto; box-shadow: 0 10px 25px rgba(0,0,0,0.5); }}
            .header {{ display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #334155; padding-bottom: 20px; margin-bottom: 25px; }}
            h2 {{ color: #38BDF8; margin: 0; font-size: 24px; }}
            table {{ width: 100%; border-collapse: collapse; margin-bottom: 20px; }}
            th {{ background: #0F172A; color: #F59E0B; text-align: left; padding: 12px; font-size: 14px; border-bottom: 2px solid #334155; }}
            .totals-row {{ text-align: right; font-size: 14px; margin-top: 15px; border-top: 1px solid #334155; padding-top: 15px; }}
            .grand-total {{ font-size: 18px; color: #38BDF8; font-weight: bold; margin-top: 8px; }}
        </style>
    </head>
    <body>
        <div class="invoice-card">
            <div class="header">
                <div>
                    <h2>{agency_name}</h2>
                    <span style="color: #94A3B8; font-size: 13px;">Official B2B Invoice</span>
                </div>
                <div style="text-align: right;">
                    <b style="font-size: 18px; color: #F59E0B;">{inv_id}</b><br/>
                    <span style="color: #94A3B8; font-size: 13px;">{payment_terms}</span>
                </div>
            </div>

            <div style="margin-bottom: 25px; background: #0F172A; padding: 15px; border-radius: 8px; border: 1px solid #334155;">
                <span style="color: #94A3B8; font-size: 12px;">BILLED TO:</span><br/>
                <b style="font-size: 16px; color: #FFFFFF;">{client_name}</b><br/>
                <span style="color: #CBD5E1; font-size: 13px;">{client_email}</span>
            </div>

            <table>
                <thead>
                    <tr>
                        <th>Service Description</th>
                        <th style="text-align: right;">Amount</th>
                    </tr>
                </thead>
                <tbody>
                    {items_html}
                </tbody>
            </table>

            <div class="totals-row">
                <div>Subtotal: <b>{currency}{subtotal:,.2f}</b></div>
                {"<div>Discount (" + str(disc_pct) + "%): <b style='color:#EF4444;'>-" + currency + f"{disc_amount:,.2f}</b></div>" if disc_pct > 0 else ""}
                {"<div>Tax (" + str(tax_pct) + "%): <b>" + currency + f"{tax_amount:,.2f}</b></div>" if tax_pct > 0 else ""}
                <div class="grand-total">Total Amount Due: {currency}{total_amount:,.2f}</div>
            </div>

            <div style="margin-top: 30px; border-top: 2px solid #334155; padding-top: 20px;">
                <h4 style="color: #38BDF8; margin-top: 0;">💳 Payment Options:</h4>
                {pay_html}
            </div>
        </div>
    </body>
    </html>
    """
    return html_template
