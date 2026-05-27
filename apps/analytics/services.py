import csv
import io
from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db.models import Count, Sum
from django.http import HttpResponse
from django.utils import timezone

from apps.accounts.models import Merchant
from apps.billing.models import CODRemittance, Invoice
from apps.shipments.models import DELIVERED, FAILED, RTO, Shipment
from apps.tracking.models import TrackingEvent

from .models import DailyAnalytics


VALID_PERIODS = ("daily", "weekly", "monthly", "yearly")


def normalize_period(period):
    period = (period or "").lower()
    if period not in VALID_PERIODS:
        raise ValueError("Unsupported report period.")
    return period


def get_period_range(period):
    period = normalize_period(period)
    now = timezone.localtime()

    if period == "daily":
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == "weekly":
        start = (now - timedelta(days=6)).replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == "monthly":
        start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    else:
        start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)

    return start, now


def get_role_scope(user):
    if user.is_staff or getattr(user, "is_ops", False):
        return "admin"
    if getattr(user, "is_customer", False):
        return "customer"
    return "merchant"


def get_scoped_shipments(user, period):
    start, end = get_period_range(period)
    queryset = Shipment.objects.select_related(
        "sender_address",
        "receiver_address",
        "merchant",
    ).prefetch_related("tracking_events").filter(
        created_at__gte=start,
        created_at__lte=end,
    )

    if get_role_scope(user) == "admin":
        return queryset

    return queryset.filter(merchant=user)


def get_scoped_invoices(user, period):
    start, end = get_period_range(period)
    queryset = Invoice.objects.filter(created_at__gte=start, created_at__lte=end)

    if get_role_scope(user) == "admin":
        return queryset

    return queryset.filter(merchant_id=user.id)


def get_report_context(user, period):
    period = normalize_period(period)
    start, end = get_period_range(period)
    shipments = get_scoped_shipments(user, period)
    invoices = get_scoped_invoices(user, period)
    shipment_ids = shipments.values_list("id", flat=True)
    tracking_events = TrackingEvent.objects.select_related("shipment").filter(
        shipment_id__in=shipment_ids,
        event_time__gte=start,
        event_time__lte=end,
    )
    cod = CODRemittance.objects.filter(
        shipment_awb__in=shipments.values_list("awb", flat=True)
    )

    status_counts = {
        row["status"]: row["count"]
        for row in shipments.values("status").annotate(count=Count("id"))
    }
    total_shipments = shipments.count()
    delivered = status_counts.get(DELIVERED, 0)
    failed = status_counts.get(FAILED, 0)
    rto = status_counts.get(RTO, 0)
    revenue = shipments.aggregate(total=Sum("freight_amount"))["total"] or Decimal("0")
    cod_total = shipments.aggregate(total=Sum("cod_amount"))["total"] or Decimal("0")
    invoice_total = invoices.aggregate(total=Sum("grand_total"))["total"] or Decimal("0")
    success_rate = round((delivered / total_shipments) * 100, 2) if total_shipments else 0

    return {
        "period": period,
        "start": start,
        "end": end,
        "user": user,
        "scope": get_role_scope(user),
        "shipments": shipments.order_by("-created_at"),
        "tracking_events": tracking_events.order_by("-event_time"),
        "invoices": invoices.order_by("-created_at"),
        "cod": cod.order_by("shipment_awb"),
        "status_counts": status_counts,
        "total_shipments": total_shipments,
        "delivered": delivered,
        "failed": failed,
        "rto": rto,
        "revenue": revenue,
        "cod_total": cod_total,
        "invoice_total": invoice_total,
        "success_rate": success_rate,
    }


