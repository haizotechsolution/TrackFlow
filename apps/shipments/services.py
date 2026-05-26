import csv
import io
from decimal import Decimal
from pathlib import Path

from django.conf import settings
from django.core.files.base import ContentFile
from django.db import transaction
from django.utils.text import slugify

from .models import Address, Shipment


VOLUMETRIC_DIVISOR = Decimal('5000')
BASE_FREIGHT = Decimal('60.00')
PER_KG_RATE = Decimal('35.00')
EXPRESS_SURCHARGE = Decimal('75.00')
SAME_DAY_SURCHARGE = Decimal('150.00')
COD_PERCENTAGE = Decimal('0.02')
MIN_COD_FEE = Decimal('25.00')


def decimal_or_zero(value):
    if value in (None, ''):
        return Decimal('0')
    return Decimal(str(value))


def calculate_volumetric_weight(length_cm, width_cm, height_cm):
    volume = (
        decimal_or_zero(length_cm)
        * decimal_or_zero(width_cm)
        * decimal_or_zero(height_cm)
    )
    if volume <= 0:
        return Decimal('0')
    return (volume / VOLUMETRIC_DIVISOR).quantize(Decimal('0.01'))


def calculate_chargeable_weight(weight_kg, length_cm=0, width_cm=0, height_cm=0):
    actual_weight = decimal_or_zero(weight_kg)
    volumetric_weight = calculate_volumetric_weight(length_cm, width_cm, height_cm)
    return max(actual_weight, volumetric_weight)


def calculate_cod_fee(cod_amount):
    amount = decimal_or_zero(cod_amount)
    if amount <= 0:
        return Decimal('0.00')
    return max(MIN_COD_FEE, amount * COD_PERCENTAGE).quantize(Decimal('0.01'))


def calculate_freight_amount(
    weight_kg,
    length_cm=0,
    width_cm=0,
    height_cm=0,
    service_type=Shipment.SERVICE_STANDARD,
    cod_amount=0,
):
    chargeable_weight = calculate_chargeable_weight(
        weight_kg,
        length_cm,
        width_cm,
        height_cm,
    )
    freight = BASE_FREIGHT + (chargeable_weight * PER_KG_RATE)
    if service_type == Shipment.SERVICE_EXPRESS:
        freight += EXPRESS_SURCHARGE
    elif service_type == Shipment.SERVICE_SAME_DAY:
        freight += SAME_DAY_SURCHARGE
    freight += calculate_cod_fee(cod_amount)
    return freight.quantize(Decimal('0.01'))


def generate_awb(merchant_id=None):
    prefix = 'TF'
    merchant_part = f'{merchant_id or 0:04d}'[-4:]
    next_id = (Shipment.objects.order_by('-id').values_list('id', flat=True).first() or 0) + 1
    sequence = f'{next_id:06d}'
    base = f'{prefix}{merchant_part}{sequence}'
    return f'{base}{luhn_checksum(base)}'


def luhn_checksum(value):
    digits = [ord(char) % 10 for char in value]
    total = 0
    parity = len(digits) % 2
    for index, digit in enumerate(digits):
        if index % 2 == parity:
            digit *= 2
            if digit > 9:
                digit -= 9
        total += digit
    return str((10 - (total % 10)) % 10).zfill(2)


def _pdf_escape(value):
    return str(value).replace('\\', '\\\\').replace('(', '\\(').replace(')', '\\)')


