from django import template
import re

register = template.Library()

def _digits(value: str) -> str:
    if value is None:
        return ""
    return re.sub(r"[^0-9]", "", str(value))

@register.filter(name="cpf_format")
def cpf_format(value):
    """Formata CPF para 000.000.000-00.
    Se não tiver 11 dígitos, retorna o valor original.
    """
    d = _digits(value)
    if len(d) != 11:
        return value or ""
    return f"{d[0:3]}.{d[3:6]}.{d[6:9]}-{d[9:11]}"

@register.filter(name="cpf_mask")
def cpf_mask(value):
    """Retorna CPF mascarado como ***.***.***-** se houver 11 dígitos, senão fallback genérico."""
    d = _digits(value)
    if len(d) == 11:
        return "***.***.***-**"
    # Fallback simples: mascara tudo mantendo tamanho
    return "*" * len(d) if d else ""

@register.filter(name="cnpj_format")
def cnpj_format(value):
    """Formata CNPJ para 00.000.000/0000-00.
    Se não tiver 14 dígitos, retorna o valor original.
    """
    d = _digits(value)
    if len(d) != 14:
        return value or ""
    return f"{d[0:2]}.{d[2:5]}.{d[5:8]}/{d[8:12]}-{d[12:14]}"

@register.filter(name="cnpj_mask")
def cnpj_mask(value):
    """Retorna CNPJ mascarado como **.***.***/****-** se houver 14 dígitos, senão fallback genérico."""
    d = _digits(value)
    if len(d) == 14:
        return "**.***.***/****-**"
    return "*" * len(d) if d else ""