def build_admin_csv_response(user, period):
    if get_role_scope(user) != "admin":
        return HttpResponse("Forbidden", status=403)

    context = get_report_context(user, period)
    start_date = context["start"].date().isoformat()
    end_date = context["end"].date().isoformat()
    filename = f"trackflow-admin-{context['period']}-report-{end_date}.csv"
    buffer = io.StringIO()
    writer = csv.writer(buffer)

    writer.writerow(["TrackFlow Admin Analytics Report"])
    writer.writerow(["Period", context["period"].title()])
    writer.writerow(["Date Range", start_date, end_date])
    writer.writerow(["Generated At", timezone.localtime().strftime("%Y-%m-%d %H:%M:%S")])
    writer.writerow([])

    writer.writerow(["Summary"])
    writer.writerow(["Total Customers", get_user_model().objects.filter(role=get_user_model().ROLE_CUSTOMER).count()])
    writer.writerow(["Total Merchants", Merchant.objects.count()])
    writer.writerow(["Total Shipments", context["total_shipments"]])
    writer.writerow(["Delivered", context["delivered"]])
    writer.writerow(["Failed", context["failed"]])
    writer.writerow(["RTO", context["rto"]])
    writer.writerow(["Delivery Success Rate", f"{context['success_rate']}%"])
    writer.writerow(["Revenue", context["revenue"]])
    writer.writerow(["COD Amount", context["cod_total"]])
    writer.writerow(["Invoice Total", context["invoice_total"]])
    writer.writerow([])

    writer.writerow(["Customers"])
    writer.writerow(["User ID", "Email", "Username", "Phone", "Active", "Joined"])
    customers = get_user_model().objects.filter(role=get_user_model().ROLE_CUSTOMER).order_by("id")
    for customer in customers.iterator(chunk_size=500):
        writer.writerow([
            customer.id,
            customer.email,
            customer.username,
            customer.phone,
            customer.is_active,
            timezone.localtime(customer.date_joined).strftime("%Y-%m-%d %H:%M:%S"),
        ])
    writer.writerow([])

    writer.writerow(["Merchants"])
    writer.writerow(["Merchant ID", "User ID", "Email", "Company", "GSTIN", "Active", "Credit Limit", "Created"])
    merchants = Merchant.objects.select_related("user").order_by("id")
    for merchant in merchants.iterator(chunk_size=500):
        writer.writerow([
            merchant.id,
            merchant.user_id,
            merchant.user.email,
            merchant.company_name,
            merchant.gstin,
            merchant.active,
            merchant.credit_limit,
            timezone.localtime(merchant.created_at).strftime("%Y-%m-%d %H:%M:%S"),
        ])
    writer.writerow([])

    writer.writerow(["Date-wise Shipment Counts"])
    writer.writerow(["Date", "Shipment Count"])
    for row in context["shipments"].values("created_at__date").annotate(count=Count("id")).order_by("created_at__date"):
        writer.writerow([row["created_at__date"], row["count"]])
    writer.writerow([])

    writer.writerow(["Shipments"])
    writer.writerow([
        "AWB", "Merchant Email", "Sender", "Receiver", "Receiver City", "Status",
        "Service", "Weight KG", "Freight", "COD", "Created At", "Latest Tracking",
    ])
    latest_tracking = {}
    for event in context["tracking_events"].order_by("shipment_id", "-event_time"):
        latest_tracking.setdefault(event.shipment_id, event)
    for shipment in context["shipments"].iterator(chunk_size=500):
        event = latest_tracking.get(shipment.id)
        writer.writerow([
            shipment.awb,
            shipment.merchant.email if shipment.merchant else "",
            shipment.sender_address.name,
            shipment.receiver_address.name,
            shipment.receiver_address.city,
            shipment.status,
            shipment.service_type,
            shipment.weight_kg,
            shipment.freight_amount,
            shipment.cod_amount,
            timezone.localtime(shipment.created_at).strftime("%Y-%m-%d %H:%M:%S"),
            f"{event.status} - {event.location or ''}" if event else "",
        ])
    writer.writerow([])

    writer.writerow(["Billing"])
    writer.writerow(["Invoice Number", "Merchant ID", "Amount", "GST", "Grand Total", "Created At"])
    for invoice in context["invoices"].iterator(chunk_size=500):
        writer.writerow([
            invoice.invoice_number,
            invoice.merchant_id,
            invoice.total_amount,
            invoice.gst_amount,
            invoice.grand_total,
            timezone.localtime(invoice.created_at).strftime("%Y-%m-%d %H:%M:%S"),
        ])
    writer.writerow([])

    writer.writerow(["COD"])
    writer.writerow(["Shipment AWB", "Amount", "Paid"])
    for remittance in context["cod"].iterator(chunk_size=500):
        writer.writerow([remittance.shipment_awb, remittance.amount, remittance.paid])
    writer.writerow([])

    writer.writerow(["Analytics Summaries"])
    writer.writerow(["Merchant", "Date", "Total", "Delivered", "Failed", "RTO", "COD", "Revenue"])
    analytics = DailyAnalytics.objects.select_related("merchant").filter(
        analytics_date__gte=context["start"].date(),
        analytics_date__lte=context["end"].date(),
    )
    for row in analytics.iterator(chunk_size=500):
        writer.writerow([
            row.merchant.company_name,
            row.analytics_date,
            row.total_shipments,
            row.delivered_shipments,
            row.failed_shipments,
            row.rto_shipments,
            row.total_cod,
            row.total_revenue,
        ])

    response = HttpResponse(buffer.getvalue(), content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response


def _pdf_escape(value):
    return str(value).replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def _build_pdf(lines, title):
    pages = []
    line_height = 18
    max_lines = 42
    for index in range(0, len(lines), max_lines):
        pages.append(lines[index:index + max_lines])

    objects = [
        "1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj",
        f"2 0 obj << /Type /Pages /Kids [{' '.join(f'{5 + i * 2} 0 R' for i in range(len(pages)))}] /Count {len(pages)} >> endobj",
        "3 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj",
        "4 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >> endobj",
    ]

    for page_number, page_lines in enumerate(pages, start=1):
        page_obj = 5 + (page_number - 1) * 2
        content_obj = page_obj + 1
        text_ops = ["BT", "/F1 10 Tf", "42 790 Td"]
        text_ops.append(f"({_pdf_escape(title)} - Page {page_number} of {len(pages)}) Tj")
        text_ops.append("0 -26 Td")
        for line in page_lines:
            font = "/F2 13 Tf" if line.get("bold") else "/F1 9 Tf"
            text_ops.append(font)
            text_ops.append(f"({_pdf_escape(line['text'][:118])}) Tj")
            text_ops.append(f"0 -{line_height} Td")
        text_ops.append("ET")
        stream = "\n".join(text_ops)
        objects.append(
            f"{page_obj} 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] "
            f"/Resources << /Font << /F1 3 0 R /F2 4 0 R >> >> /Contents {content_obj} 0 R >> endobj"
        )
        objects.append(
            f"{content_obj} 0 obj << /Length {len(stream.encode('utf-8'))} >> stream\n{stream}\nendstream endobj"
        )

    pdf = "%PDF-1.4\n" + "\n".join(objects) + "\ntrailer << /Root 1 0 R >>\n%%EOF\n"
    return pdf.encode("utf-8")


def build_user_pdf_response(user, period):
    scope = get_role_scope(user)
    if scope == "admin":
        return HttpResponse("Admins must use CSV reports.", status=400)

    context = get_report_context(user, period)
    report_name = "Customer" if scope == "customer" else "Merchant"
    title = f"TrackFlow {report_name} {context['period'].title()} Analytics Report"
    generated_at = timezone.localtime().strftime("%Y-%m-%d %H:%M:%S")
    lines = [
        {"text": title, "bold": True},
        {"text": f"Generated at: {generated_at}"},
        {"text": f"Date range: {context['start'].date()} to {context['end'].date()}"},
        {"text": f"User: {user.email}"},
        {"text": ""},
        {"text": "Analytics Summary", "bold": True},
        {"text": f"Total shipments: {context['total_shipments']}"},
        {"text": f"Delivered: {context['delivered']} | Failed: {context['failed']} | RTO: {context['rto']}"},
        {"text": f"Delivery success rate: {context['success_rate']}%"},
        {"text": f"Revenue: {context['revenue']} | COD: {context['cod_total']} | Billing total: {context['invoice_total']}"},
        {"text": ""},
        {"text": "Delivery Status Chart", "bold": True},
    ]

    for label, count in context["status_counts"].items():
        bar = "#" * min(int(count), 40)
        lines.append({"text": f"{label:<18} {count:>4} {bar}"})

    lines.extend([
        {"text": ""},
        {"text": "Shipment Table", "bold": True},
        {"text": "AWB | Status | Receiver | City | Freight | COD | Created"},
    ])
    for shipment in context["shipments"][:150]:
        lines.append({
            "text": (
                f"{shipment.awb} | {shipment.status} | {shipment.receiver_address.name} | "
                f"{shipment.receiver_address.city} | {shipment.freight_amount} | {shipment.cod_amount} | "
                f"{timezone.localtime(shipment.created_at).strftime('%Y-%m-%d')}"
            )
        })

    lines.extend([
        {"text": ""},
        {"text": "Tracking Summary", "bold": True},
        {"text": "AWB | Status | Location | Event Time"},
    ])
    for event in context["tracking_events"][:120]:
        lines.append({
            "text": (
                f"{event.shipment.awb} | {event.status} | {event.location or '-'} | "
                f"{timezone.localtime(event.event_time).strftime('%Y-%m-%d %H:%M')}"
            )
        })

    lines.extend([
        {"text": ""},
        {"text": "Billing Summary", "bold": True},
        {"text": "Invoice | Amount | GST | Total | Date"},
    ])
    for invoice in context["invoices"][:120]:
        lines.append({
            "text": (
                f"{invoice.invoice_number} | {invoice.total_amount} | {invoice.gst_amount} | "
                f"{invoice.grand_total} | {timezone.localtime(invoice.created_at).strftime('%Y-%m-%d')}"
            )
        })

    filename = f"trackflow-{scope}-{context['period']}-report-{context['end'].date().isoformat()}.pdf"
    response = HttpResponse(_build_pdf(lines, title), content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response