def generate_label_pdf(shipment_id):
    shipment = Shipment.objects.select_related('sender_address', 'receiver_address', 'merchant').get(id=shipment_id)
    lines = [
        'TrackFlow Shipping Label',
        f'AWB: {shipment.awb}',
        f'Service: {shipment.service_type}',
        f'Weight: {shipment.weight_kg} kg',
        f'COD: {shipment.cod_amount}',
        '',
        f'From: {shipment.sender_address.name}',
        f'{shipment.sender_address.address_line_1}, {shipment.sender_address.city}',
        f'{shipment.sender_address.state} - {shipment.sender_address.pincode}',
        '',
        f'To: {shipment.receiver_address.name}',
        f'{shipment.receiver_address.address_line_1}, {shipment.receiver_address.city}',
        f'{shipment.receiver_address.state} - {shipment.receiver_address.pincode}',
    ]
    text_ops = ['BT', '/F1 14 Tf', '50 780 Td']
    for index, line in enumerate(lines):
        if index:
            text_ops.append('0 -22 Td')
        text_ops.append(f'({_pdf_escape(line)}) Tj')
    text_ops.append('ET')
    stream = '\n'.join(text_ops)
    objects = [
        '1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj',
        '2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj',
        '3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >> endobj',
        '4 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj',
        f'5 0 obj << /Length {len(stream.encode("utf-8"))} >> stream\n{stream}\nendstream endobj',
    ]
    pdf = '%PDF-1.4\n' + '\n'.join(objects) + '\ntrailer << /Root 1 0 R >>\n%%EOF\n'
    return io.BytesIO(pdf.encode('utf-8'))


def save_label_pdf(shipment_id):
    shipment = Shipment.objects.get(id=shipment_id)
    pdf = generate_label_pdf(shipment_id)
    filename = f'{slugify(shipment.awb)}.pdf'
    shipment.label_file.save(filename, ContentFile(pdf.getvalue()), save=True)
    return shipment.label_file.name


def get_pod_upload_url(awb):
    file_key = f'pod/{awb}.jpg'
    if settings.TRACKFLOW_STORAGE_BACKEND == 's3':
        return {
            'upload_url': f's3://{settings.AWS_STORAGE_BUCKET_NAME}/{file_key}',
            'file_key': file_key,
        }
    media_path = Path(settings.MEDIA_ROOT) / file_key
    media_path.parent.mkdir(parents=True, exist_ok=True)
    return {
        'upload_url': f'{settings.MEDIA_URL}{file_key}',
        'file_key': file_key,
    }


@transaction.atomic
def bulk_create_shipments_from_csv(file_obj, merchant):
    decoded = file_obj.read().decode('utf-8-sig')
    rows = csv.DictReader(io.StringIO(decoded))
    created = []
    errors = []

    for row_number, row in enumerate(rows, start=2):
        try:
            sender = Address.objects.create(
                name=row.get('sender_name') or 'Sender',
                phone=row.get('sender_phone') or '',
                address_line_1=row.get('sender_address') or '',
                city=row.get('sender_city') or '',
                state=row.get('sender_state') or '',
                pincode=row.get('sender_pincode') or '',
            )
            receiver = Address.objects.create(
                name=row.get('receiver_name') or 'Receiver',
                phone=row.get('receiver_phone') or '',
                address_line_1=row.get('receiver_address') or '',
                city=row.get('receiver_city') or '',
                state=row.get('receiver_state') or '',
                pincode=row.get('receiver_pincode') or '',
            )
            weight_kg = Decimal(row.get('weight_kg') or '0.5')
            length_cm = Decimal(row.get('length_cm') or '0')
            width_cm = Decimal(row.get('width_cm') or '0')
            height_cm = Decimal(row.get('height_cm') or '0')
            service_type = row.get('service_type') or Shipment.SERVICE_STANDARD
            cod_amount = Decimal(row.get('cod_amount') or '0')
            shipment = Shipment.objects.create(
                merchant=merchant,
                sender_address=sender,
                receiver_address=receiver,
                weight_kg=weight_kg,
                length_cm=length_cm,
                width_cm=width_cm,
                height_cm=height_cm,
                service_type=service_type,
                cod_amount=cod_amount,
                freight_amount=calculate_freight_amount(
                    weight_kg,
                    length_cm,
                    width_cm,
                    height_cm,
                    service_type,
                    cod_amount,
                ),
            )
            created.append(shipment.awb)
        except Exception as exc:
            errors.append({'row': row_number, 'error': str(exc)})

    return {'created_count': len(created), 'created_awbs': created, 'errors': errors}
