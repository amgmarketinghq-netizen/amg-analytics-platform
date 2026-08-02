"""
AMG Enterprise Analytics & Data Command Center
Utility: utils/invoice_generator.py
===================================================================================
Enterprise HTML Invoice Generator Engine with Multi-Currency, Flexible Payment Methods
(PayPal, Bank Transfer, UPI), and Payment Terms.
"""

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
    """Generates clean enterprise HTML invoice with optional payment method blocks."""

    if payment_methods is None:
        payment_methods = []

    subtotal = sum(item.get("amount", 0.0) for item in items)
    discount_val = (subtotal * disc_pct) / 100.0
    taxable_amt = subtotal - discount_val
    tax_val = (taxable_amt * tax_pct) / 100.0
    total_due = taxable_amt + tax_val

    # Generate Line Items Table Rows
    item_rows_html = ""
    for idx, item in enumerate(items, 1):
        desc = item.get("description", "Analytics & Data Service")
        amt = item.get("amount", 0.0)
        item_rows_html += f"""
        <tr>
            <td style="padding: 12px; border-bottom: 1px solid #e2e8f0; text-align: center;">{idx}</td>
            <td style="padding: 12px; border-bottom: 1px solid #e2e8f0;"><strong>{desc}</strong></td>
            <td style="padding: 12px; border-bottom: 1px solid #e2e8f0; text-align: right;">{currency}{amt:,.2f}</td>
        </tr>
        """

    # Generate Payment Instructions Block
    payment_block_html = ""
    if payment_methods:
        payment_block_html += '<div style="margin-top: 30px; padding: 20px; background-color: #f8fafc; border-radius: 8px; border: 1px solid #e2e8f0;">'
        payment_block_html += '<h3 style="margin-top:0; color: #0f172a; font-size: 16px; border-bottom: 1px solid #cbd5e1; padding-bottom: 8px;">💳 Payment Instructions</h3>'

        if "PayPal" in payment_methods and paypal_email:
            payment_block_html += f"""
            <div style="margin-bottom: 12px;">
                <strong style="color: #0284c7;">🌐 PayPal (International):</strong><br>
                <span>Send payment to: <code>{paypal_email}</code></span>
            </div>
            """

        if "Bank Transfer" in payment_methods and bank_details:
            payment_block_html += f"""
            <div style="margin-bottom: 12px;">
                <strong style="color: #0284c7;">🏛️ Direct Bank Transfer:</strong><br>
                <span><strong>Bank Name:</strong> {bank_details.get('bank_name', 'N/A')}</span><br>
                <span><strong>Account Name:</strong> {bank_details.get('account_name', 'N/A')}</span><br>
                <span><strong>Account No / IBAN:</strong> {bank_details.get('account_no', 'N/A')}</span><br>
                <span><strong>IFSC / SWIFT Code:</strong> {bank_details.get('swift_ifsc', 'N/A')}</span>
            </div>
            """

        if "UPI" in payment_methods and upi_details:
            payment_block_html += f"""
            <div style="margin-bottom: 12px;">
                <strong style="color: #0284c7;">⚡ UPI Payment (India):</strong><br>
                <span><strong>UPI ID:</strong> <code>{upi_details.get('upi_id', 'N/A')}</code></span><br>
                <span><strong>Payee Name:</strong> {upi_details.get('payee_name', agency_name)}</span>
            </div>
            """

        payment_block_html += '</div>'

    html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Invoice {inv_id} - {agency_name}</title>
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; color: #1e293b; background: #ffffff; padding: 30px; margin: 0; }}
        .invoice-box {{ max-width: 800px; margin: auto; padding: 30px; border: 1px solid #e2e8f0; border-radius: 10px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); }}
        .header-table {{ width: 100%; margin-bottom: 30px; }}
        .brand-title {{ font-size: 24px; font-weight: bold; color: #0284c7; margin: 0; }}
        .inv-heading {{ font-size: 28px; font-weight: bold; color: #0f172a; text-align: right; margin: 0; }}
        .meta-table {{ width: 100%; margin-bottom: 30px; background: #f8fafc; padding: 15px; border-radius: 8px; }}
        .items-table {{ width: 100%; border-collapse: collapse; margin-bottom: 25px; }}
        .items-table th {{ background: #0f172a; color: #ffffff; padding: 12px; text-align: left; font-size: 13px; }}
        .summary-table {{ width: 40%; float: right; margin-bottom: 30px; }}
        .total-row {{ font-size: 18px; font-weight: bold; color: #0284c7; border-top: 2px solid #0284c7; }}
        .clear {{ clear: both; }}
        .footer {{ text-align: center; margin-top: 40px; font-size: 12px; color: #94a3b8; border-top: 1px solid #e2e8f0; padding-top: 15px; }}
    </style>
</head>
<body>
    <div class="invoice-box">
        <table class="header-table">
            <tr>
                <td>
                    <p class="brand-title">⚡ {agency_name}</p>
                    <p style="margin: 4px 0 0 0; color: #64748b; font-size: 13px;">Enterprise Data Infrastructure & Analytics</p>
                </td>
                <td>
                    <p class="inv-heading">INVOICE</p>
                    <p style="text-align: right; margin: 4px 0 0 0; color: #64748b; font-size: 13px;"><strong>#{inv_id}</strong></p>
                </td>
            </tr>
        </table>

        <table class="meta-table">
            <tr>
                <td style="width: 50%; vertical-align: top;">
                    <strong style="color: #64748b; font-size: 12px; text-transform: uppercase;">Billed To:</strong><br>
                    <span style="font-size: 16px; font-weight: bold; color: #0f172a;">{client_name or 'Valued Enterprise Client'}</span><br>
                    <span style="color: #475569;">{client_email or 'client@company.com'}</span>
                </td>
                <td style="width: 50%; vertical-align: top; text-align: right;">
                    <strong style="color: #64748b; font-size: 12px; text-transform: uppercase;">Payment Terms:</strong><br>
                    <span style="font-size: 14px; font-weight: bold; color: #0f172a;">{payment_terms}</span>
                </td>
            </tr>
        </table>

        <table class="items-table">
            <thead>
                <tr>
                    <th style="width: 10%; text-align: center;">#</th>
                    <th style="width: 65%;">Service Description</th>
                    <th style="width: 25%; text-align: right;">Amount</th>
                </tr>
            </thead>
            <tbody>
                {item_rows_html}
            </tbody>
        </table>

        <table class="summary-table">
            <tr>
                <td style="padding: 6px 0; color: #64748b;">Subtotal:</td>
                <td style="padding: 6px 0; text-align: right; font-weight: bold;">{currency}{subtotal:,.2f}</td>
            </tr>
            {"<tr><td style='padding:6px 0; color:#ef4444;'>Discount (" + str(disc_pct) + "%):</td><td style='padding:6px 0; text-align:right; color:#ef4444;'>-" + currency + f"{discount_val:,.2f}</td></tr>" if disc_pct > 0 else ""}
            {"<tr><td style='padding:6px 0; color:#64748b;'>Tax (" + str(tax_pct) + "%):</td><td style='padding:6px 0; text-align:right;'>" + currency + f"{tax_val:,.2f}</td></tr>" if tax_pct > 0 else ""}
            <tr class="total-row">
                <td style="padding: 10px 0;">Total Due:</td>
                <td style="padding: 10px 0; text-align: right;">{currency}{total_due:,.2f}</td>
            </tr>
        </table>

        <div class="clear"></div>

        {payment_block_html}

        <div class="footer">
            Thank you for choosing <strong>{agency_name}</strong>. For billing support, contact billing@amgmarketing.global
        </div>
    </div>
</body>
</html>"""
    return html_template
